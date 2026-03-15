from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.utils.safestring import mark_safe
from shop.models import Product, Category
from catalog.serializers import (
    ProductListSerializer, 
    ProductDetailSerializer,
    CategorySerializer
)
from catalog.models import ProductImage
import json


class ProductPagination(PageNumberPagination):
    """Paginación personalizada para productos"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para búsqueda y listado de productos con filtros avanzados.
    
    Query parameters:
    - q: Búsqueda por nombre o descripción
    - category: ID de categoría
    - min_price: Precio mínimo
    - max_price: Precio máximo
    - on_sale: true/false para productos en oferta
    - sort: 'name', 'price', '-price', '-created'
    """
    queryset = Product.objects.filter(availability=True).prefetch_related('images', 'category')
    pagination_class = ProductPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'created_date']
    ordering = ['name']

    def get_serializer_class(self):
        """Usar serializador diferente para detalle vs listado"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        """
        Filtrar productos basado en parámetros de query.
        """
        queryset = super().get_queryset()
        
        # Búsqueda por texto
        search_query = self.request.query_params.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filtro por categoría
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filtro de precio
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        
        # Filtro por ofertas
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(on_sale=True)
        
        # Filtro por tipo de molienda
        grinding_type = self.request.query_params.get('grinding_type')
        if grinding_type:
            queryset = queryset.filter(grinding_type=grinding_type)
        
        # Ordenamiento personalizado
        sort = self.request.query_params.get('sort')
        if sort in ['name', 'price', '-price', '-created_date']:
            queryset = queryset.order_by(sort)
        
        return queryset.distinct()

    @action(detail=True, methods=['get'])
    def recommended(self, request, pk=None):
        """
        Obtiene productos recomendados para un producto específico.
        Estrategia:
        1. Misma categoría (más relevante)
        2. Precio similar ±20%
        3. Que NO sea el producto actual
        4. Máximo 6 productos
        """
        product = self.get_object()
        
        # Calcular rango de precio similar (±20%)
        price_20_percent = float(product.current_price) * 0.20
        min_price = float(product.current_price) - price_20_percent
        max_price = float(product.current_price) + price_20_percent
        
        # Búsqueda de recomendados
        recommended = Product.objects.filter(
            availability=True,
            category=product.category
        ).exclude(
            id=product.id
        ).filter(
            price__gte=min_price,
            price__lte=max_price
        ).prefetch_related('images')[:6]
        
        # Si hay pocos productos en la categoría, buscar en rango de precio similar
        if recommended.count() < 4:
            recommended = Product.objects.filter(
                availability=True,
                price__gte=min_price,
                price__lte=max_price
            ).exclude(
                id=product.id,
                category=product.category
            ).prefetch_related('images')[:6]
        
        serializer = ProductListSerializer(recommended, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Obtiene todas las categorías disponibles"""
        categories = Category.objects.filter(active=True).order_by('name')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def price_range(self, request):
        """
        Retorna el rango de precios disponibles para filtros.
        Útil para renderizar sliders de precio.
        """
        products = Product.objects.filter(availability=True)
        
        if not products.exists():
            return Response({
                'min_price': 0,
                'max_price': 0,
            })
        
        min_price = products.order_by('price').first().price
        max_price = products.order_by('-price').first().price
        
        return Response({
            'min_price': float(min_price),
            'max_price': float(max_price),
        })

    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Obtiene solo productos en oferta/promoción"""
        queryset = Product.objects.filter(
            availability=True,
            on_sale=True
        ).prefetch_related('images').order_by('-created_date')[:12]
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


# ==================== FRONTEND VIEWS ====================

class ProductSearchView(TemplateView):
    """Página de búsqueda de productos con filtros"""
    template_name = 'catalog/product_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductDetailFrontendView(DetailView):
    """Página de detalle del producto mejorada con carrusel y recomendados"""
    model = Product
    template_name = 'catalog/product_detail.html'
    slug_field = 'slug'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(availability=True).prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Obtener imágenes del producto
        images = product.images.all().order_by('order')
        
        # Convertir a JSON para el template
        images_json = json.dumps([
            {
                'id': img.id,
                'image': img.image.url,
                'alt_text': img.alt_text,
                'order': img.order,
                'is_primary': img.is_primary,
            }
            for img in images
        ])
        
        # Si no tiene imágenes, usar la imagen heredada o un placeholder
        if not images:
            images_json = json.dumps([
                {
                    'id': 0,
                    'image': product.image or 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=600&fit=crop',
                    'alt_text': product.name,
                    'order': 0,
                    'is_primary': True,
                }
            ])
        
        context['images_json'] = mark_safe(images_json)
        context['images'] = images
        
        # Calcular porcentaje de descuento
        if product.on_sale and product.promotional_price:
            discount = ((product.price - product.promotional_price) / product.price) * 100
            context['discount_percentage'] = int(discount)
        
        return context
