from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from articulos.models import Articulo
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from articulos.forms import ArticuloForm


class ArticuloListView(LoginRequiredMixin,ListView):
    model = Articulo
    template_name = 'listArticulo.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Articulos'
        context['entity'] = 'Articulos'
        context['create_url'] = reverse_lazy('agregar_articulo')
        context['list_url'] = reverse_lazy('lista_articulo')
        return context

class ArticuloCreateView(LoginRequiredMixin,CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'createArticulo.html'
    success_url = reverse_lazy('lista_articulo')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Un Articulo'
        context['list_url'] = reverse_lazy('lista_articulo')
        context['entity'] = 'Articulos'
        return context

class ArticuloUpdateView(LoginRequiredMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'createArticulo.html'
    success_url = reverse_lazy('lista_articulo')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de Articulos'
        context['list_url'] = reverse_lazy('lista_articulo')
        context['entity'] = 'Articulos'
        return context

class ArticuloDeleteView(LoginRequiredMixin, DeleteView):
    model = Articulo
    template_name = 'deleteArticulo.html'
    success_url = reverse_lazy('lista_articulo')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminacion de Articulo'
        context['list_url'] = reverse_lazy('lista_articulo')
        context['entity'] = 'Articulos'
        return context