from django.db import models

# Create your models here.
from categorias.models import Categoria
from django.forms import model_to_dict

from distribuidores.models import Distribuidor
from marcas.models import Marca


class Articulo(models.Model):
    nombre = models.CharField(max_length=255, verbose_name='Referencia')
    precioCosto = models.FloatField(verbose_name='Precio Distribuidor')
    tasaGanacia = models.FloatField(verbose_name='Porcentaje de Ganancia')
    iva = models.FloatField(verbose_name='Iva (calculado antes de ganancia)')
    precioFinal = models.FloatField(verbose_name='Precio Publico')
    stock = models.IntegerField(verbose_name='Cantidad Unidades')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, verbose_name='Categoria')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, verbose_name='Marca')
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE)

    def __str__(self):
        return f'Articulo {self.id}: {self.nombre} {self.precioCosto} {self.precioFinal} {self.stock} '

    def toJSON(self):
        item = model_to_dict(self)
        item['categoria'] = self.categoria.toJSON()
        item['marca'] = self.marca.toJSON()
        item['precioFinal'] = format(self.precioFinal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['distribuidor'] = self.distribuidor.toJSON()
        return item
