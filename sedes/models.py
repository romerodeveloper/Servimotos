from django.db import models

from compañias.models import Compañia

class Sede(models.Model):
    direccion = models.CharField(max_length=255, verbose_name='Dirección', unique=True, null=False)
    ventasTotales = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Ventas totales de la sede', default=0)
    comprasTotales = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Compras totales de la sede', default=0)
    companiaPerteneciente = models.ForeignKey(Compañia, on_delete=models.CASCADE, related_name='sede_Compañia')

    def toJSON(self):
        item = super().toJSON()
        item['companiaPerteneciente'] = self.Compañia.toJSON()
        return item


    def __str__(self):
        return self.direccion
