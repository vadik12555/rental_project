from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticated
from .models import Item, Order
from .serializers import ItemSerializer, OrderSerializer


def item_list(request):
    items = Item.objects.all()
    query = request.GET.get('q')
    if query:
        items = Item.objects.filter(name__icontains=query)
    else:
        items = Item.objects.all()
    return render(request, 'catalog/index.html', {'items': items})



class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer



# --- API ДЛЯ ЗАКАЗОВ (С ЗАЩИТОЙ) 
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Чтобы каждый видел только свои заказы
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # ГЛАВНАЯ ДОБАВКА: привязываем заказ к юзеру из токена
        serializer.save(user=self.request.user)