from django.db import models

# Create your models here
# .
from django.forms import model_to_dict


class Marca(models.Model):
    nombre = models.CharField(max_length=255)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    def __str__(self):
        return f'{self.nombre}'