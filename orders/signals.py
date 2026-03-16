import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

logger = logging.getLogger(__name__)


@receiver(post_save, sender='orders.Order')
def handle_order_paid(sender, instance, created, **kwargs):
    """
    Cuando una orden se marca como pagada:
    1. Descuenta el stock de cada producto (una sola vez).
    2. Dispara el envío del correo de confirmación (una sola vez).
    """
    if not instance.paid:
        return

    _reduce_stock(instance)
    _send_confirmation_email(instance)


def _reduce_stock(order):
    """Descuenta el stock. Usa update() para evitar recursión en la signal."""
    # ✅ Re-leer desde BD para tener el valor más reciente
    from orders.models import Order
    if Order.objects.filter(pk=order.pk, stock_reduced=True).exists():
        return

    try:
        with transaction.atomic():
            for item in order.items.select_related('product').all():
                product = (
                    item.product.__class__.objects
                    .select_for_update()
                    .get(pk=item.product.pk)
                )
                previous = product.stock
                product.stock = max(0, product.stock - item.quantity)

                if product.stock == 0:
                    product.availability = False

                product.save(update_fields=['stock', 'availability'])
                logger.info(
                    f"Stock actualizado — {product.name}: "
                    f"{previous} → {product.stock}"
                )

            # ✅ update() directo evita disparar post_save de nuevo
            Order.objects.filter(pk=order.pk).update(stock_reduced=True)
            logger.info(f"Orden #{order.id}: stock_reduced=True")

    except Exception as e:
        logger.error(f"Error reduciendo stock para orden #{order.id}: {e}")


def _send_confirmation_email(order):
    """Envía correo de confirmación una sola vez."""
    from orders.models import Order
    if Order.objects.filter(pk=order.pk, confirmation_sent=True).exists():
        return

    try:
        from orders.email_service import send_order_confirmation_email
        send_order_confirmation_email(order.id)

        # ✅ update() directo evita disparar post_save de nuevo
        Order.objects.filter(pk=order.pk).update(confirmation_sent=True)
        logger.info(f"Orden #{order.id}: confirmation_sent=True")

    except Exception as e:
        logger.error(f"Error enviando correo para orden #{order.id}: {e}")