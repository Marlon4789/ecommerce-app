from rest_framework import serializers
from shop.models import Product, Category
from catalog.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializador para imágenes de productos"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order', 'is_primary']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializador optimizado para listado de productos.
    Incluye información básica e imágenes.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'slug',
            'name',
            'price',
            'promotional_price',
            'on_sale',
            'current_price',
            'stock',
            'availability',
            'category_name',
            'images',
            'grinding_type',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializador completo para vista detallada del producto.
    Incluye descripción completa e imágenes en orden.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'slug',
            'name',
            'description',
            'price',
            'promotional_price',
            'on_sale',
            'current_price',
            'discount_percentage',
            'stock',
            'availability',
            'weight',
            'grinding_type',
            'category_name',
            'images',
            'created_date',
            'updated',
        ]
    
    def get_discount_percentage(self, obj):
        """Calcula el descuento porcentual"""
        if obj.on_sale and obj.promotional_price:
            discount = ((obj.price - obj.promotional_price) / obj.price) * 100
            return round(discount, 0)
        return 0


class CategorySerializer(serializers.ModelSerializer):
    """Serializador para categorías"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
