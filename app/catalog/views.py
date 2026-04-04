from rest_framework import viewsets , filters
from .models import Item , Order
from .serializers import ItemSerializer  , OrderSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer