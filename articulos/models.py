from django.db import models

# Create your models here.
from categorias.models import Categoria
from django.forms import model_to_dict

from distribuidores.models import Distribuidor
from marcas.models import Marca
from sedes.models import Sede


class Articulo(models.Model):

    nombre = models.CharField(max_length=255, verbose_name='Referencia', null=True)
    codigoOriginal = models.CharField(max_length=255, verbose_name='Codigo Original')
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE)
    descuentoAntesDeIva = models.IntegerField(verbose_name='Descuento Por Distribuidor', default=0)
    precioCosto = models.DecimalField(verbose_name='Precio Distribuidor', max_digits=12, decimal_places=0)
    tasaGanacia = models.IntegerField(verbose_name='Porcentaje de Ganancia')
    iva = models.DecimalField(verbose_name='Iva (calculado antes de ganancia)', max_digits=12, decimal_places=0)
    precioFinal = models.DecimalField(verbose_name='Precio Publico', max_digits=12, decimal_places=0)
    stock = models.IntegerField(verbose_name='Cantidad Unidades')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, verbose_name='Categoria')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, verbose_name='Marca')
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

    def __str__(self):
        return f'Articulo {self.id}: {self.nombre} {self.precioCosto} {self.precioFinal} {self.stock} '

    def toJSON(self):
        item = model_to_dict(self)
        item['categoria'] = self.categoria.toJSON()
        item['marca'] = self.marca.toJSON()
        item['distribuidor'] = self.distribuidor.toJSON()
        return item


class Historico_Precios(models.Model):
    fecha = models.DateField(verbose_name='Fecha de Guardado')
    precioIvaIncluido = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Precio de Compra Iva Incluido')
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)

    def __str__(self):
        return f'Historico en fecha {self.fecha}'

    def toJSON(self):
        item = model_to_dict(self)
        return item