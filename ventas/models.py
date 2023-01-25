from datetime import datetime
from django.db import models
# Create your models here.
from django.forms import model_to_dict
from user.models import User
from articulos.models import Articulo


class Venta(models.Model):
    use = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.CharField(max_length=255, verbose_name='Referencia', default='N/A')
    date_joined = models.DateField(default=datetime.now)
    descuento = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)
    subtotal = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)
    iva = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)
    total = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)

    def toJSON(self):
        item = model_to_dict(self)
        item['use'] = self.use.toJSON()
        item['descuento'] = format(self.descuento, '.1f')
        item['subtotal'] = format(self.subtotal, '.1f')
        item['iva'] = format(self.iva, '.1f')
        item['total'] = format(self.total, '.1f')
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
    precio = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)
    cantidad = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)

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
