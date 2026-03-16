import logging
from django.core.mail import EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order_id):
    """
    Intenta enviar el correo vía Celery.
    Si Celery no está disponible, hace el envío de forma sincrónica.
    """
    try:
        from .tasks import order_created
        order_created.delay(order_id)
        logger.info(f"Tarea Celery encolada para orden #{order_id}")
        return True
    except Exception as e:
        logger.warning(
            f"Celery no disponible, enviando de forma sincrónica "
            f"para orden #{order_id}: {e}"
        )
        return _send_sync(order_id)


def _send_sync(order_id):
    """Envío sincrónico como fallback cuando Celery no está disponible."""
    from .models import Order  # import local

    try:
        order = Order.objects.get(id=order_id)

        subject = f'Confirmación de tu pedido #{order.id} — Kaboha Coffee'
        items_lines = "\n".join(
            f"  • {item.product.name} x{item.quantity}  →  ${item.get_cost()}"
            for item in order.items.all()
        )
        body = (
            f"Hola {order.full_name},\n\n"
            f"¡Tu pago fue confirmado! Gracias por comprar en Kaboha Coffee.\n\n"
            f"Número de pedido: #{order.id}\n"
            f"Fecha: {order.created.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Productos:\n{items_lines}\n\n"
            f"Total: ${order.get_total_cost()}\n\n"
            f"Dirección de envío:\n"
            f"{order.address}\n"
            f"{order.postal_code} — {order.city}\n\n"
            f"Pronto recibirás información sobre el envío.\n\n"
            f"¡Hasta pronto!\n"
            f"Equipo Kaboha Coffee"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        sent = email.send(fail_silently=False)
        logger.info(f"Correo sincrónico enviado para orden #{order_id}")
        return sent

    except Order.DoesNotExist:
        logger.error(f"Orden #{order_id} no encontrada")
        return False
    except Exception as e:
        logger.error(f"Error en envío sincrónico para orden #{order_id}: {e}")
        return False