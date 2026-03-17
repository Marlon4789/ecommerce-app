from django.shortcuts import render
from django.views.generic import ListView, DetailView
from shop.models import Product, Category
from cart.forms import CartAddProductForm


class ProductListView(ListView):
    """Home principal — Hero + sección Negocios."""
    model = Product
    template_name = 'products/product_home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(availability=True).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_add_form'] = CartAddProductForm()
        return context


class ProductCatalogView(ListView):
    """Catálogo completo de productos con buscador JS."""
    model = Product
    template_name = 'products/product_catalog.html'
    context_object_name = 'products'
    # Sin paginación — el filtro es client-side (JavaScript)

    def get_queryset(self):
        return Product.objects.filter(availability=True).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_add_form'] = CartAddProductForm()
        return context


class ProductDetailView(DetailView):
    """Detalle individual de producto."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return super().get_queryset().filter(availability=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_add_form'] = CartAddProductForm()
        return context