# orders/management/commands/simulate_payment.py
from django.core.management.base import BaseCommand
from orders.models import Order


class Command(BaseCommand):
    help = 'Simula un pago exitoso para probar stock y correo'

    def add_arguments(self, parser):
        parser.add_argument('order_id', type=int)

    def handle(self, *args, **options):
        order_id = options['order_id']
        try:
            order = Order.objects.get(id=order_id)

            if order.paid:
                self.stdout.write(
                    self.style.WARNING(f'Orden #{order_id} ya estaba pagada.')
                )
                return

            self.stdout.write(f'Orden #{order_id} encontrada: {order.full_name}')
            self.stdout.write(f'Items:')
            for item in order.items.all():
                self.stdout.write(
                    f'  - {item.product.name} x{item.quantity} '
                    f'(stock actual: {item.product.stock})'
                )

            # ✅ Esto dispara la signal → descuenta stock + envía correo
            order.paid = True
            order.stripe_id = 'pi_test_simulado'
            order.save()

            # Refrescar desde BD para ver cambios
            order.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Orden #{order_id} marcada como pagada.'
            ))
            self.stdout.write(f'stock_reduced     : {order.stock_reduced}')
            self.stdout.write(f'confirmation_sent : {order.confirmation_sent}')
            self.stdout.write(f'\nStock actualizado:')
            for item in order.items.all():
                item.product.refresh_from_db()
                self.stdout.write(
                    f'  - {item.product.name}: stock = {item.product.stock}'
                )

        except Order.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Orden #{order_id} no encontrada.'))