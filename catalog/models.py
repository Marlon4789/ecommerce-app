from django.db import models
from shop.models import Product


class ProductImage(models.Model):
    """
    Modelo para almacenar múltiples imágenes de un producto.
    Permite una galería estilo Mercado Libre con orden personalizado.
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        help_text='Subir imagen del producto'
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        default='Imagen del producto',
        help_text='Texto alternativo para accesibilidad'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Orden de aparición (0 es la primera)'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Marcar como imagen principal'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created']
        indexes = [
            models.Index(fields=['product', 'order']),
            models.Index(fields=['is_primary']),
        ]
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'

    def __str__(self):
        return f"Imagen de {self.product.name} - Orden {self.order}"

    def save(self, *args, **kwargs):
        # Si es la primera imagen, marcarla como principal
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_primary=False)
        elif not ProductImage.objects.filter(product=self.product, is_primary=True).exists():
            self.is_primary = True
        
        super().save(*args, **kwargs)
