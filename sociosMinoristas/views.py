from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from sociosMinoristas.forms import SocioForm
from sociosMinoristas.models import SocioMinorista


class SocioListView(LoginRequiredMixin,ListView):
    model = SocioMinorista
    template_name = 'listSocios.html'

    def get_queryset(self):
        usuario = self.request.user
        compania_id = usuario.sedePerteneciente.companiaPerteneciente.id
        return SocioMinorista.objects.filter(compañiasAsociadas__id=compania_id).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Socios Minoristas'
        context['entity'] = 'SociosMinoristas'
        context['create_url'] = reverse_lazy('agregar_socio')
        context['list_url'] = reverse_lazy('lista_socios')
        return context

class SocioCreateView(LoginRequiredMixin,CreateView):
    model = SocioMinorista
    form_class = SocioForm
    template_name = 'createSocio.html'
    success_url = reverse_lazy('lista_socios')

    def form_valid(self, form):
        usuario = self.request.user
        compania = usuario.sedePerteneciente.companiaPerteneciente
        socio = form.save(commit=False)
        socio.save()
        form.save_m2m()
        socio.compañiasAsociadas.add(compania)
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Un Socio Minorista'
        context['list_url'] = reverse_lazy('lista_socios')
        context['entity'] = 'SociosMinoristas'
        return context

class SocioUpdateView(LoginRequiredMixin, UpdateView):
    model = SocioMinorista
    form_class = SocioForm
    template_name = 'createSocio.html'
    success_url = reverse_lazy('lista_socios')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de Socios Minoristas'
        context['list_url'] = reverse_lazy('lista_socios')
        context['entity'] = 'SociosMinoristas'
        return context

class SocioDeleteView(LoginRequiredMixin, DeleteView):
    model = SocioMinorista
    template_name = 'deleteSocio.html'
    success_url = reverse_lazy('lista_socios')

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
        context['title'] = 'Eliminacion de Socios Minoritarios'
        context['list_url'] = reverse_lazy('lista_socios')
        context['entity'] = 'SociosMinoristas'
        return context