from django.conf import settings
from django.contrib import admin
from django.urls import path, include


from . import views

urlpatterns = [
    path('', views.MainPage.as_view(), name='main_page'),
    path('category/<slug:cat_slug>/', views.CategoryAuto.as_view(), name='category_auto'),
    path('create_auto/', views.AddAuto.as_view(), name='create_page'),
    path('edit_auto/<slug:auto_slug>/', views.UpdateAuto.as_view(), name='update_auto'),
    path('delete_auto/<slug:auto_slug>/', views.DeleteAuto.as_view(), name='delete_auto'),
    path('detail_auto/<slug:auto_slug>/', views.DetailAuto.as_view(), name='detail_auto'),
    path('detail_auto/<slug:auto_slug>/create_review/', views.CreateAutoReview.as_view(), name='create_review'),
    path('review/<int:pk>/update/', views.UpdateReview.as_view(), name='update_review'),
    path('review/<int:pk>/delete/', views.DeleteReview.as_view(), name='delete_review'),
    path('review/<int:review_pk>/comment/', views.CreateComment.as_view(), name='create_comment'),
    path('comment/<int:pk>/update/', views.UpdateComment.as_view(), name='update_comment'),
    path('comment/<int:pk>/delete/', views.DeleteComment.as_view(), name='delete_comment'),
    path('about', views.about, name='about_site'),
    path('parse_auto', views.parse_from_drom, name="parse_from_drom"),
    path('api/cars/', views.car_list, name='car_list'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns