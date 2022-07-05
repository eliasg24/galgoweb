from django.db import models

from dashboards.models import Compania, ServicioVehiculo, Vehiculo

# Create your models here.

class Calendario(models.Model):
    # Modelo de la Compañía
    servicio = models.ForeignKey(ServicioVehiculo, on_delete=models.CASCADE, null=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True)
    start = models.DateField(null=True, blank=True)
    horario_start = models.TimeField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    horario_end = models.TimeField(null=True, blank=True)
    
    horario_start_str = models.CharField(max_length=255, null=True, blank=True)
    horario_end_str = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True)

    def __str__(self):
        # Retorna el nombre de la compañía
        return f"start: {self.start}, end: {self.end}, title: {self.title}"
