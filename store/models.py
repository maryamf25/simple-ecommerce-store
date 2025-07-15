from django.db import models
from django.contrib.auth.models import User

# Product model to store all products in the store
class Product(models.Model):
    name = models.CharField(max_length=200)  # Product name
    description = models.TextField()         # Product description
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price with decimals
    image = models.ImageField(upload_to='products/')  # Product image uploaded to 'products/' folder

    def __str__(self):
        return self.name  # Shows product name in admin panel

# Order model to store placed orders by users
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who placed order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Product ordered
    quantity = models.PositiveIntegerField(default=1)  # Quantity ordered
    ordered_at = models.DateTimeField(auto_now_add=True)  # Timestamp of order

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
