import logging
import json
import os
from decimal import Decimal

from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail.backends import console
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.functional import empty
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from unicodedata import decimal

from compañias.models import Compañia
from sedes.models import Sede
from sociosMinoristas.models import SocioMinorista
from user.models import User, HistoricosComisiones
from ventas.models import Venta, DetVenta
from ventas.forms import VentaForm
from articulos.models import Articulo
from weasyprint import HTML, CSS

from servimotos import settings


class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'listVenta.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Venta.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetVenta.objects.filter(venta_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['create_url'] = reverse_lazy('agregar_venta')
        context['list_url'] = reverse_lazy('lista_venta')
        context['entity'] = 'Ventas'
        return context


class VentaCreateView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'createVenta.html'
    success_url = reverse_lazy('lista_venta')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # Pasar el request al formulario
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = self.search_products(request)
            elif action == 'search_autocomplete':
                data = self.search_autocomplete(request)
            elif action == 'add':
                data = self.add_venta(request)
            elif action == 'check_stock':
                data = self.check_stock(request)
            elif action == 'validar_descuento':
                data = self.obtener_porcentaje_descuento(request)
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Articulo.DoesNotExist:
            data['error'] = 'El producto no existe.'
        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data, safe=False)

    def obtener_porcentaje_descuento(self, request):
        data = {}
        cliente_id = request.POST.get('cliente_id')
        try:
            cliente = SocioMinorista.objects.get(id=cliente_id)
            data['porcentajeDescuento'] = cliente.porcentajeDescuento;
            return data
        except SocioMinorista.DoesNotExist:
            data['error'] = "Cliente no encontrado"
            return data

    def search_autocomplete(self, request):
        data = []
        term = request.POST['term'].strip()
        parts = term.split(',')
        nombre = parts[0].strip() if len(parts) > 0 else ""
        categoria = parts[1].strip() if len(parts) > 1 else ""
        products = Articulo.objects.filter(stock__gt=0, sede_id=self.request.user.sedePerteneciente.id)

        if nombre:
            products = products.filter(nombre__icontains=nombre)
        if categoria:
            products = products.filter(categoria__nombre__icontains=categoria)

        for i in products[0:10]:
            item = i.toJSON()
            item['text'] = f"{i.nombre}, {i.categoria.nombre}"
            data.append(item)
        return data

    def search_products(self, request):
        data = []
        termino = request.POST['term']
        prods = Articulo.objects.filter(nombre__icontains=termino)[0:10]
        for i in prods:
            item = i.toJSON()
            item['value'] = i.nombre
            data.append(item)
        return data

    def add_venta(self, request):
        data = {}
        self.usuario = self.request.user.id
        try:
            with transaction.atomic():
                vents = json.loads(request.POST['vents'])
                productos = vents['products']

                # Validar el stock de todos los productos antes de continuar
                for product_data in productos:
                    producto_id = product_data['id']
                    cantidad = int(product_data['cant'])
                    self.validar_stock(producto_id, cantidad)
                cliente_id = vents['cliente']
                cliente = SocioMinorista.objects.get(id=cliente_id)
                # Si la validación pasa, proceder con la venta
                venta = Venta()
                venta.date_joined = vents['date_joined']
                venta.use_id = self.usuario
                venta.cliente = cliente
                venta.descuento = float(vents['descuento'])
                venta.subtotal = float(vents['subtotal'])
                venta.iva = float(vents['iva'])
                venta.total = float(vents['total'])
                gananciaAntesDeComision = float(vents['ganancia'])
                venta.ganancia = gananciaAntesDeComision - self.update_user_comision(request, venta.total)
                venta.save()

                self.update_sede_ventas_totales(request, venta.total)
                self.update_compania_ventas_totales(request, venta.total)

                for product_data in productos:
                    self.add_detalle_venta(venta, product_data)

        except ValidationError as e:
            data['error'] = str(e)
        except Exception as e:
            data['error'] = str(e)

        return data

    def validar_stock(self, producto_id, cantidad):
        """
        Valida el stock del producto y bloquea el registro para evitar concurrencia.
        """
        with transaction.atomic():
            producto = Articulo.objects.select_for_update().get(pk=producto_id)
            if producto.stock < cantidad:
                raise ValidationError(f'Solo quedan {producto.stock} unidades disponibles de {producto.nombre}')
            producto.stock = F('stock') - cantidad
            producto.save()

    def add_detalle_venta(self, venta, product_data):

        det = DetVenta()
        det.venta_id = venta.id
        det.articulo_id = product_data['id']
        det.cantidad = int(product_data['cant'])
        det.precio = float(product_data['precioFinal'])
        det.subtotal = float(product_data['subtotal'])
        det.save()

    def update_user_comision(self, request, total):
        usuario = User.objects.get(pk=request.user.id)
        comision = total * float(usuario.porcentajeComision) / 100
        print(comision)

        fecha_actual = timezone.now()
        mes_actual = fecha_actual.month
        anio_actual = fecha_actual.year

        historico = HistoricosComisiones.objects.filter(
            fecha__year=anio_actual,
            fecha__month=mes_actual,
            usuario=usuario
        ).first()

        if historico:
            historico.comisionAcumulada += Decimal(comision)
            historico.save()
        else:
            HistoricosComisiones.objects.create(
                fecha=fecha_actual.date(),  # Se guarda la fecha actual
                comisionAcumulada= Decimal(comision),
                usuario=usuario
            )

        return comision

    def update_sede_ventas_totales(self, request, total):
        sede_actualizada = Sede.objects.get(id=request.user.sedePerteneciente.id)
        sede_actualizada.ventasTotales += total
        sede_actualizada.save()

    def update_compania_ventas_totales(self, request, total):
        compania_actualizada = Compañia.objects.get(id=request.user.sedePerteneciente.companiaPerteneciente.id)
        compania_actualizada.ventasTotales += total
        compania_actualizada.save()

    def check_stock(self, request):
        data = {}
        producto_id = request.POST.get('id')
        cantidad = int(request.POST.get('cantidad', 0))
        producto = Articulo.objects.get(pk=producto_id)
        if producto.stock >= cantidad:
            data['status'] = 'ok'
        else:
            data['status'] = 'error'
            data['message'] = f'Solo quedan {producto.stock} unidades disponibles de {producto.nombre}'
            data['cantidadDisponible'] = producto.stock
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context


