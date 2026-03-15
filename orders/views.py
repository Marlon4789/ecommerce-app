from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from shop.models import Product
from .email_service import send_order_confirmation_email
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Validar stock antes de crear la orden
            for item in cart:
                product = Product.objects.get(id=item['product'].id)
                if product.stock < item['quantity']:
                    messages.error(
                        request,
                        f"Stock insuficiente para {product.name}. "
                        f"Disponibles: {product.stock}, Solicitados: {item['quantity']}"
                    )
                    return redirect('cart:cart_detail')
            
            # Usar transaccion para asegurar integridad de datos
            with transaction.atomic():
                order = form.save()
                for item in cart:
                    product = Product.objects.get(id=item['product'].id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=item['price'],
                        quantity=item['quantity']
                    )
            
            cart.clear()
            
            # Enviar email de confirmacion (con fallback automatico)
            try:
                send_order_confirmation_email(order.id)
            except Exception as e:
                logger.error(f"Error en servicio de email para orden {order.id}: {str(e)}")
            
            # Guardar orden en sesion
            request.session['order_id'] = order.id
            messages.success(request, f"Orden creada exitosamente. ID: {order.id}")
            # Redirigir a pago
            return redirect(reverse('payment:process'))
           
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form
    })

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})