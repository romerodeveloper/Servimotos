from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from articulos.models import Articulo
from compañias.models import Compañia
from sedes.models import Sede
from ventas.models import DetVenta


class VentaUtils:

    @staticmethod
    def search_autocomplete(request):
        data = []
        term = request.POST['term'].strip()
        products = Articulo.objects.filter(
            stock__gt=0,
            sede_id=request.user.sedePerteneciente.id,
            nombre__icontains=term
        )
        for i in products[0:20]:
            item = i.toJSON()
            item['text'] = f"{i.nombre}, {i.categoria.nombre}"
            data.append(item)
        return data

    @staticmethod
    def add_detalle_venta(venta, product_data):
        articulo = Articulo.objects.get(pk=product_data['id'])
        DetVenta.objects.create(
            venta=venta,
            articulo=articulo,
            cantidad=int(product_data['cant']),
            precio=float(product_data['precioFinal']),
            subtotal=float(product_data['subtotal'])
        )
        articulo.stock -= int(product_data['cant'])
        articulo.save()

    @staticmethod
    def validar_stock(producto_id, cantidad):
        with transaction.atomic():
            producto = Articulo.objects.select_for_update().get(pk=producto_id)
            if producto.stock < cantidad:
                raise ValidationError(f'Solo quedan {producto.stock} y esta pidiendo {cantidad} unidades disponibles de {producto.nombre}')

    @staticmethod
    def actualizar_ventas(user, total):
        """Actualizar ventas de la sede y compañía."""
        sede_id = user.sedePerteneciente.id
        compania_id = user.sedePerteneciente.companiaPerteneciente.id

        Sede.objects.filter(id=sede_id).update(ventasTotales=F('ventasTotales') + total)
        Compañia.objects.filter(id=compania_id).update(ventasTotales=F('ventasTotales') + total)

    @staticmethod
    def check_stock(request, param="create", venta=None):
        data = {}
        producto_id = request.POST.get('id')
        cantidad = int(request.POST.get('cantidad', 0))
        if param == "edit":##validad de no cuente la misma cantidad que devolvera
            cantidadDetalle = DetVenta.objects.filter(venta=venta, articulo=producto_id).first()
            cantidadDetalleArticulo = cantidadDetalle.cantidad
            cantidad =  int(request.POST.get('cantidad', 0)) - int(cantidadDetalleArticulo)

        try:
            VentaUtils.validar_stock(producto_id, cantidad)
            data['status'] = 'ok'
        except ValidationError as e:
            data['status'] = 'error'
            data['message'] = str(e)
        return data