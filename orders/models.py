from django.db import models


class Order(models.Model):
    full_name         = models.CharField(max_length=100, default='')
    email             = models.EmailField(default='')
    address           = models.CharField(max_length=250, default='')
    postal_code       = models.CharField(max_length=20, default='')
    city              = models.CharField(max_length=100, default='')
    created           = models.DateTimeField(auto_now_add=True)
    updated           = models.DateTimeField(auto_now=True)
    paid              = models.BooleanField(default=False)
    stripe_id         = models.CharField(max_length=250, blank=True, default='')
    stock_reduced     = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        indexes  = [models.Index(fields=['-created'])]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self):
        """Retorna la URL del pago en el dashboard de Stripe."""
        if not self.stripe_id:
            return ''
        # Si es un pago de prueba usa /test/
        path = '/test/' if '_test_' in self.stripe_id else '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product  = models.ForeignKey(
        'shop.Product', related_name='order_items', on_delete=models.CASCADE
    )
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity