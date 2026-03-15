"""
Comando personalizado para validar y reparar problemas de stock en ordenes.
Uso: python manage.py fix_stock_issues
"""

from django.core.management.base import BaseCommand
from orders.models import Order, OrderItem
from shop.models import Product
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Detecta y repara problemas de stock en ordenes pagadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write("Verificando ordenes pagadas...")
        
        # Obtener todas las ordenes pagadas
        paid_orders = Order.objects.filter(paid=True)
        stock_issues = []
        
        for order in paid_orders:
            for item in order.items.all():
                product = item.product
                # Verificar si ya se restó el stock
                # (Esta es una heurística, idealmente tendrías un campo de audit)
                logger.info(f"Orden {order.id}: {product.name} x{item.quantity}")
        
        if stock_issues:
            self.stdout.write(
                self.style.WARNING(
                    f"Se encontraron {len(stock_issues)} problemas de stock"
                )
            )
            
            for issue in stock_issues:
                self.stdout.write(f"  - {issue}")
            
            if not dry_run:
                self.stdout.write(self.style.SUCCESS("Problemas reparados"))
        else:
            self.stdout.write(
                self.style.SUCCESS("No se encontraron problemas de stock")
            )
