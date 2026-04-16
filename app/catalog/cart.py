from django.conf import settings
from django.core.cache import cache
from .models import Item

class Cart:
    def __init__(self, request):
        # Привязываем корзину к ID пользователя
        self.user_id = request.user.id
        self.key = f"cart_{self.user_id}"
        # Вытаскиваем данные из Redis (или берем пустой словарь)
        self.cart = cache.get(self.key, {})

    def add(self, item, quantity=1):
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(item.price)}
        
        self.cart[item_id]['quantity'] += quantity
        self.save()

    def remove(self, item):
        item_id = str(item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def save(self):
        # Сохраняем обновленные данные в редис на 24 часа
        cache.set(self.key, self.cart, timeout=86400)

    def clear(self):
        cache.delete(self.key)

    def get_total_price(self):
        return sum(float(v['price']) * v['quantity'] for v in self.cart.values())