from rest_framework import serializers
from .models import Item, Order, OrderItem

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'  # Выводим все поля: id, title, price и т.д.

        
class OrderItemReadSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']


class OrderItemWriteSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(source='order_items', many=True, read_only=True)
    items_input = OrderItemWriteSerializer(many=True, write_only=True, required=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'items_input', 'created_at', 'status', 'total_price']