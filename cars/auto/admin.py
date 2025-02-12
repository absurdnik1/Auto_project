from django.contrib import admin
from .models import Auto, Truck, Category, Engine, Transmission

# Register your models here.

admin.site.register(Auto)
admin.site.register(Truck)
admin.site.register(Category)
admin.site.register(Engine)
admin.site.register(Transmission)