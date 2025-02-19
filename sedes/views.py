from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from sedes.forms import SedeForm
from sedes.models import Sede


class SedeCreateView(LoginRequiredMixin,CreateView):
    model = Sede
    form_class = SedeForm
    template_name = 'createSede.html'
    success_url = reverse_lazy('lista_compañia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Una Sede'
        context['list_url'] = reverse_lazy('lista_compañia')
        context['entity'] = 'Sede'
        return context

    def form_valid(self, form):
        usuario = self.request.user
        compania_id = usuario.sedePerteneciente.companiaPerteneciente.id
        form.instance.companiaPerteneciente_id = compania_id
        return super().form_valid(form)