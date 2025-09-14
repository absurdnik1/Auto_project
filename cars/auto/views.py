import json
from xml.etree.ElementTree import indent

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q, Value, Max
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.views.generic.base import View
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from .serializers import AutoSerializer
from .models import Auto, Category, Review, Comment
from .forms import ReviewForm, CommentForm
from .parse_from_drom import parse_ford_page


# Create your views here.


class AddAuto(LoginRequiredMixin, CreateView):
    model = Auto
    template_name = 'auto/add_auto.html'
    fields = ['title', 'slug', 'mileage', 'price', 'category', 'engine', 'transmission', 'color', 'weight',
              'drive', 'trunk_capacity', 'image', 'wheel_size', 'numbers_of_seats',
              'safety_rating', 'fuel_tank_capacity', 'fuel_type', 'production_year']
    extra_context = {'title_page': 'Add Auto'}


class UpdateAuto(LoginRequiredMixin, UpdateView):
    model = Auto
    fields = ['title', 'slug', 'mileage', 'price', 'category', 'engine', 'transmission', 'color', 'weight',
              'drive', 'trunk_capacity', 'image', 'wheel_size', 'numbers_of_seats',
              'safety_rating', 'fuel_tank_capacity', 'fuel_type', 'production_year']
    template_name = 'auto/update_auto.html'
    success_url = reverse_lazy('main_page')
    title_page = 'Edit Auto'
    slug_url_kwarg = 'auto_slug'


class DeleteAuto(LoginRequiredMixin, DeleteView):
    model = Auto
    template_name = 'auto/delete_auto.html'
    success_url = reverse_lazy('main_page')
    title_page = 'Delete Auto'
    slug_url_kwarg = 'auto_slug'


class DetailAuto(LoginRequiredMixin, DetailView):
    template_name = 'auto/detail_auto.html'
    slug_url_kwarg = 'auto_slug'
    context_object_name = 'auto'

    def get_object(self, queryset=None):
        return get_object_or_404(Auto, slug=self.kwargs[self.slug_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReviewForm()
        return context


from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

#@method_decorator(cache_page(60*5), name='dispatch')
class MainPage(LoginRequiredMixin, ListView):
    model = Auto
    template_name = 'auto/main_page.html'
    context_object_name = 'autos'
    title_page = 'Main page'
    paginate_by = 10

    def get_queryset(self):
        return Auto.objects.all().select_related('transmission', 'engine')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        autos = Auto.objects.select_related('transmission', 'engine')
        context['categories'] = categories

        category_autos = {}
        for cat in categories:
            category_autos[cat.slug] = autos.filter(category=cat)
        context['category_autos'] = category_autos
        context['filtered_by_tank'] = autos.order_by('-trunk_capacity')
        context['safe'] = autos.filter(Q(wheel_size__gte=18) | Q(safety_rating__gte=5)).annotate(
            descr=Value('Safe as fuck'))
        context['4WD'] = autos.filter(Q(drive='2'))
        context['automatic_transmission'] = autos.filter(transmission__transmission_type='0')
        context['manual_transmission'] = autos.filter(transmission__transmission_type='1')
        context['production_year'] = autos.all().order_by('-production_year')
        context['score'] = autos.annotate(max_score=Max('reviews__score')).order_by('-max_score')
        return context



class CategoryAuto(LoginRequiredMixin, ListView):
    model = Auto
    template_name = 'auto/category.html'
    context_object_name = 'autos'
    paginate_by = 5

    def get_queryset(self):
        return Auto.objects.filter(category__slug=self.kwargs['cat_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['cat_slug'])
        return context


class CreateAutoReview(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    template_name = 'auto/detail_auto.html'

    def dispatch(self, request, *args, **kwargs):
        self.auto = get_object_or_404(Auto, slug=self.kwargs['auto_slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.auto = self.auto
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_auto', kwargs={'auto_slug': self.auto.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auto'] = self.auto
        return context


class UpdateReview(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'auto/update_review.html'

    def get_success_url(self):
        return reverse_lazy('detail_auto', kwargs={'auto_slug': self.object.auto.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auto'] = self.object.auto
        context['editing_review'] = self.object
        #context['form'] = ReviewForm()
        return context


class DeleteReview(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'auto/delete_review.html'

    def get_success_url(self):
        return reverse_lazy('detail_auto', kwargs={'auto_slug': self.object.auto.slug})


class CreateComment(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        form.instance.review = review
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_auto', kwargs={'auto_slug': self.object.review.auto.slug})


class UpdateComment(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'auto/update_comment.html'

    def get_success_url(self):
        return reverse_lazy('detail_auto', kwargs={'auto_slug': self.object.review.auto.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auto'] = self.object.review.auto
        context['editing_comment'] = self.object
        return context


class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'auto/delete_comment.html'

    def get_success_url(self):
        return reverse_lazy('detail_auto', kwargs={'auto_slug': self.object.review.auto.slug})


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def car_list(request):
    autos = Auto.objects.select_related('engine', 'transmission')
    serializer = AutoSerializer(autos, many=True)
    json_data = json.dumps(serializer.data, indent=4, ensure_ascii=False)
    # Возвращаем как чистый JSON (без интерфейса DRF)
    return HttpResponse(json_data, content_type='application/json')


def parse_from_drom(request):
    url = "https://auto.drom.ru/lexus/"
    # url2 = "https://auto.drom.ru/mercedes-benz/"
    parse_ford_page(url)
    return redirect('main_page')


def about(request):
    return render(request, 'auto/about_site.html')




