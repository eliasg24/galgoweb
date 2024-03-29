from datetime import date, datetime
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func, Sum
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from calendario.models import Calendario
from dashboards.models import Llanta, Observacion, Perfil, Producto, ServicioVehiculo, Taller, Vehiculo
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
        calendarios = list(calendarios.values(
            'id',
            'horario_start_str',
            'horario_end_str',
            'title',
            'estado',
            'color',
            'hoja',
            'reporte',
            'id_servicio',
            'vehiculo__id',
            'servicio__hoja',
            'servicio__alineacion'

            ))
        
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
        compania_act = perfil.compania
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
            vehiculos_lista = [vehiculo]
            
            km_imposible = False
            km_montado = None
            for vehicule in preguardado_vehiculo:
                if 'alinearVehiculo' in vehicule:
                    vehiculo.fecha_ultima_alineacion = date.today()
                
                if 'km_imposible' in vehicule:
                    if 'km_imposible' == 'True':
                        km_montado = None
                        km_imposible = True
                    else:
                        km_montado = int(vehicule['km_vehiculo'])
                        vehiculo.km = km_montado
                        vehiculo.save()
                
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
                    
                    presion_establecida = func.presion_establecida(llanta)
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
                    llanta_nueva.km_montado = km_montado
                    llanta_nueva.presion_actual = presion_establecida

                    #? Se actualizan las llantas respectivamente
                    Llanta.objects.bulk_update([llanta_nueva], [
                        'vehiculo',
                        'posicion',
                        'ubicacion',
                        'aplicacion',
                        'tipo_de_eje',
                        'eje',
                        'inventario',
                        'km_montado',
                        'presion_actual'
                        ])

                    Llanta.objects.bulk_update([llanta], [
                        'taller', 'inventario'
                        ])
                    llantas_desmontadas.append(llanta)
                    
                    
                    func.quitar_llanta_de_carritos(llanta_nueva, perfil)
                    func.check_dualizacion(llanta_nueva)
                    func.check_dif_presion_duales(llanta_nueva)
                    func.quitar_todo_observaciones(llanta)
                    
                    print('---------------')
                    
            for data in preguardado_llantas:
                if data['tipoServicio'] == 'sr':
                    print('Servicio')
                    #?Se llama la llanta
                    llanta = Llanta.objects.get(pk=data['llanta'])
                    #? Se verifican que servicios se realizaron
                    srvcarretera = True if data['srvcarretera'] == 'True' else False
                    inflar = True if data['inflar'] == 'True' else False
                    balancear = True if data['balancear'] == 'True' else False
                    reparar = True if data['reparar'] == 'True' else False
                    valvula = True if data['valvula'] == 'True' else False
                    costado = True if data['costado'] == 'True' else False

                    rotar = data['rotar'] if data['rotar'] != 'False' else False

                    print(f'srvcarretera:{srvcarretera}')
                    print(f'inflar:{inflar}')
                    print(f'balancear:{balancear}')
                    print(f'reparar:{reparar}')
                    print(f'valvula:{valvula}')
                    print(f'costado:{costado}')

                    print(f'rotar:{rotar}')

                    #? Servicios
                    if srvcarretera:
                        producto, created = Producto.objects.get_or_create(producto ='CAMBIO EN CARRETERA NULL NULL NULL', defaults={
                            'producto': 'CAMBIO EN CARRETERA NULL NULL NULL',
                            'compania': compania_act,
                            'marca': 'NULL',
                            'dibujo': 'NULL',
                            'rango': 'NULL',
                            'dimension': 'NULL',
                            'profundidad_inicial': 25,
                            'aplicacion': 'Dirección',
                            'vida': 'Nueva',
                            'precio': 0,
                            'km_esperado': 0,
                        }
                        )

                        llanta_nueva = Llanta.objects.create(
                            numero_economico = f'{vehiculo.numero_economico}{llanta.eje}{llanta.posicion}',
                            compania = llanta.compania,
                            vehiculo = llanta.vehiculo,
                            ubicacion = llanta.ubicacion,
                            aplicacion = llanta.aplicacion,
                            vida = 'Nueva',
                            tipo_de_eje = llanta.tipo_de_eje,
                            eje = llanta.eje,
                            posicion = llanta.posicion,
                            nombre_de_eje = llanta.nombre_de_eje,
                            presion_actual = func.presion_establecida(llanta),
                            profundidad_izquierda = llanta.profundidad_izquierda,
                            profundidad_central = llanta.profundidad_central,
                            profundidad_derecha = llanta.profundidad_derecha,
                            km_montado = None,
                            producto = producto,
                            inventario = llanta.inventario,
                            fecha_de_entrada_inventario = timezone.now(),
                        )
                        llanta_nueva.numero_economico = llanta_nueva.numero_economico + str(llanta_nueva.id)
                        llanta.inventario = 'Archivado'
                        llanta.numero_economico = llanta.numero_economico + 'Archivado'
                        Llanta.objects.bulk_update([llanta, llanta_nueva], ['numero_economico', 'inventario'])
                        llanta = None
                        llanta = llanta_nueva
                        
                    
                    if inflar:
                        print('Se inflo')
                        presion_establecida = func.presion_establecida(llanta)
                        llanta.presion_actual = presion_establecida
                        presion = Observacion.objects.get(observacion = 'Baja presión')
                        alta_presion = Observacion.objects.get(observacion = 'Alta presion')
                        mala_entrada = Observacion.objects.get(observacion = 'Mala entrada')
                        doble_mala_entrada = Observacion.objects.get(observacion = 'Doble mala entrada')
                        llanta.observaciones.remove(presion)
                        llanta.observaciones.remove(alta_presion)
                        llanta.observaciones.remove(mala_entrada)
                        llanta.observaciones.remove(doble_mala_entrada)
                        
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

                        #? Corregir presiones
                        presion_establecida_montada= func.presion_establecida(llanta)
                        presion_establecida_rotar = func.presion_establecida(llanta_rotar)
                        print(f'presion_establecida_montada {presion_establecida_montada}')
                        print(f'presion_establecida_rotar {presion_establecida_rotar}')
                        llanta.presion_actual = presion_establecida_montada
                        llanta_rotar.presion_actual = presion_establecida_rotar
                        
                        Llanta.objects.bulk_update([llanta, llanta_rotar], [
                            'posicion', 
                            'tipo_de_eje', 
                            'eje', 
                            'presion_actual'
                            ])
                        llantas_rotadas.append(llanta)
                        llantas_rotadas.append(llanta_rotar)
                        
                        func.quitar_todo_de_presion(llanta)
                        func.quitar_todo_de_presion(llanta_rotar)
                        
                        func.check_dualizacion(llanta_rotar)
                        func.check_dif_presion_duales(llanta_rotar)

                    #? Rotar en diferente vehiculo
                    if rotar == 'otro':
                        print('Rotar en diferentes vehiculo')
                        id_llanta_rotar = int(data['llanta_rotar'])
                        llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)

                        if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                            continue
                        
                        km_imposible_otro = data['km_imposible_otro']
                        if km_imposible_otro == 'True':
                            km_montado_otro = None
                        else:
                            km_montado_otro = int(data['km_montado_otro'])
                        
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
                        llanta.km_montado = km_montado_otro
                        
                        #? Llanta a rotar
                        llanta_rotar.vehiculo = vehiculo_llanta_montada
                        llanta_rotar.posicion = posicion_llanta_montada
                        llanta_rotar.eje = eje_llanta_montada
                        llanta_rotar.tipo_de_eje = tipo_de_eje_llanta_montada
                        llanta_rotar.km_montado = km_montado

                        #? Quitar observaciones                  
                        func.quitar_desgaste(llanta, llanta_rotar)

                        Llanta.objects.bulk_update([llanta, llanta_rotar], [
                            'vehiculo',
                            'posicion', 
                            'tipo_de_eje', 
                            'eje', 
                            'km_montado'
                            ])
                        llantas_rotadas.append(llanta)
                        llantas_rotadas.append(llanta_rotar)
                        if vehiculo_llanta_montada not in vehiculos_lista:
                            vehiculos_lista.append(vehiculo_llanta_montada)
                        func.quitar_todo_de_presion(llanta)
                        func.quitar_todo_de_presion(llanta_rotar)
                        
                        func.check_dualizacion(llanta_rotar)
                        func.check_dif_presion_duales(llanta_rotar)
                        
                        func.check_dualizacion(llanta)
                        func.check_dif_presion_duales(llanta)
                    print('---------------')        
                    
            
            functions.servicio_vehiculo_guardado(servicio, preguardado_vehiculo)        
            functions.servicio_llanta_desmomtaje(servicio, preguardado_llantas)
            functions.servicio_llanta_servicio(llantas_desmontadas, servicio, preguardado_llantas)
            func.guardar_mensaje_calendario(servicio)
            #? Rectificar observaciones deñ vehiculo
            func.rectificar_observaciones_vehiculo(vehiculos_lista) 
            dict_data = {
                'preguardado_vehiculo': preguardado_vehiculo,
                'preguardado_llantas': preguardado_llantas,
            }
            json_context = json.dumps(dict_data, indent=None, sort_keys=False, default=str)
            
            
        else:
            json_context = json.dumps({'status': 'No se paso un servicio'}, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')