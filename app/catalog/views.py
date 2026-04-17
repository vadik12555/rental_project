from django.shortcuts import render
from rest_framework.views import APIView     
from rest_framework.response import Response  
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticated
from .models import Item, Order
from .serializers import ItemSerializer, OrderSerializer
from .cart import Cart
from django.db import transaction
from rest_framework.exceptions import ValidationError

# --- ТВОЙ ОРИГИНАЛЬНЫЙ СПИСОК ТОВАРОВ С ПОИСКОМ ---
def item_list(request):
    items = Item.objects.all()
    query = request.GET.get('q')
    if query:
        items = Item.objects.filter(name__icontains=query)
    else:
        items = Item.objects.all()
    #вернем
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
            
            # 2. Проверяем товары и списываем остатки
            # (ВАЖНО: у тебя в модели Order должна быть связь с товарами через items)
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