import logging
import json
import os
import traceback
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist
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

import user
from compañias.models import Compañia
from sedes.models import Sede
from sociosMinoristas.models import SocioMinorista
from user.models import User, HistoricosComisiones
from ventas.models import Venta, DetVenta
from ventas.forms import VentaForm
from articulos.models import Articulo
from weasyprint import HTML, CSS

from servimotos import settings
from ventas.utils import VentaUtils
import traceback



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
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = VentaUtils.search_autocomplete(request)
            elif action == 'add':
                data = self.add_venta(request)
            elif action == 'check_stock':
                data = VentaUtils.check_stock(request)
            elif action == 'validar_descuento':
                data = self.obtener_datos_socio(request)
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Articulo.DoesNotExist:
            data['error'] = 'El producto no existe.'
        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data, safe=False)

    def obtener_datos_socio(self, request):
        data = {}
        cliente_id = request.POST.get('cliente_id')
        try:
            cliente = SocioMinorista.objects.get(id=cliente_id)
            data['porcentajeDescuento'] = cliente.porcentajeDescuento
            data['estadoPrestamo'] = cliente.prestamo
            data['montoMaximoPendiente'] = cliente.montoMaximoPendiente
            return data
        except SocioMinorista.DoesNotExist:
            data['error'] = "Cliente no encontrado"
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
                for product_data in productos:
                    producto_id = product_data['id']
                    cantidad = int(product_data['cant'])
                    VentaUtils.validar_stock(producto_id, cantidad)
                cliente_id = vents['cliente']
                cliente = SocioMinorista.objects.get(id=cliente_id)
                venta = Venta()
                venta.date_joined = vents['date_joined']
                venta.use_id = self.usuario
                venta.cliente = cliente
                venta.descuento = Decimal(vents['descuento'])
                venta.subtotal = Decimal(vents['subtotal'])
                venta.iva = Decimal(vents['iva'])
                venta.total = Decimal(vents['total'])
                gananciaAntesDeComision = Decimal(vents['ganancia'])
                venta.ganancia = gananciaAntesDeComision - self.update_user_comision(request, venta.total)
                venta.estadoVenta = vents['estadoDeVenta']
                venta.save()

                self.update_socio_ventas_totales(cliente, venta.total, venta.estadoVenta)
                VentaUtils.actualizar_ventas(self.request.user, venta.total)

                for product_data in productos:
                    VentaUtils.add_detalle_venta(venta, product_data)

        except ValidationError as e:
            data['error'] = str(e)
        except Exception as e:
            # Obtenemos el traceback completo
            error_trace = traceback.format_exc()
                    # Preparamos respuesta con detalles del error
            error_response = {
                'error': str(e),
                'detail': "Error en el servidor",
                'trace': error_trace if settings.DEBUG else None  # Solo en desarrollo
            }
            data['error'] = error_response

        return data

    def update_user_comision(self, request, total):
        usuario = User.objects.get(pk=request.user.id)
        comision = total * Decimal(usuario.porcentajeComision) / 100

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

    def update_socio_ventas_totales(self, cliente, total, estado):
        #Agregar opcion de pendiente aqui con un if
        if (estado == Venta.EstadoVenta.PENDIENTE):
            cliente.montoMaximoPendiente -= total
            cliente.montoPendiente += total
        cliente.totalVentas += total
        cliente.save()



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

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', '')
            if action == 'search_products':
                return JsonResponse(VentaUtils.search_autocomplete(request), safe=False)
            elif action == 'edit':
                return self.edit_venta(request, data)
            elif action == 'check_stock':
                return JsonResponse(VentaUtils.check_stock(request, "edit", self.get_object()), safe=False)
            elif action == 'validar_descuento':
                return self.obtener_datos_socio(request)
            else:
                return JsonResponse({'error': 'Acción no válida'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def search_products(self, request, data):
        termino = request.POST.get('term', '').strip()
        productos = Articulo.objects.filter(nombre__icontains=termino)[:10]
        data['productos'] = [{'id': prod.id, 'value': prod.nombre, **prod.toJSON()} for prod in productos]
        return JsonResponse(data, safe=False)


    def edit_venta(self, request, data):
        try:
            usuario_id = self.request.user.id
            venta_data = json.loads(request.POST.get('vents', '{}'))

            with transaction.atomic():
                # Obtener la venta y cliente
                venta = self.get_object()
                cliente = SocioMinorista.objects.get(id=venta_data['cliente'])
                descuentoPrevio = venta.descuento
                estadoPrevio = venta.estadoVenta
                # Actualizar datos de la venta
                venta.date_joined = venta_data['date_joined']
                venta.use_id = usuario_id
                venta.cliente = cliente
                venta.descuento = float(venta_data['descuento'])
                venta.subtotal = float(venta_data['subtotal'])
                venta.iva = float(venta_data['iva'])
                venta.total = float(venta_data['total'])
                gananciaAntesDeComision = Decimal(venta_data['ganancia'])
                venta.save()

                # Restaurar stock de productos eliminados
                suma_devuelta = Decimal(0)
                for detalle in venta.detventa_set.all():
                    articulo = detalle.articulo
                    articulo.stock += detalle.cantidad
                    articulo.save()
                    suma_devuelta += detalle.subtotal

                totalDevolucion = suma_devuelta - descuentoPrevio
                # Restar ventas a la sede, compañía y socio
                VentaUtils.actualizar_ventas(self.request.user, (-totalDevolucion))
                venta.ganancia = gananciaAntesDeComision - self.update_user_comision(usuario_id, totalDevolucion, venta.total)
                self.update_socio_ventas_totales(cliente, totalDevolucion, venta.total, estadoPrevio, venta.estadoVenta)

                # Eliminar detalles previos
                venta.detventa_set.all().delete()

                # Validar stock antes de actualizar
                for producto in venta_data['products']:
                    VentaUtils.validar_stock(producto['id'], int(producto['cant']))
                for producto_data in venta_data['products']:
                    VentaUtils.add_detalle_venta(venta, producto_data)

                # Sumar ventas a la sede y compañía
                VentaUtils.actualizar_ventas(self.request.user, venta.total)

            data['message'] = 'Venta actualizada correctamente'
            return JsonResponse(data, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Cliente o artículo no encontrado'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Datos de la venta incompletos'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Error en los valores numéricos'}, status=400)
        except Exception as e:
            tb = traceback.format_exc()
            return JsonResponse({
                'error': str(e),
                'detail': "Ocurrió un error inesperado",
                'traceback': tb,  # Esto incluirá la línea exacta del error
                'type': type(e).__name__  # Tipo de excepción
            }, status=500)

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

    def update_user_comision(self, user_id, total_devuelto, total_recompra):
        try:
            usuario = User.objects.get(pk=int(user_id))

            # Validar que el usuario tenga porcentajeComision
            if usuario.porcentajeComision is None:
                print(f"Advertencia: Usuario {user_id} no tiene porcentaje de comisión definido")
                return float(0)  # Retorna 0 en lugar de None

            total_recompra = Decimal(str(total_recompra))
            total_devuelto = Decimal(str(total_devuelto))
            porcentaje = Decimal(str(usuario.porcentajeComision)) / Decimal(100)

            diferencia_comision = (total_recompra - total_devuelto) * porcentaje
            comisionNeta = total_recompra * porcentaje

            fecha_actual = timezone.now().date()
            mes_actual = fecha_actual.month
            anio_actual = fecha_actual.year

            historico = HistoricosComisiones.objects.filter(
                fecha__year=anio_actual,
                fecha__month=mes_actual,
                usuario=usuario
            ).first()

            if historico:
                historico.comisionAcumulada += Decimal(diferencia_comision)
                historico.save()
            else:
                HistoricosComisiones.objects.create(
                    fecha=fecha_actual.date(),  # Se guarda la fecha actual
                    comisionAcumulada=Decimal(diferencia_comision),
                    usuario=usuario
                )

            return comisionNeta

        except User.DoesNotExist:
            print(f"Error: Usuario con ID {user_id} no encontrado.")
            return float(0)  # Retorna 0 en lugar de None
        except Exception as e:
            tb = traceback.format_exc()
            error_data = {
                'error': str(e),
                'detail': "Ocurrió un error inesperado",
                'traceback': tb,
                'type': type(e).__name__
            }
            print(error_data)  # Solo imprime el diccionario de error
            return float(0)  # Retorna 0 como float

    def update_socio_ventas_totales(self, cliente, total_devolucion, total_recompra, estado_previo, estado_nuevo):
        cliente.totalVentas = F('totalVentas') - total_devolucion + total_recompra

        if estado_previo == Venta.EstadoVenta.PENDIENTE:
            cliente.montoMaximoPendiente = F('montoMaximoPendiente') + total_devolucion
            cliente.montoPendiente = F('montoPendiente') - total_devolucion

        if estado_nuevo == Venta.EstadoVenta.PENDIENTE:
            cliente.montoMaximoPendiente = F('montoMaximoPendiente') - total_recompra
            cliente.montoPendiente = F('montoPendiente') + total_recompra

        cliente.save(update_fields=['totalVentas', 'montoMaximoPendiente', 'montoPendiente'])

    def obtener_datos_socio(self, request):
        data = {}
        cliente_id = request.POST.get('cliente_id')

        try:
            cliente = SocioMinorista.objects.get(id=cliente_id)
            data['porcentajeDescuento'] = cliente.porcentajeDescuento
            data['estadoPrestamo'] = cliente.prestamo
            data['montoMaximoPendiente'] = cliente.montoMaximoPendiente
            return JsonResponse(data)  # Convertir a JsonResponse

        except SocioMinorista.DoesNotExist:
            return JsonResponse({'error': "Cliente no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(
            self.get_details_product(),
            cls=DecimalJSONEncoder  # Usamos nuestro encoder personalizado
        )
        return context

class DecimalJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(str(obj))  # Convertimos Decimal a float (via string para precisión)
        return super().default(obj)

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
