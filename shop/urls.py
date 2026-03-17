from django.urls import path
from shop.views import ProductListView, ProductCatalogView, ProductDetailView

app_name = 'shop'

urlpatterns = [
    # Home principal
    path('', ProductListView.as_view(), name='product_list'),

    # Catálogo de productos con buscador
    path('products/', ProductCatalogView.as_view(), name='product_catalog'),

    # Detalle de producto
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]