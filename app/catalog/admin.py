from django.contrib import admin
from .models import Item  , Order

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
            from django.utils.safestring import mark_safe
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет фото"