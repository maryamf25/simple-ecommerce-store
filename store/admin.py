from django.contrib import admin
from .models import Product, Order, CartItem, OrderProduct, Tag

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(OrderProduct)
admin.site.register(Tag)
