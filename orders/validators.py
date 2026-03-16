"""
Validadores de stock y disponibilidad para órdenes.
"""
import logging
from shop.models import Product

logger = logging.getLogger(__name__)


class StockValidationError(Exception):
    """Lanzada cuando hay un problema de stock al validar el carrito."""
    pass


def validate_cart_stock(cart):
    """
    Valida que todos los items del carrito tengan stock suficiente.
    Lanza StockValidationError con la lista de mensajes si hay problemas.
    """
    errors = []

    for item in cart:
        product_obj = item.get('product')
        quantity    = item.get('quantity', 0)

        if not product_obj:
            continue

        # Refrescar desde BD para tener datos actualizados
        try:
            product = Product.objects.get(id=product_obj.id)
        except Product.DoesNotExist:
            errors.append(f"El producto con ID {product_obj.id} ya no existe.")
            continue

        if not product.availability:
            errors.append(f"'{product.name}' no está disponible.")
            continue

        if product.stock < quantity:
            errors.append(
                f"'{product.name}': solo hay {product.stock} unidades "
                f"disponibles, pero solicitaste {quantity}."
            )

    if errors:
        raise StockValidationError(errors)

    return True, []


def check_product_availability(product_id, quantity):
    """
    Verifica si un producto específico tiene stock para la cantidad pedida.
    Retorna un dict con 'available', 'message' y 'stock'.
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return {'available': False, 'message': 'Producto no encontrado.', 'stock': 0}

    if not product.availability:
        return {
            'available': False,
            'message': f"'{product.name}' no está disponible.",
            'stock': 0,
        }

    if product.stock < quantity:
        return {
            'available': False,
            'message': f"Stock insuficiente. Disponibles: {product.stock}.",
            'stock': product.stock,
        }

    return {
        'available': True,
        'message': f"'{product.name}' disponible.",
        'stock': product.stock,
    }