from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductSearchView, ProductDetailFrontendView

app_name = 'catalog'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # API Routes
    path('api/', include(router.urls)),
    
    # Frontend Routes
    path('products/', ProductSearchView.as_view(), name='product-list'),
    path('product/<slug:slug>/', ProductDetailFrontendView.as_view(), name='product-detail'),
]
