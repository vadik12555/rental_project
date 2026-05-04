from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order, OrderItem


FINAL_STATUSES = {"completed", "canceled"}


@receiver(pre_save, sender=Order)
def order_store_previous_status(sender, instance: Order, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = (
        sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    )


@receiver(post_save, sender=OrderItem)
def order_item_decrease_stock_on_create(
    sender, instance: OrderItem, created: bool, **kwargs
):
    """
    When an OrderItem is created, decrease Item.stock accordingly.

    This keeps model-level behavior consistent with Order creation,
    so tests and admin actions behave the same as API order creation.
    """
    if not created:
        return

    # If the order is already finalized/canceled, don't mutate stock.
    # (Stock restoration is handled on Order status transition.)
    if instance.order.status in FINAL_STATUSES:
        return

    with transaction.atomic():
        instance.item.__class__.objects.filter(pk=instance.item_id).update(
            stock=F("stock") - instance.quantity
        )


@receiver(post_save, sender=Order)
def order_restore_stock_on_final_status(sender, instance: Order, created: bool, **kwargs):
    if created:
        return

    previous_status = getattr(instance, "_previous_status", None)
    if previous_status == instance.status:
        return

    if instance.status not in FINAL_STATUSES:
        return

    if previous_status in FINAL_STATUSES:
        return

    # Idempotency guard: even if status keeps being saved, restore only once.
    if instance.stock_restored:
        return

    with transaction.atomic():
        order = sender.objects.select_for_update().get(pk=instance.pk)

        if order.stock_restored:
            return
        if order.status not in FINAL_STATUSES:
            return

        for oi in order.order_items.select_related("item").all():
            oi.item.__class__.objects.filter(pk=oi.item_id).update(stock=F("stock") + oi.quantity)

        sender.objects.filter(pk=order.pk).update(stock_restored=True)
