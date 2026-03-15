from decimal import Decimal
import stripe
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    """
    ✅ FLUJO SIMPLIFICADO: Usa Stripe Payment Element con PaymentIntent
    GET: Crea PaymentIntent y muestra formulario
    """
    try:
        order_id = request.session.get('order_id')
        
        if not order_id:
            messages.error(request, "No hay orden para procesar")
            return redirect('shop:product_list')
        
        order = get_object_or_404(Order, id=order_id)
        
        # Validar que la orden tenga items
        if not order.items.exists():
            messages.error(request, "La orden no tiene items")
            logger.error(f"Orden {order_id} sin items")
            return redirect('cart:cart_detail')
        
        # Calcular monto total en centavos
        amount_in_cents = int(order.get_total_cost() * 100)
        
        try:
            # ✅ Crear PaymentIntent (GET y POST crean uno nuevo - Stripe maneja duplicates)
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=settings.STRIPE_CURRENCY,
                metadata={
                    'order_id': str(order.id),
                    'order_email': order.email
                },
                automatic_payment_methods={'enabled': True}
            )
            
            # Guardar reference
            order.stripe_id = intent.id
            order.save()
            
            logger.info(f"✅ PaymentIntent creado: {intent.id} para orden {order.id}")
            logger.info(f"   Monto: {amount_in_cents} centavos ({settings.STRIPE_CURRENCY})")
            
            return render(request, 'payment/process.html', {
                'order': order,
                'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
                'client_secret': intent.client_secret,
                'return_url': request.build_absolute_uri(reverse('payment:completed')),
            })
            
        except stripe.error.InvalidRequestError as e:
            logger.error(f"❌ Error en parametros Stripe: {str(e)}")
            messages.error(request, "Error en los parametros de pago")
            return render(request, 'payment/error.html', {
                'error': "Error en la configuracion del pago"
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"❌ Error de Stripe: {str(e)}")
            messages.error(request, "Error al procesar el pago")
            return render(request, 'payment/error.html', {
                'error': str(e)
            })
        
    except Exception as e:
        logger.exception(f"❌ Error general en payment_process: {str(e)}")
        messages.error(request, "Error al procesar el pago")
        return render(request, 'payment/error.html', {
            'error': f"Error: {str(e)}"
        })

    
def payment_completed(request):
    """
    Página que se muestra después de un pago exitoso.
    """
    order_id = request.session.get('order_id')
    try:
        if order_id:
            order = Order.objects.get(id=order_id)
            # Limpiar la sesión
            if 'order_id' in request.session:
                del request.session['order_id']
            return render(request, 'payment/completed.html', {'order': order})
    except Order.DoesNotExist:
        logger.error(f"Orden {order_id} no encontrada en completed")
    
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    """
    Página que se muestra si el usuario cancela el pago.
    """
    order_id = request.session.get('order_id')
    messages.info(request, "Pago cancelado. Puedes intentar de nuevo.")
    return render(request, 'payment/canceled.html')


def payment_error(request):
    """
    Página de error general de pago.
    """
    return render(request, 'payment/error.html')