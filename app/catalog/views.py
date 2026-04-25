from django.shortcuts import render  ,redirect
from rest_framework.views import APIView     
from rest_framework.response import Response  
from rest_framework import viewsets, permissions, generics , status
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from .models import Item, Order
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
        # Оборачиваем в транзакцию: или всё сработает, или ничего
        with transaction.atomic():
            # 1. Сначала сохраняем заказ
            order = serializer.save(user=self.request.user)
            
            for order_item in order.items.all():
                product = order_item.item
                if product.stock < order_item.quantity:
                    # Если товара мало, отменяем ВЕСЬ заказ (rollback)
                    raise ValidationError(
                        f"Недостаточно товара {product.name}. В наличии: {product.stock}"
                    )
                
                # 3. Вычитаем из базы
                product.stock -= order_item.quantity
                product.save()
                
def create(self, request, *args, **kwargs):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Item.objects.get(id=item_id)
            if product.stock >= quantity:
                product.stock -= quantity
                product.save()

                # Сначала создаем заказ через DRF
                response = super().create(request, *args, **kwargs)
                
                # Получаем ID созданного заказа
                order_id = self.get_serializer(response.data).instance.id
                
                # ЗАПУСКАЕМ ЗАДАЧУ ЗДЕСЬ
                from .tasks import send_order_confirmation
                send_order_confirmation.delay(order_id)

                
                return response
            else:
                messages.error(request, f"Ошибка: на складе всего {product.stock} шт.")
        except Item.DoesNotExist:
            messages.error(request, "Товар не найден.")
            
        return redirect('shop')



class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart(request)
        return Response({
            "items": cart.cart,
            "total_price": cart.get_total_price()
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