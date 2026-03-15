from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def order_created(self, order_id):
    """
    Tarea para enviar un correo de confirmacion cuando se realiza un pedido con exito.
    Implementa reintentos automaticos y manejo robusto de errores.
    """
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f'Gracias por tu compra, {order.full_name}!'
        message = (
            f"Hola {order.full_name},\n\n"
            f"Tu pedido ha sido confirmado con exito!\n\n"
            f"Numero de pedido: {order.id}\n"
            f"Estamos preparando todo con mucho cariño para que disfrutes de la mejor experiencia con Coffee Shop. "
            f"Pronto recibiras mas informacion sobre el envio.\n\n"
            f"Si tienes alguna pregunta, no dudes en responder a este correo. Estamos aqui para ayudarte!\n\n"
            f"Gracias por confiar en nosotros.\n\n"
            f"Equipo de Coffee Shop"
        )
        
        mail_sent = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False
        )
        
        logger.info(f"Email de confirmacion enviado a {order.email} para orden {order.id}")
        return mail_sent
        
    except Order.DoesNotExist:
        logger.error(f"Orden {order_id} no encontrada")
        return False
        
    except Exception as exc:
        logger.error(f"Error enviando email para orden {order_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
