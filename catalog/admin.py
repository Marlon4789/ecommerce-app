from django.contrib import admin
from .models import ProductImage


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin para gestionar imágenes de productos"""
    list_display = ['product', 'order', 'is_primary', 'created']
    list_filter = ['is_primary', 'created', 'product__category']
    search_fields = ['product__name', 'alt_text']
    ordering = ['product', 'order']
    
    fieldsets = (
        ('Producto', {
            'fields': ('product',)
        }),
        ('Imagen', {
            'fields': ('image', 'alt_text')
        }),
        ('Configuración', {
            'fields': ('order', 'is_primary')
        }),
    )
    
    readonly_fields = ['created', 'updated']
    
    def save_model(self, request, obj, form, change):
        """Asegurar que solo haya una imagen principal por producto"""
        if obj.is_primary:
            ProductImage.objects.filter(product=obj.product).exclude(pk=obj.pk).update(is_primary=False)
        super().save_model(request, obj, form, change)
