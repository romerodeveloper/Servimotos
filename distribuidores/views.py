from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from distribuidores.forms import DistribuidorForm

from distribuidores.models import Distribuidor


class DistribuidorListView(LoginRequiredMixin,ListView):
    model = Distribuidor
    template_name = 'listDistribuidor.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Distribuidores'
        context['entity'] = 'Distribuidores'
        context['create_url'] = reverse_lazy('agregar_distribuidor')
        context['list_url'] = reverse_lazy('lista_distribuidor')
        return context

class DistribuidorCreateView(LoginRequiredMixin,CreateView):
    model = Distribuidor
    form_class = DistribuidorForm
    template_name = 'createDistribuidor.html'
    success_url = reverse_lazy('lista_distribuidor')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Un Distribuidor'
        context['list_url'] = reverse_lazy('lista_distribuidor')
        context['entity'] = 'Distribuidores'
        return context

class DistribuidorUpdateView(LoginRequiredMixin, UpdateView):
    model = Distribuidor
    form_class = DistribuidorForm
    template_name = 'createDistribuidor.html'
    success_url = reverse_lazy('lista_distribuidor')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de Distribuidor'
        context['list_url'] = reverse_lazy('lista_distribuidor')
        context['entity'] = 'Distribuidores'
        return context

class DistribuidorDeleteView(LoginRequiredMixin, DeleteView):
    model = Distribuidor
    template_name = 'deleteDistribuidor.html'
    success_url = reverse_lazy('lista_distribuidor')

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
        context['title'] = 'Eliminacion de Distribuidor'
        context['list_url'] = reverse_lazy('lista_distribuidor')
        context['entity'] = 'Distribuidores'
        return context