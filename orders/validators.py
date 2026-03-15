"""
Validadores de stock y orden.
Proporciona funciones para validar disponibilidad de productos en ordenes.
"""

import logging
from shop.models import Product
from cart.cart import Cart

logger = logging.getLogger(__name__)


class StockValidationError(Exception):
    """Excepción lanzada cuando hay problema con el stock"""
    pass


def validate_cart_stock(cart):
    """
    Valida que todos los items en el carrito tengan stock disponible.
    
    Args:
        cart: Instancia de Cart
        
    Returns:
        tuple: (is_valid, error_messages)
        
    Raises:
        StockValidationError: Si hay problemas de stock
    """
    errors = []
    
    for item in cart:
        product = item.get('product')
        quantity = item.get('quantity')
        
        if not product:
            continue
            
        # Obtener la versión más reciente del producto
        product = Product.objects.get(id=product.id)
        
        # Validar disponibilidad
        if not product.availability:
            errors.append(f"{product.name} no está disponible")
            logger.warning(f"Producto {product.name} no disponible")
            continue
        
        # Validar stock
        if product.stock < quantity:
            errors.append(
                f"{product.name}: Solo hay {product.stock} disponibles, "
                f"pero solicitaste {quantity}"
            )
            logger.warning(
                f"Stock insuficiente para {product.name}. "
                f"Disponible: {product.stock}, Solicitado: {quantity}"
            )
    
    if errors:
        raise StockValidationError(errors)
    
    return True, []


def reserve_stock(order):
    """
    Reserva el stock para una orden.
    Se debe llamar después de crear los OrderItems pero antes de ir a pago.
    
    Args:
        order: Instancia de Order
        
    Returns:
        bool: True si la reserva fue exitosa
    """
    try:
        for item in order.items.all():
            product = item.product
            
            # Validar que haya stock
            if product.stock < item.quantity:
                raise StockValidationError(
                    f"Stock insuficiente para {product.name}. "
                    f"Disponible: {product.stock}, Necesario: {item.quantity}"
                )
        
        logger.info(f"Stock reservado para orden {order.id}")
        return True
        
    except StockValidationError as e:
        logger.error(f"Error reservando stock para orden {order.id}: {e}")
        raise


def check_product_availability(product_id, quantity):
    """
    Verifica si un producto específico está disponible en la cantidad requerida.
    
    Args:
        product_id: ID del producto
        quantity: Cantidad requerida
        
    Returns:
        dict: {'available': bool, 'message': str, 'stock': int}
    """
    try:
        product = Product.objects.get(id=product_id)
        
        if not product.availability:
            return {
                'available': False,
                'message': f"{product.name} no está disponible",
                'stock': 0
            }
        
        if product.stock < quantity:
            return {
                'available': False,
                'message': f"Stock insuficiente. Disponibles: {product.stock}",
                'stock': product.stock
            }
        
        return {
            'available': True,
            'message': f"{product.name} disponible",
            'stock': product.stock
        }
        
    except Product.DoesNotExist:
        return {
            'available': False,
            'message': "Producto no encontrado",
            'stock': 0
        }
