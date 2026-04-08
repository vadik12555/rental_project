from rest_framework import viewsets, permissions
from django.shortcuts import render
from .models import Item, Order
from .serializers import ItemSerializer, OrderSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # Фильтры убрали, так как библиотека не установилась

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

def item_list(request):
    items = Item.objects.all()
    return render(request, 'catalog/index.html', {'items': items})