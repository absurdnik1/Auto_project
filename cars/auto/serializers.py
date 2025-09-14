from rest_framework import serializers
from .models import Auto


class AutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auto
        fields = ['title', 'slug', 'mileage', 'price', 'category', 'engine', 'transmission', 'color', 'weight',
              'drive', 'trunk_capacity', 'wheel_size', 'numbers_of_seats',
              'safety_rating', 'fuel_tank_capacity', 'fuel_type', 'production_year']