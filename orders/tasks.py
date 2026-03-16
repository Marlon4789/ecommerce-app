import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def order_created(self, order_id):
    """
    Tarea Celery para enviar correo de confirmación.
    Se reintenta automáticamente hasta 3 veces si falla.
    """
    from .models import Order  # import local para evitar problemas de arranque

    try:
        order = Order.objects.get(id=order_id)

        subject = f'Confirmación de tu pedido #{order.id} — Kaboha Coffee'
        items_lines = "\n".join(
            f"  • {item.product.name} x{item.quantity}  →  ${item.get_cost()}"
            for item in order.items.all()
        )
        message = (
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

        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        logger.info(f"Correo enviado a {order.email} para orden #{order.id}")
        return sent

    except Order.DoesNotExist:
        logger.error(f"Orden #{order_id} no encontrada — tarea cancelada")
        return False

    except Exception as exc:
        logger.error(f"Error enviando correo para orden #{order_id}: {exc}")
        # Reintento exponencial: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))