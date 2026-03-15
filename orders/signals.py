# orders/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def update_stock(sender, instance, created=False, **kwargs):
    """
    Signal que actualiza el stock cuando un pedido es marcado como pagado.
    Usa el campo 'stock_reduced' en BD para evitar múltiples reducciones.
    """
    # ✅ ARREGLO: Verifica el campo de BD en lugar de una bandera en memoria
    if instance.paid and not instance.stock_reduced:
        try:
            for item in instance.items.all():
                product = item.product
                previous_stock = product.stock
                product.stock -= item.quantity
                
                if product.stock < 0:
                    product.stock = 0
                    
                if product.stock == 0:
                    product.availability = False
                    
                product.save()
                logger.info(
                    f"Stock actualizado para producto {product.name}. "
                    f"Stock anterior: {previous_stock}, Stock nuevo: {product.stock}"
                )
            
            # ✅ Marcar en BD que el stock fue reducido
            instance.stock_reduced = True
            instance.save(update_fields=['stock_reduced'])
            logger.info(f"Orden {instance.id} marcada con stock_reduced=True")
        except Exception as e:
            logger.error(f"Error al actualizar stock para orden {instance.id}: {str(e)}")
