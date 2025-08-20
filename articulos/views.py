from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from unicodedata import decimal

from articulos.models import Articulo, Historico_Precios
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from articulos.forms import ArticuloForm
from compañias.models import Compañia
from distribuidores.models import Distribuidor
import json

from sedes.models import Sede


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

class ArticuloCreateView(LoginRequiredMixin, CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'createArticulo.html'
    success_url = reverse_lazy('lista_articulo')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'add':
            return self.add_articulo(request)
        elif action == 'search':
            return self.search_distribuidor(request)
        else:
            return JsonResponse({'success': False, 'error': 'Acción no válida'})

    def add_articulo(self, request):
        articulo_data = json.loads(request.POST.get('articulo'))
        articulo = self.create_articulo(articulo_data)

        try:
            with transaction.atomic():
                self.actualizar_compras_totales(articulo)
                self.crear_historico_precios(articulo)

                return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def create_articulo(self, articulo_data):
        articulo = Articulo(
            nombre=articulo_data['nombre'],
            codigoOriginal=articulo_data['codigoOriginal'],
            distribuidor_id=articulo_data['distribuidor'],
            descuentoAntesDeIva=articulo_data['descuentoAntesDeIva'],
            precioCosto=articulo_data['precioCosto'],
            tasaGanacia=articulo_data['tasaGanacia'],
            iva=articulo_data['iva'],
            precioFinal=articulo_data['precioFinal'],
            stock=articulo_data['stock'],
            categoria_id=articulo_data['categoria'],
            marca_id=articulo_data['marca'],
            sede_id=self.request.user.sedePerteneciente.id
        )
        articulo.save()
        return articulo

    def actualizar_compras_totales(self, articulo):
        valor_compra = (Decimal(articulo.precioCosto) + Decimal(articulo.iva)) * Decimal(articulo.stock)

        sede_actualizada = Sede.objects.get(id=self.request.user.sedePerteneciente.id)
        sede_actualizada.comprasTotales += valor_compra
        sede_actualizada.save()

        compania_actualizada = Compañia.objects.get(id=self.request.user.sedePerteneciente.companiaPerteneciente.id)
        compania_actualizada.comprasTotales += valor_compra
        compania_actualizada.save()

    def crear_historico_precios(self, articulo):
        Historico_Precios.objects.create(
            fecha=timezone.now().date(),
            precioIvaIncluido=Decimal(articulo.precioCosto) + Decimal(articulo.iva),
            articulo=articulo
        )

    def search_distribuidor(self, request):
        distribuidor_id = request.POST.get('distribuidor')
        modelo_factura = self.get_distribuidor_modelo_factura(distribuidor_id)
        return JsonResponse({'modeloFactura': modelo_factura})

    def get_distribuidor_modelo_factura(self, distribuidor_id):
        distribuidor = Distribuidor.objects.filter(id=distribuidor_id).first()
        return distribuidor.modeloFactura

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Un Articulo'
        context['list_url'] = reverse_lazy('lista_articulo')
        context['entity'] = 'Articulos'
        context['action'] = 'add'
        return context

class ArticuloUpdateView(LoginRequiredMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'createArticulo.html'
    success_url = reverse_lazy('lista_articulo')

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'edit':
            return self.handle_edit(request)
        elif action == 'search':
            return self.handle_search(request)
        else:
            return JsonResponse({'success': False, 'error': 'Acción no válida'})

    def handle_edit(self, request):
        articulo_prev = self.get_object()
        articulo_data = json.loads(request.POST.get('articulo'))

        self.update_articulo(request, articulo_prev, articulo_data)
        articulo_prev.save()
        self.update_historico_precios(articulo_prev)

        return JsonResponse({'success': True})

    def handle_search(self, request):
        distribuidor_id = request.POST.get('distribuidor')
        modelo_factura = self.get_distribuidor_modelo_factura(distribuidor_id)
        return JsonResponse({'modeloFactura': modelo_factura})

    def update_articulo(self, request, articulo, articulo_data):
        compraPrevia = self.calcular_compra(articulo.precioCosto, articulo.iva, articulo.stock)
        compraNueva = self.calcular_compra(articulo_data['precioCosto'], articulo_data['iva'], articulo_data['stock'])

        articulo.nombre = articulo_data['nombre']
        articulo.codigoOriginal = articulo_data['codigoOriginal']
        articulo.distribuidor_id = articulo_data['distribuidor']
        articulo.descuentoAntesDeIva = articulo_data['descuentoAntesDeIva']
        articulo.precioCosto = articulo_data['precioCosto']
        articulo.tasaGanacia = articulo_data['tasaGanacia']
        articulo.iva = articulo_data['iva']
        articulo.precioFinal = articulo_data['precioFinal']
        articulo.stock = articulo_data['stock']
        articulo.categoria_id = articulo_data['categoria']
        articulo.marca_id = articulo_data['marca']

        try:
            sede_actualizada = Sede.objects.get(id=request.user.sedePerteneciente.id)
            compania_actualizada = Compañia.objects.get(id=request.user.sedePerteneciente.companiaPerteneciente.id)
        except ObjectDoesNotExist:
            return {"error": "Sede o Compañía no encontrada"}

        sede_actualizada.comprasTotales -= compraPrevia
        compania_actualizada.comprasTotales -= compraPrevia
        sede_actualizada.comprasTotales += compraNueva
        compania_actualizada.comprasTotales += compraNueva

        sede_actualizada.save()
        compania_actualizada.save()

    def calcular_compra(self, precio_costo, iva, stock):
        return (Decimal(precio_costo) + Decimal(iva)) * Decimal(stock)

    def update_historico_precios(self, articulo):
        precio_iva_incluido = Decimal(articulo.precioCosto) + Decimal(articulo.iva)
        today = timezone.now().date()
        historico = Historico_Precios.objects.filter(fecha=today, articulo=articulo).first()
        if historico:
            historico.precioIvaIncluido = precio_iva_incluido
            historico.save()
        else:
            Historico_Precios.objects.create(
                fecha=today,
                precioIvaIncluido=precio_iva_incluido,
                articulo=articulo
            )

    def get_distribuidor_modelo_factura(self, distribuidor_id):
        distribuidor = Distribuidor.objects.filter(id=distribuidor_id).first()
        if distribuidor:
            return distribuidor.modeloFactura
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Artículos'
        context['list_url'] = reverse_lazy('lista_articulo')
        context['entity'] = 'Artículos'
        context['action'] = 'edit'
        return context

class ArticuloDeleteView(LoginRequiredMixin, DeleteView):
    model = Articulo
    template_name = 'deleteArticulo.html'
    success_url = reverse_lazy('lista_articulo')

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def calcular_compra(self, precio_costo, iva, stock):
        return (Decimal(precio_costo) + Decimal(iva)) * Decimal(stock)

    def actualizar_compras(self, articulo, user):
        try:
            compraPrevia = self.calcular_compra(articulo.precioCosto, articulo.iva, articulo.stock)
            sede_actualizada = Sede.objects.get(id=user.sedePerteneciente.id)
            compania_actualizada = Compañia.objects.get(id=user.sedePerteneciente.companiaPerteneciente.id)
            sede_actualizada.comprasTotales -= compraPrevia
            compania_actualizada.comprasTotales -= compraPrevia
            sede_actualizada.save()
            compania_actualizada.save()

        except ObjectDoesNotExist:
            return {"error": "Sede o Compañía no encontrada"}
        except Exception as e:
            return {"error": str(e)}

        return None

    def post(self, request, *args, **kwargs):
        response_data = {}
        try:
            articulo = self.get_object()
            with transaction.atomic():
                error = self.actualizar_compras(articulo, request.user)
                if error:
                    return JsonResponse(error, status=400)
                articulo.delete()

            response_data['message'] = "Artículo eliminado correctamente"
            return JsonResponse(response_data, status=200)

        except Exception as e:
            response_data['error'] = str(e)
            return JsonResponse(response_data, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminacion de Articulo'
        context['list_url'] = reverse_lazy('lista_articulo')
        context['entity'] = 'Articulos'
        return context