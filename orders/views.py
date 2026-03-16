import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from shop.models import Product

logger = logging.getLogger(__name__)


def order_create(request):
    """
    Crea la orden y sus items, limpia el carrito y redirige a pago.
    El correo de confirmación se envía desde la signal DESPUÉS del pago,
    no aquí, para no enviar correos de órdenes que nunca se pagaron.
    """
    cart = Cart(request)

    if not cart:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            # ── Validar stock antes de crear la orden ──────────────────────
            for item in cart:
                product = Product.objects.get(id=item['product'].id)
                if product.stock < item['quantity']:
                    messages.error(
                        request,
                        f"Stock insuficiente para '{product.name}'. "
                        f"Disponibles: {product.stock}, "
                        f"solicitados: {item['quantity']}."
                    )
                    return redirect('cart:cart_detail')

            # ── Crear orden e items en una transacción ─────────────────────
            try:
                with transaction.atomic():
                    order = form.save()
                    for item in cart:
                        product = Product.objects.get(id=item['product'].id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=item['price'],
                            quantity=item['quantity'],
                        )

                cart.clear()
                request.session['order_id'] = order.id
                logger.info(f"Orden #{order.id} creada. Redirigiendo a pago.")
                return redirect(reverse('payment:process'))

            except Exception as e:
                logger.error(f"Error creando orden: {e}")
                messages.error(request, "Ocurrió un error al crear tu pedido. Intenta de nuevo.")
                return redirect('cart:cart_detail')
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form,
    })


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})