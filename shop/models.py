from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=300, unique=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

        verbose_name = 'category' 
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    weight = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    on_sale = models.BooleanField(default=False)

    def current_price(self):
        if self.on_sale and self.promotional_price:
            return str(self.promotional_price)
        return str(self.price)
    

    

    GRINDING_TYPE_CHOICES = [
        ('fine', 'fine'),
        ('medium', 'medium'),
        ('coarse', 'coarse')
    ]
    grinding_type = models.CharField(max_length=10, choices=GRINDING_TYPE_CHOICES)

    availability = models.BooleanField(default=True)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/')
    created_date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
  
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_date']),
        ]

    def __str__(self):
        return self.name
