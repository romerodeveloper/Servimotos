from datetime import datetime
from django.db import models
# Create your models here.
from django.forms import model_to_dict
from user.models import User
from articulos.models import Articulo

from distribuidores.models import Distribuidor


class Compra(models.Model):
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    iva = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    total = models.DecimalField(default=0, max_digits=9, decimal_places=0)

    def toJSON(self):
        item = model_to_dict(self)
        item['distribuidor'] = self.distribuidor.toJSON()
        item['subtotal'] = self.subtotal
        item['iva'] = self.iva
        item['total'] = self.total
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['det'] = [i.toJSON() for i in self.detcompra_set.all()]
        return item

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['id']

class DetCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    precio = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    cantidad = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0, max_digits=9, decimal_places=0)

    def __str__(self):
        return self.prod.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['venta'])
        item['articulo'] = self.articulo.toJSON()
        item['precio'] = self.precio
        item['subtotal'] = self.subtotal
        return item

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalle de Compras'
        ordering = ['id']
