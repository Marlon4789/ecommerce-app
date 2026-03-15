import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt
def stripe_webhook(request):
    import logging
    logger = logging.getLogger(__name__)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Payload inválido: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Firma inválida: {e}")
        return HttpResponse(status=400)

    logger.info(f"Evento Stripe recibido: {event.type}")

    # ✅ NUEVO: Manejar PaymentIntent (nuevo flujo con Payment Element)
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        order_id = payment_intent.metadata.get('order_id')
        
        logger.info(f"PaymentIntent completado: {payment_intent.id}")
        logger.info(f"  Order ID from metadata: {order_id}")
        logger.info(f"  Status: {payment_intent.status}")
        
        try:
            order = Order.objects.get(id=order_id)
            logger.info(f"Orden encontrada: #{order.id}")
            
            if not order.paid:
                order.paid = True
                order.stripe_id = payment_intent.id
                order.save()
                logger.info(f"✅ Orden #{order.id} marcada como PAGADA. PaymentIntent: {payment_intent.id}")
                
                # Log delStock antes de actualización por signal
                logger.info(f"Items en orden #{order.id}:")
                for item in order.items.all():
                    logger.info(f"  - {item.product.name} x{item.quantity}")
            else:
                logger.info(f"Orden #{order.id} ya estaba marcada como pagada")
                
        except Order.DoesNotExist:
            logger.error(f"❌ Orden NO encontrada: {order_id}")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"❌ Error procesando orden: {e}")
            return HttpResponse(status=500)

    # ✅ ANTIGUO: Manejar Checkout Session (flujo anterior)
    elif event.type == 'checkout.session.completed':
        session = event.data.object
        
        logger.info(f"Sessión checkout completada: {session.id}")
        logger.info(f"  Mode: {session.mode}")
        logger.info(f"  Payment Status: {session.payment_status}")
        logger.info(f"  Client Reference ID: {session.client_reference_id}")

        try:
            # Buscar orden por client_reference_id (que es el order.id)
            order_id = session.client_reference_id
            if not order_id:
                logger.error("No client_reference_id en session")
                return HttpResponse(status=400)
                
            order = Order.objects.get(id=order_id)
            logger.info(f"Orden encontrada: #{order.id}")
            
            if not order.paid:
                order.paid = True
                order.stripe_id = session.id
                order.save()
                logger.info(f"✅ Orden #{order.id} marcada como PAGADA. Stripe ID: {session.id}")
                
                logger.info(f"Items en orden #{order.id}:")
                for item in order.items.all():
                    logger.info(f"  - {item.product.name} x{item.quantity}")
            else:
                logger.info(f"Orden #{order.id} ya estaba marcada como pagada")
                
        except Order.DoesNotExist:
            logger.error(f"❌ Orden NO encontrada: {session.client_reference_id}")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"❌ Error procesando orden: {e}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)

