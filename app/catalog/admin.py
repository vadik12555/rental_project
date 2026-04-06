from django.contrib import admin
from .models import Item  , Order

admin.site.register(Item)
# Register your models here.
admin.site.register(Order)
