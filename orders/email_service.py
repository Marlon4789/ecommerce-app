"""
Servicio de email con fallback a envío sincrónico si Celery falla.
Proporciona un manejo robusto del envío de emails en la aplicación.
"""

import logging
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.db import transaction
from .models import Order

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order_id):
    """
    Envía un email de confirmación de orden.
    Intenta enviar mediante Celery, con fallback a envío sincrónico.
    
    Args:
        order_id: ID de la orden
        
    Returns:
        bool: True si el email fue enviado, False en caso contrario
    """
    try:
        from .tasks import order_created
        # Intentar enviar de forma asincrónica
        order_created.delay(order_id)
        logger.info(f"Tarea de email encolada para orden {order_id}")
        return True
        
    except Exception as e:
        logger.warning(
            f"Celery no disponible, usando envío sincrónico para orden {order_id}: {str(e)}"
        )
        # Fallback: envío sincrónico
        return send_order_confirmation_sync(order_id)


def send_order_confirmation_sync(order_id):
    """
    Envía un email de confirmación de forma sincrónica.
    Se usa como fallback cuando Celery no está disponible.
    
    Args:
        order_id: ID de la orden
        
    Returns:
        bool: True si el email fue enviado, False en caso contrario
    """
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f'Confirmacion de tu pedido #{order_id} - Coffee Shop'
        
        email_body = f"""
Hola {order.full_name},

Gracias por tu compra en Coffee Shop!

Tu pedido ha sido confirmado exitosamente.

Detalles del pedido:
- Numero de pedido: {order.id}
- Fecha: {order.created.strftime('%d/%m/%Y %H:%M')}
- Total: ${order.get_total_cost()}

Productos:
"""
        
        for item in order.items.all():
            email_body += f"\n- {item.product.name} x{item.quantity} = ${item.get_cost()}"
        
        email_body += f"""

Direccion de envio:
{order.address}
{order.postal_code} {order.city}

Pronto recibieras mas informacion sobre el estado de tu envio.

Si tienes preguntas, puedes responder a este correo.

Gracias por confiar en Coffee Shop!
Equipo de Coffee Shop
"""
        
        email_message = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        
        mail_sent = email_message.send(fail_silently=False)
        logger.info(f"Email enviado sincronicamente para orden {order_id}")
        return mail_sent
        
    except Order.DoesNotExist:
        logger.error(f"Orden {order_id} no encontrada")
        return False
        
    except Exception as e:
        logger.error(f"Error enviando email para orden {order_id}: {str(e)}")
        # Registrar el error pero no lanzar excepción para no romper el flujo
        return False
