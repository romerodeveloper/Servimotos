from datetime import datetime
from django.db import models
# Create your models here.
from django.forms import model_to_dict

from sociosMinoristas.models import SocioMinorista
from user.models import User
from articulos.models import Articulo


class Venta(models.Model):
    class EstadoVenta(models.TextChoices):
        PAGO = "PAGO"
        PENDIENTE = "PENDIENTE"
        DEVUELTO = "DEVUELTO"

    estadoVenta = models.CharField(
        max_length=10,
        choices=EstadoVenta.choices,
        default=EstadoVenta.PAGO,
        verbose_name="Estado de la Venta Actual"
    )
    use = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(SocioMinorista, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    descuento = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    subtotal = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    iva = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    total = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    ganancia = models.DecimalField(default=0, max_digits=9, decimal_places=0)

    def toJSON(self):
        item = model_to_dict(self)
        item['use'] = self.use.toJSON()
        item['cliente'] = self.cliente.toJSON()
        item['descuento'] = self.descuento
        item['ganancia'] = self.descuento
        item['subtotal'] = self.subtotal
        item['iva'] = self.iva
        item['total'] = self.total
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['det'] = [i.toJSON() for i in self.detventa_set.all()]
        return item

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['id']

class DetVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    precio = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    cantidad = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0, max_digits=9, decimal_places=0)

    def __str__(self):
        return self.prod.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['venta'])
        item['articulo'] = self.articulo.toJSON()
        item['precio'] = format(self.precio, '.1f')
        item['subtotal'] = format(self.subtotal, '.1f')
        return item

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalle de Ventas'
        ordering = ['id']
