import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin

from calendario.models import Calendario
from dashboards.models import Perfil

# Create your views here.

class CalendarioApi(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):
        user = self.request.user
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        calendarios = Calendario.objects.filter(compania = compania)
        calendarios = list(calendarios.values('id', 'horario_start_str', 'horario_end_str', 'title'))
        
        dict_context = {
            'calendarios': calendarios,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')