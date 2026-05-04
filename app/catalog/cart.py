from decimal import Decimal

from .models import Item


class Cart:
    """
    Session-based cart.

    Stored in request.session as:
      {
        "<item_id>": {"quantity": 2},
        ...
      }
    """

    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(self.SESSION_KEY, {})
        if not isinstance(self.cart, dict):
            self.cart = {}
            self.session[self.SESSION_KEY] = self.cart

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, item: Item, quantity: int = 1, override: bool = False):
        item_id = str(item.id)
        quantity = int(quantity)
        if quantity < 1:
            return

        if item_id not in self.cart:
            self.cart[item_id] = {"quantity": 0}

        if override:
            self.cart[item_id]["quantity"] = quantity
        else:
            self.cart[item_id]["quantity"] += quantity
        self.save()

    def remove(self, item: Item):
        item_id = str(item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True
        self.cart = {}

    def __len__(self):
        return sum(row.get("quantity", 0) for row in self.cart.values())

    def iter_items(self):
        item_ids = [int(i) for i in self.cart.keys() if str(i).isdigit()]
        items_by_id = {str(i.id): i for i in Item.objects.filter(id__in=item_ids)}

        for item_id, row in self.cart.items():
            item = items_by_id.get(item_id)
            if not item:
                continue
            qty = int(row.get("quantity", 0) or 0)
            if qty < 1:
                continue
            price = Decimal(str(item.price))
            yield {
                "item": item,
                "quantity": qty,
                "price": price,
                "total_price": price * qty,
            }

    def get_total_price(self):
        return sum((row["total_price"] for row in self.iter_items()), Decimal("0"))