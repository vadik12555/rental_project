from django.contrib import admin
from .models import Item  , Order

admin.site.register(Item)
# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at') # Добавили status
    list_filter = ('status', 'created_at') # Добавили фильтр справа
    list_editable = ('status',) # Позволяет менять статус прямо в списке!