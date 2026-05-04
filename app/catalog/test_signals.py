import pytest

from django.contrib.auth import get_user_model

from .models import Item, Order, OrderItem


@pytest.mark.django_db
def test_restore_item_stock_on_order_canceled_signal():
    user = get_user_model().objects.create_user(username="u1", password="pass12345")

    item = Item.objects.create(
        title="Test item",
        description="desc",
        price="10.00",
        stock=10,
    )

    order = Order.objects.create(user=user)
    OrderItem.objects.create(order=order, item=item, quantity=3)

    item.refresh_from_db()
    assert item.stock == 7

    order.status = "canceled"
    order.save(update_fields=["status"])

    item.refresh_from_db()
    assert item.stock == 10

