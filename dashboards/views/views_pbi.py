import json
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.models import User, Group

from dashboards.models import Perfil, Vehiculo


class VeicleData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        vehiculos = Vehiculo.objects.filter(compania=compania)
        #Serializar data
        vehiculos = list(vehiculos.values())
        
        dict_context = {
            'vehiculos': vehiculos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')