from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    try:
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        if request.method == 'POST':
            success_url = request.build_absolute_uri(reverse('payment:completed'))
            cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
            
            session_data = {
                'mode': 'payment',
                'client_reference_id': str(order.id),
                'success_url': success_url,
                'cancel_url': cancel_url,
                'line_items': [],
                'payment_method_types': ['card'],
            }
            
            for item in order.items.all():
                # Para debugging
                print(f"Procesando item: {item.product.name}")
                print(f"Precio original: {item.price}")
                # price_in_cents = int(float(item.price) * 100)
                price_in_cents = int(Decimal(item.price) * 100)
                print(f"Precio en centavos: {price_in_cents}")
                
                session_data['line_items'].append({
                    'price_data': {
                        'unit_amount': price_in_cents,
                        'currency': settings.STRIPE_CURRENCY,  # Usa la moneda desde settings
                        'product_data': {
                            'name': str(item.product.name),
                            'description': f"Cantidad: {item.quantity}"
                        },
                    },
                    'quantity': item.quantity,
                })
            
            try:
                # Debug info
                print("Datos de sesión:", session_data)
                
                session = stripe.checkout.Session.create(**session_data)
                order.stripe_id = session.id
                order.save()
                
                print(f"Sesión creada exitosamente: {session.id}")
                return redirect(session.url, code=303)
                
            except stripe.error.StripeError as e:
                print(f"Error de Stripe: {str(e)}")
                return render(request, 'payment/error.html', {
                    'error': str(e),
                    'debug_info': {
                        'currency': settings.STRIPE_CURRENCY,
                        'amount': price_in_cents
                    }
                })
                
    except Exception as e:
        print(f"Error general: {str(e)}")
        return render(request, 'payment/error.html', {'error': str(e)})
    
    return render(request, 'payment/process.html', {'order': order})

    
def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')

def payment_error(request):
    return render(request, 'payment/error.html')