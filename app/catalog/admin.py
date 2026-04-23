from django.contrib import admin
from .models import Item, Order, Product  
from django.utils.safestring import mark_safe

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'stock', 'get_image_preview') 
    readonly_fields = ('get_image_preview',)
    
    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет фото"
    get_image_preview.short_description = "Превью"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_editable = ('status',)

admin.site.register(Product) # Самая простая регистрация для третьего товара