class VentaDeleteView(LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = 'deleteVenta.html'
    success_url = reverse_lazy('lista_venta')
    url_redirect = success_url

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
        context['title'] = 'Eliminación de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        return context


class VentaUpdateView(LoginRequiredMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'createVenta.html'
    success_url = reverse_lazy('lista_venta')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        self.usuario = self.request.user.id
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                termino = request.POST['term']
                prods = Articulo.objects.filter(nombre__icontains=termino)[0:10]
                for i in prods:
                    item = i.toJSON()
                    item['value'] = i.nombre
                    data.append(item)
            elif action == 'search_autocomplete':
                data = []
                term = request.POST['term'].strip()
                data.append({'id': term, 'text': term})
                products = Articulo.objects.filter(nombre__icontains=term, stock__gt=0)
                for i in products[0:10]:
                    item = i.toJSON()
                    item['text'] = i.nombre
                    data.append(item)
            elif action == 'edit':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    # venta = Venta.objects.get(pk=self.get_object().id)
                    cliente_id = vents['cliente']
                    cliente = SocioMinorista.objects.get(id=cliente_id)
                    venta = self.get_object()
                    venta.date_joined = vents['date_joined']
                    venta.use_id = self.usuario
                    venta.cliente = cliente
                    venta.descuento = float(vents['descuento'])
                    venta.subtotal = float(vents['subtotal'])
                    venta.iva = float(vents['iva'])
                    venta.total = float(vents['total'])
                    venta.save()
                    venta.detventa_set.all().delete()
                    for i in vents['products']:
                        det = DetVenta()
                        det.venta_id = venta.id
                        det.articulo_id = i['id']
                        det.cantidad = int(i['cant'])
                        det.precio = float(i['precioFinal'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                        det.articulo.stock -= (int(i['cant']) - int(i['cantidadIni']))
                        det.articulo.save()
                    if vents['articulosEliminados'] != []:
                        for i in vents['articulosEliminados']:
                            articulo = Articulo.objects.get(pk=i['id'])
                            articulo.stock += int(i['cantidadIni'])
                            articulo.save()

            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_details_product(self):
        data = []
        try:
            for i in DetVenta.objects.filter(venta_id=self.get_object().id):
                item = i.articulo.toJSON()
                item['cant'] = i.cantidad
                data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.get_details_product())
        return context


class VentaInvoicePdfView(View):

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('invoice.html')
            context = {
                'venta': Venta.objects.get(pk=self.kwargs['pk']),
                'comp': {'nombre': 'SERVIMOTOS DEL CAMINO S.A.', 'runt': '80731044',
                         'direccion': 'Av. Boyaca # 51b - 39 SUR BOGOTA, COLOMBIA',
                         'correo': 'servimotos_del_camino@gmail.com', 'celular': '3112932799'},
                'icon': '{}{}'.format(settings.MEDIA_URL, 'logo.png')
            }
            html = template.render(context)
            css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
            pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('lista_venta'))
