from django.db import models

from compañias.models import Compañia

class Sede(models.Model):
    direccion = models.CharField(max_length=255, verbose_name='Dirección', unique=True, null=False)
    ventasTotales = models.FloatField(verbose_name='Ventas totales de la sede')
    comprasTotales = models.FloatField(verbose_name='Compras totales de la sede')
    companiaPerteneciente = models.ForeignKey(Compañia, on_delete=models.CASCADE, related_name='sede_Compañia')

    def toJSON(self):
        item = super().toJSON()
        item['ventasTotales'] = format(self.ventasTotales, '.2f')
        item['comprasTotales'] = format(self.comprasTotales, '.2f')
        #item['usuarioAdministrador'] = self.User.toJSON()
        item['companiaPerteneciente'] = self.Compañia.toJSON()
        return item

    def __str__(self):
        return self.direccion
