from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from catalog.views import (
    ItemViewSet,
    OrderViewSet,
    item_list,
    CartAPIView,
    cart_add,
    cart_detail,
    cart_remove,
    cart_update,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.views.generic import RedirectView
from catalog import views as catalog_views

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('shop/', item_list, name='shop'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/cart/', CartAPIView.as_view(), name='cart_api'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:item_id>/', cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', cart_remove, name='cart_remove'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('my-orders/', catalog_views.my_orders, name='my_orders'),
    path('', RedirectView.as_view(url='/shop/', permanent=True)), 
]

# Чтобы работали картинки, если ты их загружаешь
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)