from django.contrib import admin
from .models import Item, Order, Product  
from django.utils.safestring import mark_safe

admin.site.register(Item)
# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at') # Добавили status
    list_filter = ('status', 'created_at') # Добавили фильтр справа
    list_editable = ('status',) # Позволяет менять статус прямо в списке!
    readonly_fields = ('created_at', 'total_price')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'stock') # Выводим остатки
    search_fields = ('title',) # Поиск по названию
    list_editable = ('price', 'stock') # Меняем прямо в списке
    eadonly_fields = ('get_image_preview',)
    
    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет фото"
    get_image_preview.short_description = "Превью"
    
    # Позволяет добавлять/удалять товары прямо на странице заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('item',) # Удобный выбор товара, если их будет 1000+



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    # Подключаем товары к заказу
    inlines = [OrderItemInline]
    # Запрещаем менять итоговую цену вручную (пусть считает метод save)
    readonly_fields = ('total_price', 'created_at')