from django.db import models

from dashboards.models import Compania

# Create your models here.

class Calendario(models.Model):
    # Modelo de la Compañía

    start = models.DateField(null=True, blank=True)
    horario_start = models.TimeField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    horario_end = models.TimeField(null=True, blank=True)
    
    title = models.CharField(max_length=255, null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)

    def __str__(self):
        # Retorna el nombre de la compañía
        return f"start: {self.start}, end: {self.end}, title: {self.title}"
