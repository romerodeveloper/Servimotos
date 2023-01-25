import logging
import json
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.backends import console
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
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

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                termino = request.POST['term']
                prods = Articulo.objects.filter(nombre__icontains=termino)[0:10]
                for i in prods[0:10]:
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
            elif action == 'add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    venta = Venta()
                    venta.date_joined = vents['date_joined']
                    venta.use_id = request.user.id
                    venta.cliente = vents['cliente']
                    venta.descuento = float(vents['descuento'])
                    venta.subtotal = float(vents['subtotal'])
                    venta.iva = float(vents['iva'])
                    venta.total = float(vents['total'])
                    venta.save()
                    for i in vents['products']:
                        det = DetVenta()
                        det.venta_id = venta.id
                        det.articulo_id = i['id']
                        det.cantidad = int(i['cant'])
                        det.precio = float(i['precioFinal'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                        det.articulo.stock -= det.cantidad
                        det.articulo.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

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
                    #venta = Venta.objects.get(pk=self.get_object().id)
                    venta = self.get_object()
                    venta.date_joined = vents['date_joined']
                    venta.use_id = request.user.id
                    venta.cliente = vents['cliente']
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
                'comp': {'nombre': 'SERVIMOTOS DEL CAMINO S.A.', 'runt': '80731044', 'direccion': 'Av. Boyaca # 51b - 39 SUR BOGOTA, COLOMBIA', 'correo': 'servimotos_del_camino@gmail.com', 'celular': '3112932799'},
                'icon': '{}{}'.format(settings.MEDIA_URL, 'logo.png')
            }
            html = template.render(context)
            css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
            pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('lista_venta'))
