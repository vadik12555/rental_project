from rest_framework import serializers
from .models import Item  , Order

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'  # Выводим все поля: id, title, price и т.д.

        
class OrderSerializer(serializers.ModelSerializer):
    # Это вытянет данные товаров прямо внутрь заказа
    items = ItemSerializer(many=True, read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'created_at', 'status', 'total_price']