from django.contrib import admin
from django.conf import settings
from .models import AddProduct, Carts, Contact, Signup, Transaction, Wishlists

admin.site.register(Contact)
admin.site.register(Signup)
admin.site.register(AddProduct)
admin.site.register(Wishlists)
admin.site.register(Carts)
admin.site.register(Transaction)