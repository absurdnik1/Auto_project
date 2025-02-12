from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainPage.as_view(), name='main_page'),
    path('category/<slug:cat_slug>/', views.CategoryAuto.as_view(), name='category_auto'),
    path('create_auto/', views.AddAuto.as_view(), name='create_page'),
    path('edit_auto/<slug:auto_slug>/', views.UpdateAuto.as_view(), name='update_auto'),
    path('delete_auto/<slug:auto_slug>/', views.DeleteAuto.as_view(), name='delete_auto'),
    path('detail_auto/<slug:auto_slug>/', views.DetailAuto.as_view(), name='detail_auto'),
    path('about', views.about, name='about_site'),
]
