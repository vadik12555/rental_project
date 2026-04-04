from rest_framework import viewsets , filters
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']