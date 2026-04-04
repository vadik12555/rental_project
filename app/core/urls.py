from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views import ItemViewSet
from django.conf import settings
from catalog.views import ItemViewSet, OrderViewSet
from django.conf.urls.static import static
# Роутер сам создаст пути для GET, POST, PUT, DELETE
router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'orders' , OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # Подключаем наше API
    path('', include(router.urls)),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)