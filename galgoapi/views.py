import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.models import User, Group

from dashboards.models import Aplicacion, Perfil, Ubicacion


# Create your views here.

class GalgoSucursales(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        email = request.GET.get('email', None)
        password = request.GET.get('password', None)
        print(email)
        print(password)
        if (
            email == '' or email == None
            or
            password == '' or password == None
            ):
            json_context = json.dumps({'status': 'datos incompletos'}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        
        try:
            user = User.objects.get(email = email)
            perfil = Perfil.objects.get(user = user)
            is_pass_ok = user.check_password(password)
            if is_pass_ok:
                ubicacion = Ubicacion.objects.filter(compania = perfil.compania)

                #Serializar data
                ubicacion_list = list(ubicacion.values(
                        "id",
                        "nombre",
                        "compania__id",
                        "compania__compania",
                        ))
                dict_context = {
                    'sucursales': ubicacion_list,
                }

                json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
            else:
                json_context = json.dumps({'status': 'datos incorrectos'}, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
        except:
            json_context = json.dumps({'status': 'no existe cuenta con el email definido'}, indent=None, sort_keys=False, default=str)
    
            return HttpResponse(json_context, content_type='application/json')
    
    
    
class GalgoAplicaciones(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        email = request.GET.get('email', None)
        password = request.GET.get('password', None)
        print(email)
        print(password)
        if (
            email == '' or email == None
            or
            password == '' or password == None
            ):
            json_context = json.dumps({'status': 'datos incompletos'}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        try:
            user = User.objects.get(email = email)
            perfil = Perfil.objects.get(user = user)
            is_pass_ok = user.check_password(password)
            if is_pass_ok:
                ubicacion = Aplicacion.objects.filter(compania = perfil.compania)

                #Serializar data
                ubicacion_list = list(ubicacion.values(
                        "id",
                        "nombre",
                        "compania__id",
                        "compania__compania",
                        "ubicacion__id",
                        "ubicacion__nombre",
                        ))
                dict_context = {
                    'sucursales': ubicacion_list,
                }

                json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
            else:
                json_context = json.dumps({'status': 'datos incorrectos'}, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
        except:
            json_context = json.dumps({'status': 'no existe cuenta con el email definido'}, indent=None, sort_keys=False, default=str)
    
            return HttpResponse(json_context, content_type='application/json')