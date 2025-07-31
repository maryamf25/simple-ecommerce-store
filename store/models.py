from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Optional. Used for showing discount."
    )
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to='products/')
    tags = models.ManyToManyField(Tag, blank=True)  # ✅ Tag relationship

    def __str__(self):
        return self.name

    def is_discounted(self):
        return self.original_price and self.original_price > self.price

    def discount_percentage(self):
        if self.is_discounted():
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')  # many-to-many via intermediate model
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderProduct(models.Model):  # intermediate table to store quantity with product
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order #{self.order.id})"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
