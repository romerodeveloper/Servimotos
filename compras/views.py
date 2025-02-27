import logging
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.backends import console
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from articulos.models import Articulo

from compras.models import Compra, DetCompra

from compras.forms import CompraForm


class CompraListView(LoginRequiredMixin, ListView):
    model = Compra
    template_name = 'listCompra.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Compra.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetCompra.objects.filter(compra_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Compras'
        context['create_url'] = reverse_lazy('agregar_compra')
        context['list_url'] = reverse_lazy('lista_compra')
        context['entity'] = 'Compras'
        return context


class CompraCreateView(LoginRequiredMixin, CreateView):
    model = Compra
    form_class = CompraForm
    template_name = 'createCompra.html'
    success_url = reverse_lazy('lista_compra')
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
            elif action == 'add':
                with transaction.atomic():
                    comps = json.loads(request.POST['comps'])
                    comp = Compra()
                    comp.date_joined = comps['date_joined']
                    comp.distribuidor_id = comps['distribuidor']
                    comp.subtotal = float(comps['subtotal'])
                    comp.iva = float(comps['iva'])
                    comp.total = float(comps['total'])
                    comp.save()
                    for i in comps['products']:
                        det = DetCompra()
                        det.compra_id = comp.id
                        det.articulo_id = i['id']
                        det.cantidad = int(i['cant'])
                        det.precio = float(i['precioFinal'])
                        det.subtotal = float(i['subtotal'])
                        #insert de articulo
                        det.save()
                        det.articulo.stock += det.cantidad
                        det.articulo.tasaGanacia = float(i['tasaGanacia'])
                        det.articulo.precioCosto = float(i['precioCosto'])
                        det.articulo.precioFinal = float(i['precioFinal'])
                        det.articulo.iva = float(i['ivaProd'])
                        det.articulo.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una Compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

class CompraDeleteView(LoginRequiredMixin, DeleteView):
    model = Compra
    template_name = 'deleteCompra.html'
    success_url = reverse_lazy('lista_compra')
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
        context['title'] = 'Eliminación de Una Compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        return context

class CompraUpdateView(LoginRequiredMixin, UpdateView):
    model = Compra
    form_class = CompraForm
    template_name = 'createCompra.html'
    success_url = reverse_lazy('lista_compra')
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
                    comps = json.loads(request.POST['comps'])
                    #venta = Venta.objects.get(pk=self.get_object().id)
                    comp = self.get_object()
                    comp.date_joined = comps['date_joined']
                    comp.distribuidor_id = comps['distribuidor']
                    comp.subtotal = float(comps['subtotal'])
                    comp.iva = float(comps['iva'])
                    comp.total = float(comps['total'])
                    comp.save()
                    comp.detcompra_set.all().delete()
                    for i in comps['products']:
                        det = DetCompra()
                        det.compra_id = comp.id
                        det.articulo_id = i['id']
                        det.cantidad = int(i['cant'])
                        det.precio = float(i['precioFinal'])
                        det.subtotal = float(i['subtotal'])
                        # insert de articulo
                        det.save()
                        det.articulo.stock += (int(i['cant']) - int(i['cantidadIni']))
                        det.articulo.tasaGanacia = float(i['tasaGanacia'])
                        det.articulo.precioCosto = float(i['precioCosto'])
                        det.articulo.precioFinal = float(i['precioFinal'])
                        det.articulo.iva = float(i['ivaProd'])
                        det.articulo.save()
                        if comps['articulosEliminados'] != []:
                            for i in comps['articulosEliminados']:
                                articulo = Articulo.objects.get(pk=i['id'])
                                articulo.stock -= int(i['cantidadIni'])
                                articulo.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_details_product(self):
        data = []
        try:
            for i in DetCompra.objects.filter(compra_id=self.get_object().id):
                item = i.articulo.toJSON()
                item['cant'] = i.cantidad
                data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Una Compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.get_details_product())
        return context
