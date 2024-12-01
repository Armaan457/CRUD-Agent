from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from products.views import ProductViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Product API",
        default_version="v1",
        description="API for managing products",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),  
]
