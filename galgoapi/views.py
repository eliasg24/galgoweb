from datetime import date
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.models import User, Group
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest, TruncDate

from dashboards.models import Aplicacion, Inspeccion, InspeccionVehiculo, Llanta, Perfil, Ubicacion, Vehiculo
from dashboards.functions import functions as func
from galgoapi.functions import functions
from django.utils import timezone
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
        
class GalgoInspeccion(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        try:
            vehiculo = int( request.GET.get('vehiculo', None) )
            
        except:
            json_context = json.dumps({'status': 'vehiculo debe ser un numero entero'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        
        try:
            llantas = request.GET.get('llantas', None)
            llantas = functions.str_to_list_int(llantas)
        except:
            json_context = json.dumps({'status': 'llantas deben ser un numero entero'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
            
        try:
            presiones = request.GET.get('presiones', None)
            presiones = functions.str_to_list_int(presiones)
        except:
            json_context = json.dumps({'status': 'dato incorrectos en presiones'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        
        try:
            profundidades = request.GET.get('profundidades', None)
            profundidades = functions.str_to_list_int(profundidades)
        except:
            json_context = json.dumps({'status': 'datos incorrectos en profundidades'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        
        email = request.GET.get('email', None)
        
        if len(llantas) != len(presiones) != len(profundidades):
            json_context = json.dumps({'status': 'la cantidad de datos no coinciden'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        
        try:
            user = User.objects.get(email=email)
            usuario_actual = Perfil.objects.get(user=user)
            perfil = Perfil.objects.get(user=user)
            vehiculo = Vehiculo.objects.get(pk=vehiculo)
            if perfil.compania != vehiculo.compania:
                json_context = json.dumps({'status': 'Este usuario no tiene permitido modificar esta unidad, cambie su contexto'}, indent=None, sort_keys=False, default=str)
                return HttpResponse(json_context, content_type='application/json')
            
            
            llantas_check = Llanta.objects.filter(id__in = llantas, vehiculo = vehiculo, inventario = 'Rodante').count()
            if llantas_check != len(llantas):
                json_context = json.dumps({'status': 'Esta intentando editar llantas que no son rodante o que no pertenecen al veiculo'}, indent=None, sort_keys=False, default=str)
                return HttpResponse(json_context, content_type='application/json')
            
            vehiculo_inspeccion = InspeccionVehiculo.objects.create(
                tipo_de_evento = 'Inspección Galgo',
                usuario = usuario_actual,
                vehiculo = vehiculo,
                fecha = timezone.now()
            ) 
            
            index = 0
            inspecciones = []
            llantas_exclude = Llanta.objects.filter(vehiculo_id = vehiculo.id, inventario = 'Rodante').exclude(id__in = llantas)
            print(llantas_exclude)
            for llanta_ in llantas:
                llanta = llantas[index]
                presion = presiones[index]
                profundidad = profundidades[index]
                llanta_act = Llanta.objects.get(pk=llanta)
                producto = llanta_act.producto
                
                llanta_act.presion_actual = presion
                if profundidad <= producto.profundidad_inicial:
                    llanta_act.profundidad_central = profundidad
                
                llanta_act.save()
                func.check_dualizacion(llanta_act)
                func.check_dif_presion_duales(llanta_act)
                
                inspecciones.append(Inspeccion(
                        tipo_de_evento = 'Inspección Galgo',
                        inspeccion_vehiculo = vehiculo_inspeccion,
                        llanta = llanta_act,
                        posicion = llanta_act.posicion,
                        tipo_de_eje = llanta_act.tipo_de_eje,
                        eje = llanta_act.eje,
                        usuario = usuario_actual,
                        vehiculo = vehiculo,
                        fecha_hora = timezone.now(),
                        vida = llanta_act.vida,
                        km_vehiculo = vehiculo.km,
                        presion = presion,
                        presion_establecida = func.presion_establecida(llanta_act),
                        profundidad_izquierda = None,
                        profundidad_central = profundidad,
                        profundidad_derecha = None,
                        evento = str({\
                        "llanta_inicial" : str(llanta_act.id), "llanta_mod" : "",\
                        "numero_economico": llanta_act.numero_economico, "numero_economico_mod": "",
                        "producto_inicial" : str(producto), "producto_mod" : "",\
                        "vida_inicial" : llanta_act.vida, "vida_mod" : "",\
                        "km_inicial" : str(vehiculo.km), "km_mod" : "",\
                        "presion_inicial" : str(presion), "presion_mod" : "",\
                        "profundidad_izquierda_inicial" : str(''), "profundidad_izquierda_mod" : "",\
                        "profundidad_central_inicial" : str(profundidad), "profundidad_central_mod" : "",\
                        "profundidad_derecha_inicial" : str(''), "profundidad_derecha_mod" : ""\
                        })
                    ))
                
                print('---')
                
                index += 1
                
            for llanta_ in llantas_exclude:
                llanta_act = llanta_
                producto = llanta_act.producto
                
                inspecciones.append(Inspeccion(
                        tipo_de_evento = 'Inspección Galgo',
                        inspeccion_vehiculo = vehiculo_inspeccion,
                        llanta = llanta_act,
                        posicion = llanta_act.posicion,
                        tipo_de_eje = llanta_act.tipo_de_eje,
                        eje = llanta_act.eje,
                        usuario = usuario_actual,
                        vehiculo = vehiculo,
                        fecha_hora = timezone.now(),
                        vida = llanta_act.vida,
                        km_vehiculo = vehiculo.km,
                        presion = llanta_act.presion_actual,
                        presion_establecida = func.presion_establecida(llanta_act),
                        profundidad_izquierda = llanta_act.profundidad_izquierda,
                        profundidad_central = llanta_act.profundidad_central,
                        profundidad_derecha = llanta_act.profundidad_derecha,
                        evento = str({\
                        "llanta_inicial" : str(llanta_act.id), "llanta_mod" : "",\
                        "numero_economico": llanta_act.numero_economico, "numero_economico_mod": "",
                        "producto_inicial" : str(producto), "producto_mod" : "",\
                        "vida_inicial" : llanta_act.vida, "vida_mod" : "",\
                        "km_inicial" : str(vehiculo.km), "km_mod" : "",\
                        "presion_inicial" : str(llanta_act.presion_actual), "presion_mod" : "",\
                        "profundidad_izquierda_inicial" : str(llanta_act.profundidad_izquierda), "profundidad_izquierda_mod" : "",\
                        "profundidad_central_inicial" : str(llanta_act.profundidad_central), "profundidad_central_mod" : "",\
                        "profundidad_derecha_inicial" : str(llanta_act.profundidad_derecha), "profundidad_derecha_mod" : ""\
                        })
                    ))
                index += 1
            obj = Inspeccion.objects.bulk_create(inspecciones)
            
            func.rectificar_observaciones_vehiculo(vehiculo)
            vehiculo.fecha_ultima_inspeccion = timezone.now()
            vehiculo.save()
            dict_context = {
                'Status': 'Inspeccion Realizada',
            }
            json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')
        except Exception as ex:
            print(ex)
            json_context = json.dumps({'status': 'Datos erroneos'}, indent=None, sort_keys=False, default=str)
            return HttpResponse(json_context, content_type='application/json')