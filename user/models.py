from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict

from sedes.models import Sede
from servimotos.settings import MEDIA_URL, STATIC_URL




class User(AbstractUser):
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)
    token = models.UUIDField(primary_key=False, editable=False, null=True, blank=True)
    sedePerteneciente = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='user_Compañia')
    porcentajeComision = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        item = model_to_dict(self, exclude=['password', 'user_permissions', 'last_login'])
        if self.last_login:
            item['last_login'] = self.last_login.strftime('%Y-%m-%d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['image'] = self.get_image()
        item['full_name'] = self.get_full_name()
        item['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups.all()]
        item['porcentajeComision'] = format(self.porcentajeComision, '.1f')
        return item

class HistoricosComisiones(models.Model):
    fecha = models.DateField(verbose_name='Fecha de Guardado')
    comisionAcumulada = models.DecimalField(verbose_name='Comision Acumulada en el Mes', max_digits=9, decimal_places=0, default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Historico en fecha {self.fecha}'

    def toJSON(self):
        item = model_to_dict(self)
        item['comisionAcumulada'] = self.comisionAcumulada
        return item