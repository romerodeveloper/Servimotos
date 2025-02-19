
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone

from articulos.models import Articulo, Historico_Precios
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from articulos.forms import ArticuloForm


class ArticuloListView(LoginRequiredMixin,ListView):
    model = Articulo
    template_name = 'listArticulo.html'

    def get_queryset(self):
        usuario = self.request.user
        sede_id = usuario.sedePerteneciente.id
        return Articulo.objects.filter(sede_id=sede_id).prefetch_related('historico_precios_set').distinct()

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        usuario = self.request.user
        sede_id = usuario.sedePerteneciente.id
        form.instance.sede_id = sede_id

        response = super().form_valid(form)

        Historico_Precios.objects.create(
            fecha=timezone.now().date(),
            precio_iva_incluido=form.instance.precioCosto+form.instance.iva,
            articulo=form.instance
        )

        return response

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        articulo_anterior = Articulo.objects.get(pk=self.object.pk)
        precio_anterior = articulo_anterior.precioCosto + articulo_anterior.iva

        response = super().form_valid(form)

        articulo_actualizado = self.object
        precio_actualizado = articulo_actualizado.precioCosto + articulo_actualizado.iva

        if precio_anterior != precio_actualizado:
            Historico_Precios.objects.create(
                fecha=timezone.now().date(),
                precio_iva_incluido=precio_actualizado,
                articulo=articulo_actualizado
            )

        return response
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