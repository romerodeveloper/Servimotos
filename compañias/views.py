from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from compañias.forms import CompañiaForm
from compañias.models import Compañia
from sedes.models import Sede


class CompañiaListView(LoginRequiredMixin,ListView):
    model = Compañia
    template_name = 'listCompañia.html'

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'sedePerteneciente') and usuario.sedePerteneciente:
            compania_id = usuario.sedePerteneciente.companiaPerteneciente.id
            self.sedes = Sede.objects.filter(companiaPerteneciente=compania_id).all() # Asumiendo que 'sedes' es la relación de sedes en Compañia
            return Compañia.objects.filter(id=compania_id)
        return Compañia.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sedes'] = self.sedes
        context['title'] = 'Detalle de compañia'
        context['entity'] = 'Compañias'
        context['create_url'] = reverse_lazy('agregar_compañia')
        context['list_url'] = reverse_lazy('lista_compañia')
        return context

class CompañiaCreateView(LoginRequiredMixin,CreateView):
    model = Compañia
    form_class = CompañiaForm
    template_name = 'createCompañia.html'
    success_url = reverse_lazy('lista_compañia')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Una Compañia'
        context['list_url'] = reverse_lazy('lista_compañia')
        context['entity'] = 'Compañias'
        return context

class CompañiaUpdateView(LoginRequiredMixin, UpdateView):
    model = Compañia
    form_class = CompañiaForm
    template_name = 'createCompañia.html'
    success_url = reverse_lazy('lista_compañia')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de Compañia'
        context['list_url'] = reverse_lazy('lista_compañia')
        context['entity'] = 'Compañias'
        return context

class CompañiaDeleteView(LoginRequiredMixin, DeleteView):
    model = Compañia
    template_name = 'deleteCompañia.html'
    success_url = reverse_lazy('lista_compañia')

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
        context['title'] = 'Eliminacion de Compañia'
        context['list_url'] = reverse_lazy('lista_compañia')
        context['entity'] = 'Compañias'
        return context
