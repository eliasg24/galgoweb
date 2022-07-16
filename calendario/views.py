from datetime import date, datetime
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func, Sum
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin


from calendario.models import Calendario
from dashboards.models import Llanta, Observacion, Perfil, ServicioVehiculo, Taller, Vehiculo
from dashboards.functions import functions as func
from calendario.functions import functions

# Create your views here.

class CalendarioApi(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):
        user = self.request.user
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        hoy = datetime.today()
        calendarios = Calendario.objects.filter(compania = compania).annotate(
            id_servicio = F('servicio__id'),
            color = Case(
                    When(servicio__estado='cerrado', then=Value("blue")),
                    When(end__lte=hoy, then=Value("red")),
                    default=Value("green")
                    ),
            estado=F('servicio__estado'),
            reporte = Case(
                    When( servicio__estado='cerrado', then='servicio__id'),
                    When( servicio__estado='abierto', then=Value(0))
                    ),
            title = F('vehiculo__numero_economico'),
            
            )
        calendarios = list(calendarios.values('id', 'horario_start_str', 'horario_end_str', 'title', 'estado', 'color', 'reporte', 'id_servicio'))
        
        dict_context = {
            'calendarios': calendarios,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')


class CerrarServicioApi(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):
        user = self.request.user
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        hoy = datetime.today()
        
        servicio = (request.GET['servicio'] if 'servicio' in request.GET else None)
        print(servicio)
        if servicio != '' and servicio != None:
            try:
                servicio = ServicioVehiculo.objects.get(pk=servicio)
            except:
                json_context = json.dumps({'status': 'Servicio no encontrado'}, indent=None, sort_keys=False, default=str)
                return HttpResponse(json_context, content_type='application/json')
            if servicio.estado == 'cerrado':
                json_context = json.dumps({'status': 'Servicio Cerrado'}, indent=None, sort_keys=False, default=str)
                return HttpResponse(json_context, content_type='application/json')
            preguardado_vehiculo = servicio.preguardado_vehiculo
            preguardado_vehiculo = preguardado_vehiculo.replace("\'", "\"")
            preguardado_vehiculo = json.loads(preguardado_vehiculo)
            
            preguardado_llantas = []
            preguardado_llantas_raw = servicio.preguardado_llantas
            preguardado_llantas_raw = preguardado_llantas_raw.replace("\'", "\"")
            preguardado_llantas_raw = json.loads(preguardado_llantas_raw)
            
            for dato in preguardado_llantas_raw:
                if dato:
                    preguardado_llantas.append(dato)
            print(preguardado_llantas)
            
            vehiculo = servicio.vehiculo
            for vehicule in preguardado_vehiculo:
                if 'alinearVehiculo' in vehicule:
                    vehiculo.fecha_ultima_alineacion = date.today()
            Vehiculo.objects.bulk_update([vehiculo], ['fecha_ultima_alineacion'])
            llantas_desmontadas = []
            llantas_rotadas = []
            print('---------------')
            for data in preguardado_llantas:
                print(data)
                if data['tipoServicio'] == 'desmontaje':
                    print('Desmontaje')
                    #? Se llama la llanta actual
                    llanta = Llanta.objects.get(pk=data['llanta'])
                    vehiculo = llanta.vehiculo
                    ubicacion = llanta.ubicacion
                    aplicacion = llanta.aplicacion
                    tipo_eje = llanta.tipo_de_eje
                    eje = llanta.eje
                    posicion = llanta.posicion

                    #? Se llama la llanta a montar
                    nuevaLlanta = data['llanta_nueva']
                    llanta_nueva = Llanta.objects.get(pk = nuevaLlanta)

                    #? Se obtienen los datos del desmontaje
                    razon = data['razon']
                    almacen_desmontaje = data['almacen_desmontaje']
                    
                    taller_desmontaje = Taller.objects.get(id = int(data['taller_desmontaje']))
                    
                    #? Se desmonta la llanta
                    llanta.inventario = almacen_desmontaje
                    llanta.taller = taller_desmontaje

                    #?Montaje de la nueva llanta
                    llanta_nueva.vehiculo = vehiculo
                    llanta_nueva.posicion = posicion
                    llanta_nueva.ubicacion = ubicacion
                    llanta_nueva.aplicacion = aplicacion
                    llanta_nueva.tipo_de_eje = tipo_eje
                    llanta_nueva.eje = eje
                    llanta_nueva.inventario = 'Rodante'

                    #? Se actualizan las llantas respectivamente
                    Llanta.objects.bulk_update([llanta_nueva], [
                        'vehiculo',
                        'posicion',
                        'ubicacion',
                        'aplicacion',
                        'tipo_de_eje',
                        'eje',
                        'inventario'
                        ])

                    Llanta.objects.bulk_update([llanta], [
                        'taller', 'inventario'
                        ])
                    llantas_desmontadas.append(llanta)

                    print('---------------')
                    
            for data in preguardado_llantas:
                if data['tipoServicio'] == 'sr':
                    print('Servicio')
                    #?Se llama la llanta
                    llanta = Llanta.objects.get(pk=data['llanta'])
                    #? Se verifican que servicios se realizaron
                    inflar = True if data['inflar'] == 'True' else False
                    balancear = True if data['balancear'] == 'True' else False
                    reparar = True if data['reparar'] == 'True' else False
                    valvula = True if data['valvula'] == 'True' else False
                    costado = True if data['costado'] == 'True' else False

                    rotar = data['rotar'] if data['rotar'] != 'False' else False


                    print(f'inflar:{inflar}')
                    print(f'balancear:{balancear}')
                    print(f'reparar:{reparar}')
                    print(f'valvula:{valvula}')
                    print(f'costado:{costado}')

                    print(f'rotar:{rotar}')

                    #? Servicios
                    if inflar:
                        print('Se inflo')
                        presion_establecida = func.presion_establecida(llanta)
                        llanta.presion_actual = presion_establecida
                        presion = Observacion.objects.get(observacion = 'Baja presión')
                        llanta.observaciones.remove(presion)
                    if balancear:
                        print('Se balanceo')
                        llanta.fecha_de_balanceado = date.today()
                    if reparar:
                        print('Se reparo')
                        obj_penetrado = Observacion.objects.get(observacion = 'Objeto penetrado')
                        llanta.observaciones.remove(obj_penetrado)
                    if valvula:
                        print('Se reparo valvula')
                        valvula_fuga = Observacion.objects.get(observacion = 'Válvula fugando')
                        valvula_inaccesible = Observacion.objects.get(observacion = 'Válvula inaccesible')
                        llanta.observaciones.remove(valvula_fuga)
                        llanta.observaciones.remove(valvula_inaccesible)
                    if costado:
                        print('Se reparo costado')
                        costado = Observacion.objects.get(observacion = 'Ruptura en costado')
                        llanta.observaciones.remove(costado)

                    Llanta.objects.bulk_update([llanta], [
                        'presion_actual', 
                        'fecha_de_balanceado'
                        ])

                    #? Rotar en el mismo vehiculo
                    if rotar == 'mismo':
                        print('Rotar en el mismo vehiculo')
                        id_llanta_rotar = int(data['llanta_rotar'])
                        llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)

                        if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                            continue
                        
                        #? Datos de la llanta a rotar
                        posicion_llanta_rotar = llanta_rotar.posicion
                        eje_llanta_rotar = llanta_rotar.eje
                        tipo_de_eje_llanta_rotar = llanta_rotar.tipo_de_eje

                        #? Datos de la llanta montada
                        posicion_llanta_montada = llanta.posicion
                        eje_llanta_montada = llanta.eje
                        tipo_de_eje_llanta_montada = llanta.tipo_de_eje

                        #? llanta montada
                        llanta.posicion = posicion_llanta_rotar
                        llanta.eje = eje_llanta_rotar
                        llanta.tipo_de_eje = tipo_de_eje_llanta_rotar
                        #? Llanta a rotar
                        llanta_rotar.posicion = posicion_llanta_montada
                        llanta_rotar.eje = eje_llanta_montada
                        llanta_rotar.tipo_de_eje = tipo_de_eje_llanta_montada

                        #? Quitar observaciones                  
                        func.quitar_desgaste(llanta, llanta_rotar)

                        Llanta.objects.bulk_update([llanta, llanta_rotar], [
                            'posicion', 
                            'tipo_de_eje', 
                            'eje', 
                            ])
                        llantas_rotadas.append(llanta)
                        llantas_rotadas.append(llanta_rotar)

                    #? Rotar en diferente vehiculo
                    if rotar == 'otro':
                        print('Rotar en diferentes vehiculo')
                        id_llanta_rotar = int(data['llanta_rotar'])
                        llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)

                        if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                            continue
                        
                        #? Datos de la llanta a rotar
                        vehiculo_llanta_rotar = llanta_rotar.vehiculo
                        posicion_llanta_rotar = llanta_rotar.posicion
                        eje_llanta_rotar = llanta_rotar.eje
                        tipo_de_eje_llanta_rotar = llanta_rotar.tipo_de_eje

                        #? Datos de la llanta montada
                        vehiculo_llanta_montada = llanta.vehiculo
                        posicion_llanta_montada = llanta.posicion
                        eje_llanta_montada = llanta.eje
                        tipo_de_eje_llanta_montada = llanta.tipo_de_eje

                        #? llanta montada
                        llanta.vehiculo = vehiculo_llanta_rotar
                        llanta.posicion = posicion_llanta_rotar
                        llanta.eje = eje_llanta_rotar
                        llanta.tipo_de_eje = tipo_de_eje_llanta_rotar
                        #? Llanta a rotar
                        llanta_rotar.vehiculo = vehiculo_llanta_montada
                        llanta_rotar.posicion = posicion_llanta_montada
                        llanta_rotar.eje = eje_llanta_montada
                        llanta_rotar.tipo_de_eje = tipo_de_eje_llanta_montada

                        #? Quitar observaciones                  
                        func.quitar_desgaste(llanta, llanta_rotar)

                        Llanta.objects.bulk_update([llanta, llanta_rotar], [
                            'vehiculo',
                            'posicion', 
                            'tipo_de_eje', 
                            'eje', 
                            ])
                        llantas_rotadas.append(llanta)
                        llantas_rotadas.append(llanta_rotar)
                    print('---------------')        
                    
            
            functions.servicio_vehiculo_guardado(servicio, preguardado_vehiculo)        
            functions.servicio_llanta_desmomtaje(servicio, preguardado_llantas)
            functions.servicio_llanta_servicio(llantas_desmontadas, servicio, preguardado_llantas)
                   
            dict_data = {
                'preguardado_vehiculo': preguardado_vehiculo,
                'preguardado_llantas': preguardado_llantas,
            }
            json_context = json.dumps(dict_data, indent=None, sort_keys=False, default=str)
            
            
        else:
            json_context = json.dumps({'status': 'No se paso un servicio'}, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')