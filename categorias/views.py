from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from categorias.models import Categoria
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from categorias.forms import CategoriaForm


class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'listCategoria.html'

    def get_queryset(self):
        usuario = self.request.user
        compania_id = usuario.sedePerteneciente.companiaPerteneciente.id
        self.categorias = Categoria.objects.filter(compañiaAsociada=compania_id)
        return self.categorias

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Categorías'
        context['entity'] = 'Categorias'
        context['create_url'] = reverse_lazy('agregar_categoria')
        context['list_url'] = reverse_lazy('lista_categoria')
        return context

class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'createCategoria.html'
    success_url = reverse_lazy('lista_categoria')

    def form_valid(self, form):
        usuario = self.request.user
        compania_id = usuario.sedePerteneciente.companiaPerteneciente.id
        form.instance.compañiaAsociada_id = compania_id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Una Categoria'
        context['list_url'] = reverse_lazy('lista_categoria')
        context['entity'] = 'Categorias'
        return context

class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'createCategoria.html'
    success_url = reverse_lazy('lista_categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de Categoria'
        context['list_url'] = reverse_lazy('lista_categoria')
        context['entity'] = 'Categorias'
        return context

class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'deleteCategoria.html'
    success_url = reverse_lazy('lista_categoria')

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
        context['title'] = 'Eliminacion de Categoria'
        context['list_url'] = reverse_lazy('lista_categoria')
        context['entity'] = 'Categorias'
        return context