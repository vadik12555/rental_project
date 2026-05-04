from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView     
from rest_framework.response import Response  
from rest_framework import viewsets, permissions, generics , status
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from .models import Item, Order, OrderItem
from .serializers import ItemSerializer, OrderSerializer
from .cart import Cart
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .tasks import send_order_confirmation

def item_list(request):
    # Пытаемся вытянуть список из кэша
    items = cache.get('catalog_items')
    
    if not items:
        # Если в кэше пусто — идем в базу
        items = Item.objects.all()
        # Сохраняем в Redis на 15 минут
        cache.set('catalog_items', items, 60 * 15)
        print("--- Данные взяты из Postgres ---")
    else:
        print("Данные прилетели из Redis")
        
    return render(request, 'catalog/index.html', {'items': items})

def cart_detail(request):
    cart = Cart(request)
    return render(
        request,
        "catalog/cart.html",
        {"cart_items": list(cart.iter_items()), "cart_total": cart.get_total_price()},
    )


def cart_add(request, item_id: int):
    if request.method != "POST":
        return redirect("shop")

    cart = Cart(request)
    item = get_object_or_404(Item, pk=item_id)
    cart.add(item=item, quantity=1)
    messages.success(request, f"Товар «{item.title}» добавлен в корзину.")
    return redirect("shop")


def cart_update(request, item_id: int):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = Cart(request)
    item = get_object_or_404(Item, pk=item_id)
    qty = request.POST.get("quantity", "1")
    try:
        qty_int = int(qty)
    except ValueError:
        qty_int = 1

    if qty_int < 1:
        cart.remove(item)
    else:
        cart.add(item=item, quantity=qty_int, override=True)
    return redirect("cart_detail")


def cart_remove(request, item_id: int):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = Cart(request)
    item = get_object_or_404(Item, pk=item_id)
    cart.remove(item)
    return redirect("cart_detail")


@login_required
def cart_checkout(request):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = Cart(request)
    cart_rows = list(cart.iter_items())
    if not cart_rows:
        messages.info(request, "Корзина пуста — добавь товары перед оформлением заказа.")
        return redirect("cart_detail")

    with transaction.atomic():
        # Lock all items used in cart to make stock checks safe.
        item_ids = [row["item"].id for row in cart_rows]
        locked_items = {
            i.id: i for i in Item.objects.select_for_update().filter(id__in=item_ids)
        }

        # Validate stock for each row.
        for row in cart_rows:
            locked_item = locked_items.get(row["item"].id)
            if not locked_item:
                raise ValidationError("Товар из корзины не найден.")
            if locked_item.stock < row["quantity"]:
                raise ValidationError(
                    f"Недостаточно товара {locked_item.title}. В наличии: {locked_item.stock}"
                )

        order = Order.objects.create(user=request.user)
        total_price = 0

        for row in cart_rows:
            locked_item = locked_items[row["item"].id]
            qty = row["quantity"]
            OrderItem.objects.create(order=order, item=locked_item, quantity=qty)
            total_price += locked_item.price * qty

        Order.objects.filter(pk=order.pk).update(total_price=total_price)

        # Clear cart only after successful DB operations.
        cart.clear()

    messages.success(request, "Заказ успешно оформлен.")
    return redirect("my_orders")


# --- API ДЛЯ ТОВАРОВ ---
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # Здесь права доступа не ограничены, чтобы все видели товары


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        items_input = serializer.validated_data.get('items_input') or []
        if not items_input:
            raise ValidationError("items_input обязателен и не должен быть пустым.")

        with transaction.atomic():
            order = Order.objects.create(user=self.request.user)

            total_price = 0
            for row in items_input:
                item_id = row['item_id']
                quantity = row['quantity']

                try:
                    item = Item.objects.select_for_update().get(id=item_id)
                except Item.DoesNotExist:
                    raise ValidationError(f"Товар с id={item_id} не найден.")

                if item.stock < quantity:
                    raise ValidationError(
                        f"Недостаточно товара {item.title}. В наличии: {item.stock}"
                    )

                OrderItem.objects.create(order=order, item=item, quantity=quantity)
                total_price += item.price * quantity

            Order.objects.filter(pk=order.pk).update(total_price=total_price)

            transaction.on_commit(lambda: send_order_confirmation.delay(order.id))

            serializer.instance = order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart(request)
        return Response({
            "items": cart.cart,
            "total_price": str(cart.get_total_price()),
        })

    def post(self, request):
        cart = Cart(request)
        item_id = request.data.get('item_id')
        item = Item.objects.get(id=item_id)
        cart.add(item=item)
        return Response({"message": "Товар добавлен в корзину"})

@login_required
def my_orders(request):
# Эта функция берет все заказы текущего юзера и отдает их в шаблон
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'catalog/orders.html', {'orders': orders})