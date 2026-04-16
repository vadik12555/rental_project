from django.shortcuts import render
from rest_framework.views import APIView     
from rest_framework.response import Response  
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticated
from .models import Item, Order
from .serializers import ItemSerializer, OrderSerializer
from .cart import Cart

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


# --- API ДЛЯ ЗАКАЗОВ (С ЗАЩИТОЙ) ---
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # ИСПРАВЛЕНО: используем напрямую импортированный IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Чтобы каждый видел только свои заказы
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # ГЛАВНАЯ ДОБАВКА: привязываем заказ к юзеру из токена
        serializer.save(user=self.request.user)


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