from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from auto.models import Auto, Category


# Create your views here.


class AddAuto(LoginRequiredMixin, CreateView):
    model = Auto
    template_name = 'auto/add_auto.html'
    fields = ['title', 'slug', 'category', 'engine', 'transmission', 'color', 'weight',
              'drive', 'trunk_capacity', 'image', 'wheel_size', 'numbers_of_seats',
              'safety_rating', 'fuel_tank_capacity', 'fuel_type']
    extra_context = {'title_page': 'Add Auto'}


class UpdateAuto(LoginRequiredMixin, UpdateView):
    model = Auto
    fields = ['title', 'category', 'engine', 'transmission', 'color', 'weight',
              'drive', 'trunk_capacity', 'image', 'wheel_size', 'numbers_of_seats',
              'safety_rating', 'fuel_tank_capacity', 'fuel_type']
    template_name = 'auto/update_auto.html'
    success_url = reverse_lazy('main_page')
    title_page = 'Edit Auto'
    slug_url_kwarg = 'auto_slug'


class DeleteAuto(LoginRequiredMixin, DeleteView):
    model = Auto
    template_name = 'auto/delete_auto.html'
    success_url = 'auto/delete_auto.html'
    title_page = 'Delete Auto'
    slug_url_kwarg = 'auto_slug'


class DetailAuto(DetailView):
    template_name = 'auto/detail_auto.html'
    slug_url_kwarg = 'auto_slug'
    context_object_name = 'auto'

    def get_object(self, queryset=None):
        return get_object_or_404(Auto, slug=self.kwargs[self.slug_url_kwarg])


class MainPage(LoginRequiredMixin, ListView):
    model = Auto
    template_name = 'auto/main_page.html'
    context_object_name = 'autos'
    title_page = 'Main page'
    paginate_by = 10

    def get_queryset(self):
        return Auto.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        return context


class CategoryAuto(ListView):
    model = Auto
    template_name = 'auto/category.html'
    context_object_name = 'autos'
    paginate_by = 5

    def get_queryset(self):
        return Auto.objects.filter(category__slug=self.kwargs['cat_slug'])



def about(request):
    return render(request, 'auto/about_site.html')




