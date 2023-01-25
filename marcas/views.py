from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from marcas.models import Marca
from marcas.forms import MarcaForm


class MarcaListView(LoginRequiredMixin, ListView):
    model = Marca
    template_name = 'listMarca.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Marcas'
        context['entity'] = 'Marcas'
        context['create_url'] = reverse_lazy('agregar_marca')
        context['list_url'] = reverse_lazy('lista_marca')
        return context

class MarcaCreateView(LoginRequiredMixin, CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'createMarca.html'
    success_url = reverse_lazy('lista_marca')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Una Marca'
        context['entity'] = 'Marcas'
        context['list_url'] = reverse_lazy('lista_marca')
        return context

class MarcaUpdateView(LoginRequiredMixin, UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'createMarca.html'
    success_url = reverse_lazy('lista_marca')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de Categoria'
        context['entity'] = 'Marcas'
        context['list_url'] = reverse_lazy('lista_marca')
        return context

class MarcaDeleteView(LoginRequiredMixin, DeleteView):
    model = Marca
    template_name = 'deleteMarca.html'
    success_url = reverse_lazy('lista_marca')

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
        context['title'] = 'Eliminacion de Marca'
        context['list_url'] = reverse_lazy('lista_marca')
        context['entity'] = 'Marcas'
        return context