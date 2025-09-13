from datetime import datetime

from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator, MaxValueValidator, \
    MinValueValidator
from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
# Create your models here.

class Engine(models.Model):
    title = models.CharField(max_length=255, verbose_name='Engine name')
    power = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Engine'
        verbose_name_plural = 'Engines'


class Transmission(models.Model):
    transmission_choices = (('0', 'automatic'),('1', 'manual'))
    title = models.CharField(default="Unknown", max_length=255, verbose_name='Transmission title')
    transmission_type = models.CharField(max_length=100, choices=transmission_choices, default=transmission_choices[0],
                                         verbose_name='Transmission type')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Transmission'
        verbose_name_plural = 'Transmissions'


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Category title', null=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug',
                            validators=[
                                MinLengthValidator(5, message="Min 5 symbols"),
                                MaxLengthValidator(30, message="Max 30 symbols")
                            ])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


def current_year():
    return datetime.now().year

def max_value_current_year(value):
    return MaxValueValidator(current_year(), value)

class Auto(models.Model):
    drive_choices = (('0','front wheel drive'),
                     ('1','rear wheel drive'),
                     ('2', 'four-wheel drive'))
    safety_ratings = ((1, 'one'),
                      (2, 'two'),
                      (3, 'three'),
                      (4,'four'),
                      (5, 'five'),
                      (6, 'six'),
                      (7, 'seven'),
                      (8, 'eight'),
                      (9, 'nine'),
                      (10, 'ten'))
    fuel_types = (('бензин', 'gasoline'),
                  ('дизель', 'diesel'),
                  ('водород', 'hydrogen'),
                  ('электро', 'electro'))
    today_year = datetime.now().year
    title = models.CharField(max_length=255, verbose_name='Title auto')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug',
                            validators=[
                                MinLengthValidator(5, message="Min 5 symbols"),
                                MaxLengthValidator(30, message="Max 30 symbols")
                            ])
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='autos',
                                 verbose_name='Category')
    engine = models.ForeignKey('Engine', on_delete=models.CASCADE, related_name='autos',
                               verbose_name='Engine')
    transmission = models.ForeignKey('Transmission', on_delete=models.CASCADE, related_name='autos',
                                     verbose_name='Transmission')
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите цвет в формате HEX (например, #FFFFFF).'
            )
        ],
        default='#000000',
        verbose_name='Color'
    )
    weight = models.IntegerField(default=1000, verbose_name='Weight')
    drive = models.CharField(max_length=100, choices=drive_choices, default=drive_choices[0], verbose_name='drive')
    trunk_capacity = models.IntegerField(default=300, verbose_name='Trunk_capacity', validators=[
        MaxValueValidator(1000, message='Max 1000 kg'),
        MinValueValidator(100, message='Min 100 kg')
    ])
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True, verbose_name='Auto image')
    wheel_size = models.IntegerField(default=15, validators=[
        MinValueValidator(10, message='Min 10R'),
        MaxValueValidator(25, message='Max 25R')],
        verbose_name='Wheel size')
    numbers_of_seats = models.IntegerField(default=5, validators=[
        MinValueValidator(2, 'Min 2 seats'),
        MaxValueValidator(9, 'Max 9 seats')
    ],
        verbose_name='Numbers of seats')
    safety_rating = models.IntegerField(choices=safety_ratings, default=safety_ratings[0], verbose_name='Safety_rating')
    fuel_tank_capacity = models.IntegerField(default=50, validators=[
        MinValueValidator(5, message='Min 5 liters'),
        MaxValueValidator(10000, message='Max 10000 liters')
    ])
    fuel_type = models.CharField(max_length=100, choices=fuel_types, default=fuel_types[0])
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Creation time')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Update time')
    production_year = models.IntegerField(default=2000, validators=[MinValueValidator(1960), max_value_current_year])
    price = models.IntegerField(default=0, verbose_name="Price")
    mileage = models.IntegerField(default=0, verbose_name="Mileage")
    url = models.URLField(max_length=500, null=True, blank=True, verbose_name="Drom URL")


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Auto'
        verbose_name_plural = 'Autos'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'], name='time_create_indx')
        ]

    def get_absolute_url(self):
        return reverse('main_page')



class Truck(Auto):
    load_capacity = models.IntegerField(validators=[
        MaxValueValidator(300000, message='Max 300000 kg')
    ])

    class Meta:
        verbose_name = 'Truck',
        verbose_name_plural = 'Trucks'
        ordering = ['-time_create']


class Review(models.Model):
    text = models.TextField(max_length=1000, verbose_name='Review text')
    auto = models.ForeignKey('Auto', on_delete=models.CASCADE, related_name='reviews', verbose_name='Auto')
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Score')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Publication date')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='User')

    def __str__(self):
        return f'{self.user.username} - {self.auto.title}'

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='User')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments', verbose_name='Review')
    text = models.TextField(max_length=200, verbose_name='Comment text')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

