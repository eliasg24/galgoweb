import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.models import User, Group
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest, TruncDate

from dashboards.models import Aplicacion, Llanta, Perfil, Ubicacion, Vehiculo


# Create your views here.

class GalgoSucursales(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        email = request.GET.get('email', None)
        print(email)
        if email == '' or email == None:
            json_context = json.dumps({'status': 'datos incompletos'}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        
        try:
            user = User.objects.get(email = email)
            perfil = Perfil.objects.get(user = user)
            try:
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
            except:
                json_context = json.dumps({'status': 'no existe cuenta con el email definido'}, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
        except:
            json_context = json.dumps({'status': 'no existe cuenta con el email definido'}, indent=None, sort_keys=False, default=str)
    
            return HttpResponse(json_context, content_type='application/json')
    
class GalgoAplicaciones(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        email = request.GET.get('email', None)
        print(email)
        if email == '' or email == None:
            json_context = json.dumps({'status': 'datos incompletos'}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        try:
            user = User.objects.get(email = email)
            perfil = Perfil.objects.get(user = user)
            try:
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
                    'aplicaciones': ubicacion_list,
                }

                json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
            except:
                json_context = json.dumps({'status': 'no existe cuenta con el email definido'}, indent=None, sort_keys=False, default=str)

                return HttpResponse(json_context, content_type='application/json')
        except:
            json_context = json.dumps({'status': 'no existe cuenta con el email definido'}, indent=None, sort_keys=False, default=str)
    
            return HttpResponse(json_context, content_type='application/json')
        
class GalgoVehiculos(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        sucursal = request.GET.get('sucursal', None)
        print(sucursal)
        if sucursal == '' or sucursal == None:
            json_context = json.dumps({'status': 'datos incompletos'}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        
        try:
            sucursal = Ubicacion.objects.get(id = sucursal)
            vehiculos = Vehiculo.objects.filter(compania = sucursal.compania, ubicacion = sucursal)
        
            #Serializar data
            ubicacion_list = list(vehiculos.values(
                        "id",
                        "numero_economico",
                        "modelo",
                        "marca",
                        "compania_id",
                        "compania__compania",
                        "ubicacion_id",
                        "ubicacion__nombre",
                        "numero_de_llantas",
                        "clase",
                        "configuracion",
                        "km",
                        "estatus_activo",
            ))
            dict_context = {
                'vehiculos': ubicacion_list,
            }
            json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        except:
            json_context = json.dumps({'status': 'sin coincidencias'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        
class GalgoLlantas(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        print('sdnfsdfnl')
        vehiculo = request.GET.get('vehiculo', None)
        print(vehiculo)
        if vehiculo == '' or vehiculo == None:
            json_context = json.dumps({'status': 'datos incompletos'}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        
        
        try:
            vehiculo = Vehiculo.objects.get(id = vehiculo)
            llantas = Llanta.objects.filter(vehiculo=vehiculo, inventario='Rodante').annotate(
            min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")
            )
            #Serializar data
            ubicacion_list = list(llantas.values(
                "id",
                "numero_economico",
                "compania_id",
                "compania__compania",
                "vehiculo_id",
                "vehiculo__numero_economico",
                "vida",
                "tipo_de_eje",
                "eje",
                "posicion",
                "nombre_de_eje",
                "presion_actual",
                "inventario",
                "min_profundidad",
            ))
            dict_context = {
                'llantas': ubicacion_list,
            }
            json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        except:
            json_context = json.dumps({'status': 'sin coincidencias'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')