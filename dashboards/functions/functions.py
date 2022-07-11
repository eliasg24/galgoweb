#Python
from concurrent.futures import thread
import json
import threading

# Django
from django.contrib import auth
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.core.files import File
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models.aggregates import Min, Max, Count
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest
from django.forms import DurationField
from django.utils import timezone
from calendario.models import Calendario


# Utilities
from dashboards.models import Aplicacion, Bitacora, Bitacora_Pro, Compania, HistoricoLlanta, Inspeccion, Llanta, LlantasSeleccionadas, Observacion, Perfil, ServicioLlanta, ServicioVehiculo, Taller, Ubicacion, Vehiculo, Producto, FTP
from datetime import date, datetime, timedelta
from heapq import nlargest
from itertools import count
import math
import matplotlib.pyplot as plt 
import numpy as np
from random import sample, randint, uniform, random
from sklearn.metrics import r2_score
import pandas as pd
import os
import statistics



class DiffDays(Func):
    function = 'DATE_PART'
    template = "%(function)s('day', %(expressions)s)"

class CastDate(Func):
    function = 'date_trunc'
    template = "%(function)s('day', %(expressions)s)"    

def archivar_taller(POST, pk, servicio_vehiculo):
    vehiculo_con_ejes = vehiculo_con_ejes_acomodados(pk)
    lista_itenciones = []
    intenciones_acomodadas = []
    intenciones_vehiculo = []
    #print(POST)
    #? Acciones del vehiculo
    vehiculo = Vehiculo.objects.get(pk = pk)
    try:
        acciones_vehiculo = json.loads(POST.getlist('vehiculo')[0])
    except:
        acciones_vehiculo = []
    if 'alinearVehiculo' in acciones_vehiculo:
        intenciones_vehiculo.append({'alinearVehiculo': 'True'})
        
    try:
        dataPOST = json.loads(POST.getlist('data')[0])
    except:
        dataPOST = []
    for data in dataPOST:
        if data['tipoServicio'] == 'desmontaje':
            print('Desmontaje')
            #? Se llama la llanta actual
            llanta = Llanta.objects.get(pk=data['llantaId'])
            vehiculo = llanta.vehiculo
                            
            #? Se llama la llanta a montar
            nuevaLlanta = data['nuevaLlanta']
            llanta_nueva = Llanta.objects.get(numero_economico = nuevaLlanta)
            
            #? Se obtienen los datos del desmontaje
            razon = data['razon']
            almacen_desmontaje = data['almacen_desmontaje']
            taller_desmontaje = Taller.objects.get(id = int(data['taller_desmontaje']))
            
            lista_itenciones.append({
                'tipoServicio': 'desmontaje',
                'llanta': llanta.id,
                'llanta_nueva': llanta_nueva.id,
                'razon': razon,
                'taller_desmontaje': taller_desmontaje.id
                })
        
     
    for data in dataPOST:
        if data['tipoServicio'] == 'sr':
            print('Servicio')
            #?Se llama la llanta
            llanta = Llanta.objects.get(pk=data['llantaId'])
            #? Se verifican que servicios se realizaron
            inflar = True if data['inflar'] == 'on' else False
            balancear = True if data['balancear'] == 'on' else False
            reparar = True if data['reparar'] == 'on' else False
            valvula = True if data['valvula'] == 'on' else False
            costado = True if data['costado'] == 'on' else False
            
            rotar = data['rotar'] if data['rotar'] != 'no' else False
            id_llanta_rotar = ''
            #? Rotar en el mismo vehiculo
            if rotar == 'mismo':
                print('Rotar en el mismo vehiculo')
                id_llanta_rotar = int(data['origenLlanta'])
                llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)
                                  
            #? Rotar en diferente vehiculo
            if rotar == 'otro':
                print('Rotar en diferentes vehiculo')
                id_llanta_rotar = int(data['llantaOrigen'])
                llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)
            
            lista_itenciones.append({
                    'tipoServicio': 'sr',
                    'llanta': llanta.id,
                    'inflar': str(inflar),
                    'balancear': str(balancear),
                    'reparar': str(reparar),
                    'valvula': str(valvula),
                    'costado': str(costado),
                    'rotar': str(rotar),
                    'llanta_rotar': id_llanta_rotar
                    })
    print('-------------')
    
    for vehiculo in vehiculo_con_ejes:
        for ejes in vehiculo['ejes']:
            for llanta in ejes:
                intencion_temp = {}
                for intencion in lista_itenciones:
                    if intencion['llanta'] == llanta['llanta'].id:
                        intencion_temp = intencion
                intenciones_acomodadas.append(intencion_temp)
                
    print(acciones_vehiculo)
    print(dataPOST)
    print(lista_itenciones)
    print()
    print(intenciones_acomodadas)
    
    servicio_vehiculo.preguardado_llantas = str(intenciones_acomodadas)
    servicio_vehiculo.preguardado_vehiculo = str(intenciones_vehiculo)
    servicio_vehiculo.save()
    calendarioTaller(servicio_vehiculo)

def acomodo_de_llantas_por_vehiculo(llantas, ids_vehiculo:list):
    """Funcion que obtiene un QuerySet de llantas y una lista de ids y los acomoda por vehiculo

    Args:
        llantas (QuerySet): Llantas
        ids_vehiculo (list): Lista de ids de los vehiculos

    Returns:
        llantas_acomodadas [list]: Lista de listas de llantas acomodada por vehiculos
    """
    llantas_acomodadas = []
    for id in ids_vehiculo:
        list_temp = []
        for llanta in llantas:
            if llanta.vehiculo.id == id:
                list_temp.append(llanta)
        llantas_acomodadas.append(list_temp)
    #print(llantas_acomodadas)
    return llantas_acomodadas

def acomodo_ejes_vehicle(vehiculos_llantas_acomodadas:list):
    """_summary_

    Args:
        vehiculos_llantas_acomodadas (list): _description_

    Returns:
        list: Lista que contiene los diccionarios de los vehiculos acomodados
    """
    vehiculos_acomodados = []
    #Check de presion y profundidades
    baja_presion = Observacion.objects.get(observacion = 'Baja presión') #?Rojo
    alta_presion = Observacion.objects.get(observacion = 'Alta presion') #?Amarillo
    baja_profundidad = Observacion.objects.get(observacion = 'Baja profundidad') #?Rojo
    en_punto_de_retiro = Observacion.objects.get(observacion = 'En punto de retiro') #? Amarillo
    #Check de desgastes
    d_alta_presion = Observacion.objects.get(observacion = 'Desgaste alta presión') #?Amarillo
    d_costilla_interna = Observacion.objects.get(observacion = 'Desgaste  costilla interna') #?Amarillo
    d_inclinado_derecha = Observacion.objects.get(observacion = 'Desgaste inclinado a la derecha') #?Amarillo
    d_inclinado_izquierda = Observacion.objects.get(observacion = 'Desgaste inclinado a la izquierda') #?Amarillo
    #Check desdualizacion
    desdualizacion = Observacion.objects.get(observacion = 'Desdualización')
    
    
    #Primero itero en los vehiculos
    for vehiculo in vehiculos_llantas_acomodadas:
        vehiculo_actual = None
        ejes = []
        #Saco una lista con los diversas cantidades de ejes
        for llanta in vehiculo:
            ejes.append(llanta.eje)
        ejes = list(set(ejes))
        ejes_total = []
        #Itero sobre eesos ejes
        for eje in ejes:
            temp_ejes = []
            #Itero sobre las llantas para buscar coincidencia de ejes
            for llanta in vehiculo:
                vehiculo_actual = llanta.vehiculo
                if llanta.eje == eje:
                    #Se obtienen las observaciones
                    observaciones = llanta.observaciones.all()
                    #Se ponen los default de los campos
                    color_presion = 'good'
                    color_profundidad = 'good'
                    ico_desgaste = ''
                    ico_desdualizacion = ''
                    #Se comprueban las condiciones 
                    #Checar presiones
                    if baja_presion in observaciones:
                        color_presion = 'bad'
                    if alta_presion in observaciones:
                        color_presion = 'yellow'
                    #Checar profundidades
                    if baja_profundidad in observaciones:
                        color_profundidad = 'bad'
                    if en_punto_de_retiro in observaciones:
                        color_profundidad = 'yellow'
                    #Checar desgastes
                    if d_alta_presion in observaciones:
                        ico_desgaste = 'active'
                    if d_costilla_interna in observaciones:
                        ico_desgaste = 'active'
                    if d_inclinado_derecha in observaciones:
                        ico_desgaste = 'active'
                    if d_inclinado_izquierda in observaciones:
                        ico_desgaste = 'active'
                    #Check Desdualización
                    if desdualizacion in observaciones:
                        ico_desdualizacion = 'icon-cross'
                    color_middle = color_observaciones_all_one(llanta)
                    
                    temp_ejes.append({
                        'llanta': llanta,
                        'posicion': llanta.posicion,
                        'color_presion': color_presion,
                        'color_profundidad': color_profundidad,
                        'ico_desgaste': ico_desgaste,
                        'ico_desdualizacion': ico_desdualizacion,
                        'color_middle': color_middle,
                        'min_presion': round(min_presion(llanta)),
                        'max_presion': round(max_presion(llanta)),
                    })
            ejes_total.append(temp_ejes)
            dias_sin_inspeccion = 'N/A'
            dias_sin_alinear = 'N/A'
            
            color_dias_inspenccion = 'good'
            color_dias_alinear = 'good'
            color_dias_inflado = 'good'
            hoy = date.today()
            if vehiculo_actual.fecha_ultima_inspeccion != None:
                #print(vehiculo_actual.fecha_ultima_inspeccion)
                dias_sin_inspeccion = (hoy - vehiculo_actual.fecha_ultima_inspeccion).days
            if vehiculo_actual.compania.periodo2_inspeccion != 0:
                #print(vehiculo_actual.compania.periodo2_inspeccion)
                try:
                    if dias_sin_inspeccion > (vehiculo_actual.compania.periodo2_inspeccion * 2):
                        color_dias_inspenccion = 'bad'
                    elif dias_sin_inspeccion > vehiculo_actual.compania.periodo2_inspeccion:
                        color_dias_inspenccion = 'yellow'
                except:
                    pass
                
            if vehiculo_actual.fecha_ultima_alineacion != None:
                #print(vehiculo_actual.fecha_ultima_inspeccion)
                dias_sin_alinear = (hoy - vehiculo_actual.fecha_ultima_alineacion).days   
            
            if vehiculo_actual.dias_alinear != 0:
                #print(vehiculo_actual.dias_alinear)
                try:
                    if dias_sin_alinear > (vehiculo_actual.dias_alinear * 2):
                        color_dias_alinear = 'bad'
                    elif dias_sin_alinear > vehiculo_actual.dias_alinear:
                        color_dias_alinear = 'yellow'
                except:
                    pass 
        dias_sin_inflar = is_valid_dias_sin_inflar(vehiculo_actual)
        if vehiculo_actual.compania.periodo2_inflado != 0:
            try:
                if dias_sin_inflar > (vehiculo_actual.compania.periodo2_inflado * 2):
                    color_dias_inflado = 'bad'
                elif dias_sin_inflar > vehiculo_actual.compania.periodo2_inflado:
                    color_dias_inflado = 'yellow'
            except:
                pass
        
        sp1 = is_sp1(vehiculo_actual)
            
        vehiculos_acomodados.append(
            {
                'vehiculo': vehiculo_actual,
                'ejes':  ejes_total,
                'dias_sin_inspeccion': dias_sin_inspeccion,
                'dias_sin_alinear': dias_sin_alinear,
                'color_dias_inspenccion': color_dias_inspenccion,
                'color_dias_alinear': color_dias_alinear,
                'dias_sin_inflar': dias_sin_inflar,
                'color_dias_inflado': color_dias_inflado,
                'fecha_inflado': vehiculo_actual.fecha_de_inflado,
                'sp1': sp1
            }
        )
    return vehiculos_acomodados

def is_sp1(vehiculo_actual):
    configuracion = vehiculo_actual.configuracion
    if 'SP1' in configuracion:
        print(vehiculo_actual)
        print(True)
        return True
    else:
        print(vehiculo_actual)
        print(False)
        return False
    

def is_valid_dias_sin_inflar(vehiculo_actual):
    """Funcion que determina si la lista de dias sin inflar es valisa(Que no este vacia)

    Args:
        dias_sin_inflar (list): Lista de los dias con inflado

    Returns:
        _type_: Cadena o fecha que resulto
    """
    if vehiculo_actual.fecha_de_inflado != None:
        return (datetime.now(timezone.utc) - vehiculo_actual.fecha_de_inflado).days
        #return max(dias_sin_inflar)
    else:
        return 'N/A'


def acomodo_pocisiones_vehicle(vehiculos):
    """Funcion que toma los vehiculos y acomoda sus ejes por posicion.

    Args:
        vehiculos (list): Lista de las llantas acomodadas 

    Returns:
        vehiculos_ejes_acomodados list: Lista de diccionarios con los vehiculos y sus ejes acomodados
    """
    #Se genera una lista donde se guardaran los vehiculos
    vehiculos_ejes_acomodados = []
    #Se itera en los vehiculos iniciales
    for vehiculo in vehiculos:
        #Se crea una lista donde se almacenaran los ejes acomodados
        ejes = []
        #Se itera en los ejes
        for eje in vehiculo['ejes']:
            #Se verifica que tipo de eje es
            if len(eje) == 2:
                eje_temp = ['', '']
                for llanta in eje:
                    if 'LI' in llanta['posicion']:
                        eje_temp[0] = llanta
                    elif 'RI' in llanta['posicion']:
                        eje_temp[1] = llanta
                ejes.append(eje_temp)
                
            if len(eje) == 4:
                eje_temp = ['', '', '', '']
                for llanta in eje:
                    if 'LO' in llanta['posicion']:
                        eje_temp[0] = llanta
                    elif 'LI' in llanta['posicion']:
                        eje_temp[1] = llanta
                    elif 'RI' in llanta['posicion']:
                        eje_temp[2] = llanta
                    elif 'RO' in llanta['posicion']:
                        eje_temp[3] = llanta
                ejes.append(eje_temp)
                             
        vehiculos_ejes_acomodados.append({
            'vehiculo': vehiculo['vehiculo'],
            'ejes': ejes,
            'dias_sin_inspeccion': vehiculo['dias_sin_inspeccion'],
            'dias_sin_alinear': vehiculo['dias_sin_alinear'],
            'color_dias_inspenccion': vehiculo['color_dias_inspenccion'],
            'color_dias_alinear': vehiculo['color_dias_alinear'],
            'dias_sin_inflar': vehiculo['dias_sin_inflar'],
            'color_dias_inflado': vehiculo['color_dias_inflado'],
            'fecha_inflado': vehiculo['fecha_inflado'],
            'sp1': vehiculo['sp1']
            
        })
        
    return vehiculos_ejes_acomodados


def acomodo_ejes(ejes_no_ordenados):
    ejes = []
    for eje in ejes_no_ordenados:
        if len(eje) == 2:
            lista_temp = ['', '']
            for llanta_act in eje:
                if 'LI' in llanta_act[0].posicion:
                    lista_temp[0] = llanta_act
                    
                elif 'RI' in llanta_act[0].posicion:
                    lista_temp[1] = llanta_act
            ejes.append(lista_temp)
            print(' 0---0')
        
        else:
            lista_temp = ['', '', '', '']
            for llanta_act in eje:
                if 'LO' in llanta_act[0].posicion:
                    lista_temp[0] = llanta_act
                elif 'LI' in llanta_act[0].posicion:
                    lista_temp[1] = llanta_act
                elif 'RI' in llanta_act[0].posicion:
                    lista_temp[2] = llanta_act
                elif 'RO' in llanta_act[0].posicion:
                    lista_temp[3] = llanta_act
            ejes.append(lista_temp)
            print('00---00')
    return ejes

def actualizar_km_actual(llanta_actual, llanta_referencia, vehiculo, vehiculo_referencia):
    if vehiculo_referencia.km != None:
        km_viejo = float(vehiculo_referencia.km) - float(llanta_actual.km_montado)
        km_nuevo = float(vehiculo.km) - float(llanta_actual.km_montado)
        km_dif = km_nuevo - km_viejo
        if llanta_actual.km_actual!= None:
            km = llanta_actual.km_actual + km_dif
        else:
            km = km_dif
        return km
    else:
        km_nuevo = float(vehiculo.km) - float(llanta_actual.km_montado)
        if llanta_actual.km_actual!= None:
            km = llanta_actual.km_actual + km_nuevo
        else:
            km = km_nuevo
        return km

def actualizar_km_actual_no_km_montado(primer_inspeccion, ultima_inspeccion):
    #Datos primera inspeccion
    primer_profundidad = min_profundidad(primer_inspeccion)
    primer_km = primer_inspeccion.km_vehiculo
    #Datos ultima inspeccion
    ultima_profundidad = min_profundidad(ultima_inspeccion)
    ultima_km = ultima_inspeccion.km_vehiculo
    #Calculos de variables
    mm_desgastados = primer_profundidad - ultima_profundidad
    km_recorrido = ultima_km - primer_km
    km_x_mm = km_recorrido / mm_desgastados
    profundidad_inicial = primer_inspeccion.llanta.producto.profundidad_inicial
    #Km teorico
    km_teorico = (profundidad_inicial - ultima_profundidad) * km_x_mm
    return km_teorico
    
def all_num_eco_compania(compania, llantas_actuales):
    num_eco = []
    llantas = Llanta.objects.filter(compania = compania)
    for llanta in llantas:
        if llanta not in llantas_actuales:
            num_eco.append(llanta.numero_economico)
    return num_eco

def actualizar_vida(llanta):
    vida = llanta.vida
    if vida == 'Nueva':
        return '1R'
    elif vida == '1R':
        return '2R'
    elif vida == '2R':
        return '3R'
    elif vida == '3R':
        return '4R'
    elif vida == '4R':
        return '5R'

def cambio_de_vida(llanta, llanta_futuro):
    try:
        historico_llanta = HistoricoLlanta.objects.get(num_eco = llanta)
        if llanta.vida == 'Nueva':
            historico_llanta.casco_nuevo = llanta.producto
            historico_llanta.km_recorrido_nuevo = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
            
        elif llanta.vida == '1R':
            if historico_llanta.km_recorrido_nuevo == None:
                historico_llanta.renovado_1 = llanta.producto
                historico_llanta.km_recorrido_1 = llanta_futuro.km_actual
                historico_llanta.km_total = llanta_futuro.km_actual
            else:
                historico_llanta.renovado_1 = llanta.producto
                historico_llanta.km_recorrido_1 = llanta_futuro.km_actual - historico_llanta.km_total
                historico_llanta.km_total = llanta_futuro.km_actual
                
        elif llanta.vida == '2R':
            if historico_llanta.km_recorrido_1 == None:
                historico_llanta.renovado_2 = llanta.producto
                historico_llanta.km_recorrido_2 = llanta_futuro.km_actual
                historico_llanta.km_total = llanta_futuro.km_actual
            else:
                historico_llanta.renovado_2 = llanta.producto
                historico_llanta.km_recorrido_2 = llanta_futuro.km_actual  - historico_llanta.km_total
                historico_llanta.km_total = llanta_futuro.km_actual
            
        elif llanta.vida == '3R':
            if historico_llanta.km_recorrido_2 == None:
                historico_llanta.renovado_3 = llanta.producto
                historico_llanta.km_recorrido_3 = llanta_futuro.km_actual
                historico_llanta.km_total = llanta_futuro.km_actual
            else:
                historico_llanta.renovado_3 = llanta.producto
                historico_llanta.km_recorrido_3 = llanta_futuro.km_actual - historico_llanta.km_total
                historico_llanta.km_total = llanta_futuro.km_actual
            
        elif llanta.vida == '4R':
            if historico_llanta.km_recorrido_3 == None:
                historico_llanta.renovado_4 = llanta.producto
                historico_llanta.km_recorrido_4 = llanta_futuro.km_actual
                historico_llanta.km_total = llanta_futuro.km_actual
            else:
                historico_llanta.renovado_4 = llanta.producto
                historico_llanta.km_recorrido_4 = llanta_futuro.km_actual - historico_llanta.km_total
                historico_llanta.km_total = llanta_futuro.km_actual
            
        elif llanta.vida == '5R':
            if historico_llanta.km_recorrido_4 == None:
                historico_llanta.renovado_5 = llanta.producto
                historico_llanta.km_recorrido_5 = llanta_futuro.km_actual
                historico_llanta.km_total = llanta_futuro.km_actual
            else:
                historico_llanta.renovado_5 = llanta.producto
                historico_llanta.km_recorrido_5 = llanta_futuro.km_actual - historico_llanta.km_total
                historico_llanta.km_total = llanta_futuro.km_actual
        historico_llanta.save()
    except:
        historico_llanta = HistoricoLlanta.objects.create(num_eco = llanta)
        print('crear')
        print(llanta.vida)
        if llanta.vida == 'Nueva':
            historico_llanta.casco_nuevo = llanta.producto
            historico_llanta.km_recorrido_nuevo = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
        elif llanta.vida == '1R':
            historico_llanta.renovado_1 = llanta.producto
            historico_llanta.km_recorrido_1 = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
        elif llanta.vida == '2R':
            historico_llanta.renovado_2 = llanta.producto
            historico_llanta.km_recorrido_2 = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
        elif llanta.vida == '3R':
            historico_llanta.renovado_3 = llanta.producto
            historico_llanta.km_recorrido_3 = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
        elif llanta.vida == '4R':
            historico_llanta.renovado_4 = llanta.producto
            historico_llanta.km_recorrido_4 = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
        elif llanta.vida == '5R':
            historico_llanta.renovado_5 = llanta.producto
            historico_llanta.km_recorrido_5 = llanta_futuro.km_actual
            historico_llanta.km_total = llanta_futuro.km_actual
        historico_llanta.save()
    
def clases_mas_frecuentes(vehiculo_fecha, compania):
    try:
        vehiculos = Vehiculo.objects.filter(compania=compania)
        clases_compania = []
        for vehiculo in vehiculos:
            if not(vehiculo.clase in clases_compania):
                clases_compania.append(vehiculo.clase.capitalize())
        clases = {}
        for v in vehiculo_fecha:
            clase = v.clase.capitalize()
            if clase in clases:
                clases[clase] += 1
            else:
                clases[clase] = 1
        if 2 < len(clases) <= 8:
            clases_mayores = nlargest(len(clases), clases, key=clases.get)
        elif 0 <= len(clases) <= 2:
            for clase_compania in clases_compania:
                if not(clase_compania in clases):
                    clases[clase_compania] = 0
            clases_mayores = nlargest(8, clases, key=clases.get)
        else:
            clases_mayores = nlargest(8, clases, key=clases.get)
        for c in clases.copy():
            if c in clases_mayores:
                vehiculo_clase = Vehiculo.objects.filter(clase__icontains=c.upper(), compania=compania)
                clases[c] = round((clases[c] / vehiculo_clase.count()) * 100, 2)
            else:
                clases.pop(c)
        return clases
    except:
        return None


def check_presion_pulpo(llanta, min_presion, max_presion, condicional):
    presion = int(llanta.presion_actual)
    alta = Observacion.objects.get(observacion='Alta presion')
    baja = Observacion.objects.get(observacion='Baja presión')
    mala_entrada = Observacion.objects.get(observacion='Mala entrada')
    doble_mala_entrada = Observacion.objects.get(observacion='Doble mala entrada')
    llanta.observaciones.remove(alta)
    llanta.observaciones.remove(baja)
    print("llanta", llanta)
    print("mala_entrada", mala_entrada)
    print("doble_mala_entrada", doble_mala_entrada)
    print(presion)
    if presion < min_presion:
        llanta.observaciones.add(baja)
        llanta.vehiculo.observaciones_llanta.add(baja)
        if mala_entrada in llanta.observaciones.all() or doble_mala_entrada in llanta.observaciones.all() :
            llanta.observaciones.add(doble_mala_entrada)
        else:
            llanta.observaciones.add(mala_entrada)
        if mala_entrada in llanta.vehiculo.observaciones_llanta.all() or doble_mala_entrada in llanta.vehiculo.observaciones_llanta.all() :
            llanta.vehiculo.observaciones_llanta.add(doble_mala_entrada)
            condicional = False
        else:
            llanta.vehiculo.observaciones_llanta.add(mala_entrada)
            condicional = False
            
    elif presion > max_presion:
        llanta.observaciones.add(alta)
        llanta.vehiculo.observaciones_llanta.add(alta)
        if mala_entrada in llanta.observaciones.all() or doble_mala_entrada in llanta.observaciones.all() :
            llanta.observaciones.add(doble_mala_entrada)
        else:
            llanta.observaciones.add(mala_entrada)
        if mala_entrada in llanta.vehiculo.observaciones_llanta.all() or doble_mala_entrada in llanta.vehiculo.observaciones_llanta.all() :
            condicional = False
            llanta.vehiculo.observaciones_llanta.add(doble_mala_entrada)
        else:
            llanta.vehiculo.observaciones_llanta.add(mala_entrada)
            condicional = False
            llanta.observaciones.add(mala_entrada)
        
    else:
        if condicional:
            llanta.vehiculo.observaciones_llanta.remove(doble_mala_entrada)
        llanta.observaciones.remove(doble_mala_entrada)
        
        if condicional:
            llanta.vehiculo.observaciones_llanta.remove(mala_entrada)
        llanta.observaciones.remove(mala_entrada)
    
    llanta.save()

    return condicional


def aplicaciones_mas_frecuentes(vehiculo_fecha, vehiculos, compania):
    try:
        aplicaciones_compania = []
        for vehiculo in vehiculos:
            if not(vehiculo.aplicacion in aplicaciones_compania):
                aplicaciones_compania.append(vehiculo.aplicacion)
        aplicaciones = {}
        for v in vehiculo_fecha:
            aplicacion = v.aplicacion
            if aplicacion in aplicaciones:
                aplicaciones[aplicacion] += 1
            else:
                aplicaciones[aplicacion] = 1
        if 2 < len(aplicaciones) <= 8:
            aplicaciones_mayores = nlargest(len(aplicaciones), aplicaciones, key=aplicaciones.get)
        elif 0 <= len(aplicaciones) <= 2:
            for aplicacion_compania in aplicaciones_compania:
                if not(aplicacion_compania in aplicaciones):
                    aplicaciones[aplicacion_compania] = 0
            aplicaciones_mayores = nlargest(8, aplicaciones, key=aplicaciones.get)
        else:
            aplicaciones_mayores = nlargest(8, aplicaciones, key=aplicaciones.get)
        for c in aplicaciones.copy():
            if c in aplicaciones_mayores:
                vehiculo_aplicacion = vehiculos.filter(aplicacion=c, compania=compania)
                aplicaciones[c] = round((aplicaciones[c] / vehiculo_aplicacion.count()) * 100, 2)
            else:
                aplicaciones.pop(c)
        return aplicaciones
    except:
        return None

def cant_ejes(vehiculo_acomodado):
    ejes = 0
    for eje in vehiculo_acomodado[0]['ejes']:
        ejes += 1
    return ejes


def cantidad_llantas(configuracion):
    try:
        llantas = 0
        for caracter in configuracion:
            if caracter.isdigit():
                llantas += int(caracter)
        return llantas
    except:
        return 0

def cantidad_llantas_por_eje(configuracion):
    try:
        llantas = []
        for caracter in configuracion:
            if caracter.isdigit():
                llantas.append(int(caracter))
        return llantas
    except:
        return []

def comportamiento_de_desgaste(inspecciones):
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=1)
    regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llanta = regresion.values("llanta").distinct()
    llanta_completa = Llanta.objects.get(id=llanta[0]["llanta"])
    if llanta_completa.km_montado:
        x = []
        y = []
        x.append(llanta_completa.producto.profundidad_inicial)
        y.append(llanta_completa.km_montado)
        km_llanta = regresion.filter(llanta=llanta[0]["llanta"]).values("km_vehiculo")
        for r in km_llanta:
            suma = abs(r["km_vehiculo"] - llanta_completa.km_montado)
            y.append(suma)
        profundidades = regresion.filter(llanta=llanta[0]["llanta"]).values("min_profundidad")
        for p in profundidades:
            x.append(p["min_profundidad"])
        print(x, y)
        valores = {}
        for valor in range(len(x)):
            valores[valor] = [x[valor], y[valor]]
        return valores
    else:
        return None


def color_presion(presion, presion_minima, presion_maxima):
    try:
        if presion >= presion_minima and presion <= presion_maxima:
            color_presion = 'good'
        else:
            color_presion = 'bad'
    except: 
        color_presion = 'bad'
    return color_presion


def color_profundidad(profundidad, punto_de_retiro):
    if profundidad != None:
        if profundidad <=  punto_de_retiro:
            color = 'bad'
        elif profundidad >= (punto_de_retiro + .01) and profundidad <= (punto_de_retiro + 1):
            color = 'yellow'
        else:
            color = 'good'
        return color
    else:
        return 'bad'

def color_observaciones(observaciones):
    rojo = 0
    amarillo = 0
    for obs in observaciones:
        if obs.color == 'Rojo':
             rojo += 1
        elif obs.color == 'Amarillo':
            amarillo += 1
    if rojo > 0:
        color = 'bad'
    elif amarillo > 0:
        color = 'yellow'
    else:
        color = 'good'
    return color
        
def color_observaciones_all(inspeccion_vehiculo):
    inspecciones = Inspeccion.objects.filter(inspeccion_vehiculo = inspeccion_vehiculo)
    colores = []
    observaciones_vehiculo = inspeccion_vehiculo.observaciones.all()
    colores.append(color_observaciones(observaciones_vehiculo))
        
    for ins in inspecciones:
        colores.append(color_observaciones(ins.observaciones.all()))
    if 'bad' in colores:
        return 'bad'
    elif 'yellow' in colores:
        return 'yellow'
    else:
        return 'good'

def color_observaciones_all_one(inspeccion):
    colores = []
    observaciones = inspeccion.observaciones.all()
    for obs in observaciones:
        colores.append(color_observaciones_one(obs))
    if 'bad' in colores:
        return 'bad'
    elif 'yellow' in colores:
        return 'yellow'
    else:
        return 'good'
    
def color_observaciones_one(observacion):
    if observacion.color == 'Rojo':
        return 'bad'
    elif observacion.color == 'Amarillo':
        return 'yellow'
    else:
        return 'good'
    

def contar_dias(fecha):
    fecha_date = datetime.strptime(fecha, "%Y-%m-%d").date()
    hoy = date.today()
    return hoy - fecha_date


def contar_entrada_correcta(vehiculos):
    try:
        entradas = {}
        for vehiculo in vehiculos:
            presion_de_entrada = vehiculo.presion_de_entrada
            presion_establecida_1 = vehiculo.presion_establecida_1
            presion_establecida_2 = vehiculo.presion_establecida_2
            presion_establecida_3 = vehiculo.presion_establecida_3
            presion_establecida_4 = vehiculo.presion_establecida_4
            presion_establecida_5 = vehiculo.presion_establecida_5
            presion_establecida_6 = vehiculo.presion_establecida_6
            presion_establecida_7 = vehiculo.presion_establecida_7
            if presion_de_entrada == 0 or presion_establecida_1 == 0 or presion_establecida_2 == 0 or presion_establecida_3 == 0 or presion_establecida_4 == 0 or presion_establecida_5 == 0 or presion_establecida_6 == 0 or presion_establecida_7 == 0:
                entrada_correcta = 0
            else:
                
                try:
                    entrada_correcta_1 = presion_de_entrada/presion_establecida_1
                except:
                    entrada_correcta_1 = 1
                try:
                    entrada_correcta_2 = presion_de_entrada/presion_establecida_2
                except:
                    entrada_correcta_2 = 1
                try:
                    entrada_correcta_3 = presion_de_entrada/presion_establecida_3
                except:
                    entrada_correcta_3 = 1
                try:
                    entrada_correcta_4 = presion_de_entrada/presion_establecida_4
                except:
                    entrada_correcta_4 = 1
                try:
                    entrada_correcta_5 = presion_de_entrada/presion_establecida_5
                except:
                    entrada_correcta_5 = 1
                try:
                    entrada_correcta_6 = presion_de_entrada/presion_establecida_6
                except:
                    entrada_correcta_6 = 1
                try:
                    entrada_correcta_7 = presion_de_entrada/presion_establecida_7
                except:
                    entrada_correcta_7 = 1
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9:
                entradas[vehiculo.id] = True
        return len(entradas)
    except:
        return None

def contar_entrada_correcta_pro(vehiculos):
    entradas = {}
    for vehiculo in vehiculos:
        configuracion = vehiculo.configuracion
        llantas = cantidad_llantas(configuracion)
        llantas_eje = cantidad_llantas_por_eje(configuracion)
        if llantas >= 2:
            presion_encontrada_1 = vehiculo.ultima_bitacora_pro.presion_de_entrada_1
            presion_establecida_1 = vehiculo.presion_establecida_1
            if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                entrada_correcta_1 = 0
            else:
                entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
            presion_encontrada_2 = vehiculo.ultima_bitacora_pro.presion_de_entrada_2
            if llantas_eje[0] >= 2:
                presion_establecida_2 = vehiculo.presion_establecida_1
            elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                presion_establecida_2 = vehiculo.presion_establecida_2
            if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                entrada_correcta_2 = 0
            else:
                entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
            if llantas >= 4:                    
                presion_encontrada_3 = vehiculo.ultima_bitacora_pro.presion_de_entrada_3
                if llantas_eje[0] >= 3:
                    presion_establecida_3 = vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                    presion_establecida_3 = vehiculo.presion_establecida_2
                if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                    entrada_correcta_3 = 0
                else:
                    entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                presion_encontrada_4 = vehiculo.ultima_bitacora_pro.presion_de_entrada_4
                if llantas_eje[0] >= 4:
                    presion_establecida_4 = vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                    presion_establecida_4 = vehiculo.presion_establecida_2
                if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                    entrada_correcta_4 = 0
                else:
                    entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                if llantas >= 6:      
                    presion_encontrada_5 = vehiculo.ultima_bitacora_pro.presion_de_entrada_5
                    if (llantas_eje[0] + llantas_eje[1]) >= 5:
                        presion_establecida_5 = vehiculo.presion_establecida_2
                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                        presion_establecida_5 = vehiculo.presion_establecida_3
                    if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                        entrada_correcta_5 = 0
                    else:
                        entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                    presion_encontrada_6 = vehiculo.ultima_bitacora_pro.presion_de_entrada_6
                    if (llantas_eje[0] + llantas_eje[1]) >= 6:
                        presion_establecida_6 = vehiculo.presion_establecida_2
                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                        presion_establecida_6 = vehiculo.presion_establecida_3
                    if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                        entrada_correcta_6 = 0
                    else:
                        entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                    if llantas >= 8:
                        presion_encontrada_7 = vehiculo.ultima_bitacora_pro.presion_de_entrada_7
                        if (llantas_eje[0] + llantas_eje[1]) >= 7:
                            presion_establecida_7 = vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                            presion_establecida_7 = vehiculo.presion_establecida_3
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                            presion_establecida_7 = vehiculo.presion_establecida_4
                        if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                            entrada_correcta_7 = 0
                        else:
                            entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                        presion_encontrada_8 = vehiculo.ultima_bitacora_pro.presion_de_entrada_8
                        if (llantas_eje[0] + llantas_eje[1]) >= 8:
                            presion_establecida_8 = vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                            presion_establecida_8 = vehiculo.presion_establecida_3
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                            presion_establecida_8 = vehiculo.presion_establecida_4
                        if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                            entrada_correcta_8 = 0
                        else:
                            entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                        if llantas >= 10:
                            presion_encontrada_9 = vehiculo.ultima_bitacora_pro.presion_de_entrada_9
                            if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                presion_establecida_9 = vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                presion_establecida_9 = vehiculo.presion_establecida_4
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                presion_establecida_9 = vehiculo.presion_establecida_5
                            if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                entrada_correcta_9 = 0
                            else:
                                entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                            presion_encontrada_10 = vehiculo.ultima_bitacora_pro.presion_de_entrada_10
                            if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                presion_establecida_10 = vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                presion_establecida_10 = vehiculo.presion_establecida_4
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                presion_establecida_10 = vehiculo.presion_establecida_5
                            if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                entrada_correcta_10 = 0
                            else:
                                entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                            if llantas >= 12:
                                presion_encontrada_11 = vehiculo.ultima_bitacora_pro.presion_de_entrada_11
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                    presion_establecida_11 = vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                    presion_establecida_11 = vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                    presion_establecida_11 = vehiculo.presion_establecida_5
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                    presion_establecida_11 = vehiculo.presion_establecida_6
                                if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                    entrada_correcta_11 = 0
                                else:
                                    entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                presion_encontrada_12 = vehiculo.ultima_bitacora_pro.presion_de_entrada_12
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                    presion_establecida_12 = vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                    presion_establecida_12 = vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                    presion_establecida_12 = vehiculo.presion_establecida_5
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                    presion_establecida_12 = vehiculo.presion_establecida_6
                                if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                    entrada_correcta_12 = 0
                                else:
                                    entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
        if llantas >= 12:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9 and entrada_correcta_11 >= 0.9 and entrada_correcta_12 >= 0.9:
                entradas[vehiculo.id] = True
        elif llantas >= 10:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9:
                entradas[vehiculo.id] = True
        elif llantas >= 8:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9:
                entradas[vehiculo.id] = True
        elif llantas >= 6:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9:
                entradas[vehiculo.id] = True
        elif llantas >= 4:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9:
                entradas[vehiculo.id] = True
        elif llantas >= 2:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9:
                entradas[vehiculo.id] = True
    return len(entradas)

def contar_mala_entrada(bitacoras):
    try:
        entradas = {}
        for bitacora in bitacoras:
            presion_de_entrada = bitacora.presion_de_entrada
            presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
            presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
            presion_establecida_3 = bitacora.vehiculo.presion_establecida_3
            presion_establecida_4 = bitacora.vehiculo.presion_establecida_4
            presion_establecida_5 = bitacora.vehiculo.presion_establecida_5
            presion_establecida_6 = bitacora.vehiculo.presion_establecida_6
            presion_establecida_7 = bitacora.vehiculo.presion_establecida_7
            try:
                entrada_correcta_1 = presion_de_entrada/presion_establecida_1
            except:
                entrada_correcta_1 = 1
            try:
                entrada_correcta_2 = presion_de_entrada/presion_establecida_2
            except:
                entrada_correcta_2 = 1
            try:
                entrada_correcta_3 = presion_de_entrada/presion_establecida_3
            except:
                entrada_correcta_3 = 1
            try:
                entrada_correcta_4 = presion_de_entrada/presion_establecida_4
            except:
                entrada_correcta_4 = 1
            try:
                entrada_correcta_5 = presion_de_entrada/presion_establecida_5
            except:
                entrada_correcta_5 = 1
            try:
                entrada_correcta_6 = presion_de_entrada/presion_establecida_6
            except:
                entrada_correcta_6 = 1
            try:
                entrada_correcta_7 = presion_de_entrada/presion_establecida_7
            except:
                entrada_correcta_7 = 1

            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9:
                if bitacora.id in entradas:
                    entradas[bitacora.id] += 1
                else:
                    entradas[bitacora.id] = 1
        return len(entradas)
    except:
        return 0

def contar_mala_entrada_pro(bitacoras):
    try:
        entradas = {}
        for bitacora in bitacoras:
            configuracion = bitacora.vehiculo.configuracion
            llantas = cantidad_llantas(configuracion)
            llantas_eje = cantidad_llantas_por_eje(configuracion)
            if llantas >= 2:
                presion_encontrada_1 = bitacora.presion_de_entrada_1
                presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
                if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                    entrada_correcta_1 = 0
                else:
                    entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
                presion_encontrada_2 = bitacora.presion_de_entrada_2
                if llantas_eje[0] >= 2:
                    presion_establecida_2 = bitacora.vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                    presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
                if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                    entrada_correcta_2 = 0
                else:
                    entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
                if llantas >= 4:                    
                    presion_encontrada_3 = bitacora.presion_de_entrada_3
                    if llantas_eje[0] >= 3:
                        presion_establecida_3 = bitacora.vehiculo.presion_establecida_1
                    elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                        presion_establecida_3 = bitacora.vehiculo.presion_establecida_2
                    if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                        entrada_correcta_3 = 0
                    else:
                        entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                    presion_encontrada_4 = bitacora.presion_de_entrada_4
                    if llantas_eje[0] >= 4:
                        presion_establecida_4 = bitacora.vehiculo.presion_establecida_1
                    elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                        presion_establecida_4 = bitacora.vehiculo.presion_establecida_2
                    if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                        entrada_correcta_4 = 0
                    else:
                        entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                    if llantas >= 6:      
                        presion_encontrada_5 = bitacora.presion_de_entrada_5
                        if (llantas_eje[0] + llantas_eje[1]) >= 5:
                            presion_establecida_5 = bitacora.vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                            presion_establecida_5 = bitacora.vehiculo.presion_establecida_3
                        if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                            entrada_correcta_5 = 0
                        else:
                            entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                        presion_encontrada_6 = bitacora.presion_de_entrada_6
                        if (llantas_eje[0] + llantas_eje[1]) >= 6:
                            presion_establecida_6 = bitacora.vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                            presion_establecida_6 = bitacora.vehiculo.presion_establecida_3
                        if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                            entrada_correcta_6 = 0
                        else:
                            entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                        if llantas >= 8:
                            presion_encontrada_7 = bitacora.presion_de_entrada_7
                            if (llantas_eje[0] + llantas_eje[1]) >= 7:
                                presion_establecida_7 = bitacora.vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                                presion_establecida_7 = bitacora.vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                                presion_establecida_7 = bitacora.vehiculo.presion_establecida_4
                            if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                                entrada_correcta_7 = 0
                            else:
                                entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                            presion_encontrada_8 = bitacora.presion_de_entrada_8
                            if (llantas_eje[0] + llantas_eje[1]) >= 8:
                                presion_establecida_8 = bitacora.vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                                presion_establecida_8 = bitacora.vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                                presion_establecida_8 = bitacora.vehiculo.presion_establecida_4
                            if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                                entrada_correcta_8 = 0
                            else:
                                entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                            if llantas >= 10:
                                presion_encontrada_9 = bitacora.presion_de_entrada_9
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                    presion_establecida_9 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                    presion_establecida_9 = bitacora.vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                    presion_establecida_9 = bitacora.vehiculo.presion_establecida_5
                                if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                    entrada_correcta_9 = 0
                                else:
                                    entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                                presion_encontrada_10 = bitacora.presion_de_entrada_10
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                    presion_establecida_10 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                    presion_establecida_10 = bitacora.vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                    presion_establecida_10 = bitacora.vehiculo.presion_establecida_5
                                if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                    entrada_correcta_10 = 0
                                else:
                                    entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                                if llantas >= 12:
                                    presion_encontrada_11 = bitacora.presion_de_entrada_11
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                        presion_establecida_11 = bitacora.vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                        presion_establecida_11 = bitacora.vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                        presion_establecida_11 = bitacora.vehiculo.presion_establecida_5
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                        presion_establecida_11 = bitacora.vehiculo.presion_establecida_6
                                    if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                        entrada_correcta_11 = 0
                                    else:
                                        entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                    presion_encontrada_12 = bitacora.presion_de_entrada_12
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                        presion_establecida_12 = bitacora.vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                        presion_establecida_12 = bitacora.vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                        presion_establecida_12 = bitacora.vehiculo.presion_establecida_5
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                        presion_establecida_12 = bitacora.vehiculo.presion_establecida_6
                                    if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                        entrada_correcta_12 = 0
                                    else:
                                        entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
            if llantas >= 12:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9 or entrada_correcta_11 < 0.9 or entrada_correcta_12 < 0.9:
                    if bitacora.id in entradas:
                        entradas[bitacora.id] += 1
                    else:
                        entradas[bitacora.id] = 1
            elif llantas >= 10:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9:
                    if bitacora.id in entradas:
                        entradas[bitacora.id] += 1
                    else:
                        entradas[bitacora.id] = 1
            elif llantas >= 8:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9:
                    if bitacora.id in entradas:
                        entradas[bitacora.id] += 1
                    else:
                        entradas[bitacora.id] = 1
            elif llantas >= 6:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9:
                    if bitacora.id in entradas:
                        entradas[bitacora.id] += 1
                    else:
                        entradas[bitacora.id] = 1
            elif llantas >= 4:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9:
                    if bitacora.id in entradas:
                        entradas[bitacora.id] += 1
                    else:
                        entradas[bitacora.id] = 1
            elif llantas >= 2:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9:
                    if bitacora.id in entradas:
                        entradas[bitacora.id] += 1
                    else:
                        entradas[bitacora.id] = 1
            else:
                entradas[bitacora.id] = 0
        return len(entradas)
    except:
        return 0

def convertir_fecha(fecha):
    try:
        partes_fecha = fecha.split("/")
        return f"{partes_fecha[2]}/{partes_fecha[1]}/{partes_fecha[0]}"
    except:
        return None

def convertir_fecha2(fecha):
    partes_fecha = fecha.split("-")
    year = int(partes_fecha[0])
    month = int(partes_fecha[1])
    day = int(partes_fecha[2][:2])
    fecha = date(year, month, day)
    return fecha

def convertir_fecha3(fecha):
    partes_fecha = fecha.split("/")
    year = int(partes_fecha[2][:4])
    month = int(partes_fecha[0])
    day = int(partes_fecha[1])
    fecha = date(year, month, day)
    return fecha

def convertir_fecha4(fecha):
    partes_fecha = fecha.split("/")
    year = int(partes_fecha[2][:4])
    month = int(partes_fecha[0])
    day = int(partes_fecha[1])
    fecha = datetime(year, month, day)
    return fecha

def convertir_rango(fecha):
    partes_fecha = fecha.split("-")
    fecha = f"{partes_fecha[0]}/{partes_fecha[1]}/{partes_fecha[2]}"
    return fecha

def convertir_rango2(fecha):
    partes_fecha = fecha.split("-")
    fecha1 = f"{partes_fecha[0][0:2]}/{partes_fecha[0][3:5]}/{partes_fecha[0][6:10]}"
    fecha2 = f"{partes_fecha[1][1:3]}/{partes_fecha[1][4:6]}/{partes_fecha[1][7:11]}"
    return fecha1, fecha2

def cpk_vehiculo_cantidad(cpk_vehiculos):
    try:
        max_v = max(cpk_vehiculos)
        min_v = min(cpk_vehiculos)
        resta = max_v - min_v
        div = resta / 8

        valores = []
        for i in range(9):
            valores.append(round(min_v + (div * i), 4))

        rangos = []
        rango_1 = 0
        rango_2 = 0
        rango_3 = 0
        rango_4 = 0
        rango_5 = 0
        rango_6 = 0
        rango_7 = 0
        rango_8 = 0
        for cpk in cpk_vehiculos:
            if valores[0] <= cpk < valores[1]:
                rango_1 += 1
            elif valores[1] <= cpk < valores[2]:
                rango_2 += 1
            elif valores[2] <= cpk < valores[3]:
                rango_3 += 1
            elif valores[3] <= cpk < valores[4]:
                rango_4 += 1
            elif valores[4] <= cpk < valores[5]:
                rango_5 += 1
            elif valores[5] <= cpk < valores[6]:
                rango_6 += 1
            elif valores[6] <= cpk < valores[7]:
                rango_7 += 1
            elif valores[7] <= cpk <= valores[8]:
                rango_8 += 1
        rangos.append(rango_1)
        rangos.append(rango_2)
        rangos.append(rango_3)
        rangos.append(rango_4)
        rangos.append(rango_5)
        rangos.append(rango_6)
        rangos.append(rango_7)
        rangos.append(rango_8)
    except:
        valores = [0, 0, 0, 0, 0, 0, 0, 0]
        rangos = [0, 0, 0, 0, 0, 0, 0, 0]
    return valores, rangos


def desdualizacion(llantas, periodo):
    relacion = {}
    vehiculos = []
    for llanta in llantas:
        relacion[llanta] = llanta.vehiculo
        if not(llanta.vehiculo in vehiculos):
            vehiculos.append(llanta.vehiculo)
    
    for vehiculo in vehiculos:
        posicion = {}
        dual = {}
        for key, val in relacion.items():
            if vehiculo == val:
                if key.posicion == ("1RI" or "1RO"):
                    if "0" in posicion:
                        dual[key] = posicion["0"]
                    else:
                        posicion["0"] = key
                elif key.posicion == ("1LI" or "1LO"):
                    if "1" in posicion:
                        dual[key] = posicion["1"]
                    else:
                        posicion["1"] = key
                elif key.posicion == ("2RI" or "2RO"):
                    if "2" in posicion:
                        dual[key] = posicion["2"]
                    else:
                        posicion["2"] = key
                elif key.posicion == ("2LI" or "2LO"):
                    if "3" in posicion:
                        dual[key] = posicion["3"]
                    else:
                        posicion["3"] = key
                elif key.posicion == ("4RI" or "4RO"):
                    if "4" in posicion:
                        dual[key] = posicion["4"]
                    else:
                        posicion["4"] = key
                elif key.posicion == ("4LI" or "4LO"):
                    if "5" in posicion:
                        dual[key] = posicion["5"]
                    else:
                        posicion["5"] = key

    eje = {}
    for key, val in dual.items():
        if periodo:
            profundidad_1 = key.min_profundidad
            profundidad_2 = val.min_profundidad
        else:
            profundidad_1 = key.primera_min_profundidad
            profundidad_2 = val.primera_min_profundidad
        if (profundidad_1 - profundidad_2) < -3 or (profundidad_1 - profundidad_2) > 3:
            if key.tipo_de_eje[0] == "S":
                if "direccion" in eje:
                    eje["direccion"] += 1
                else:
                    eje["direccion"] = 1
            elif key.tipo_de_eje[0] == "D":
                if "traccion" in eje:
                    eje["traccion"] += 1
                else:
                    eje["traccion"] = 1
            elif key.tipo_de_eje[0] == "T":
                if "arrastre" in eje:
                    eje["arrastre"] += 1
                else:
                    eje["arrastre"] = 1
            elif key.tipo_de_eje[0] == "C":
                if "loco" in eje:
                    eje["loco"] += 1
                else:
                    eje["loco"] = 1
            elif key.tipo_de_eje[0] == "L":
                if "retractil" in eje:
                    eje["retractil"] += 1
                else:
                    eje["retractil"] = 1

    return eje

def desgaste_profundidad(izquierda, central , derecha, llanta_actual):
    print(izquierda, central , derecha)
    if (izquierda != None and central != None and derecha != None):
        print('hey')
        if not(izquierda == central == derecha):
            print('izq centr der')
            
            if izquierda < central > derecha:
                desgaste_costilla_interna = Observacion.objects.get(observacion = 'Desgaste  costilla interna')
                llanta_actual.observaciones.add(desgaste_costilla_interna)
                print(desgaste_costilla_interna)

            elif izquierda > central < derecha:
                desgaste_alta_presión = Observacion.objects.get(observacion = 'Desgaste alta presión')
                llanta_actual.observaciones.add(desgaste_alta_presión)
                print(desgaste_alta_presión)
                
            elif izquierda == min(izquierda, central, derecha):
                desgaste_inclinado_izquierda = Observacion.objects.get(observacion = 'Desgaste inclinado a la izquierda')
                llanta_actual.observaciones.add(desgaste_inclinado_izquierda)
                print(desgaste_inclinado_izquierda)

            elif derecha == min(izquierda, central, derecha):
                desgaste_inclinado_derecha = Observacion.objects.get(observacion = 'Desgaste inclinado a la derecha')
                llanta_actual.observaciones.add(desgaste_inclinado_derecha)
                print(desgaste_inclinado_derecha)

            
            
    elif izquierda != None and central != None:
        print('izq central')
        if izquierda > central:
            desgaste_inclinado_izquierda = Observacion.objects.get(observacion = 'Desgaste inclinado a la izquierda')
            llanta_actual.observaciones.add(desgaste_inclinado_izquierda)
            print(desgaste_inclinado_izquierda)
        elif izquierda < central:
            desgaste_costilla_interna = Observacion.objects.get(observacion = 'Desgaste  costilla interna')
            llanta_actual.observaciones.add(desgaste_costilla_interna)
            print(desgaste_costilla_interna)
            
    elif central != None and derecha != None:
        print('central derecha')
        if central < derecha:
            desgaste_inclinado_derecha = Observacion.objects.get(observacion = 'Desgaste inclinado a la derecha')
            llanta_actual.observaciones.add(desgaste_inclinado_derecha)
            print(desgaste_inclinado_derecha)
        elif central > derecha:
            desgaste_costilla_interna = Observacion.objects.get(observacion = 'Desgaste  costilla interna')
            llanta_actual.observaciones.add(desgaste_costilla_interna)
            print(desgaste_costilla_interna)
    
    elif izquierda != None and derecha != None:
        print('izq der')
        if izquierda > derecha:
            desgaste_inclinado_derecha = Observacion.objects.get(observacion = 'Desgaste inclinado a la derecha')
            llanta_actual.observaciones.add(desgaste_inclinado_derecha)
            print(desgaste_inclinado_derecha)
        elif izquierda < derecha:
            desgaste_inclinado_izquierda = Observacion.objects.get(observacion = 'Desgaste inclinado a la izquierda')
            llanta_actual.observaciones.add(desgaste_inclinado_izquierda)
            print(desgaste_inclinado_izquierda)
    else:
        print('Ningun caso')

def desgaste_irregular(llantas, periodo):
    if periodo:
        llantas_desgaste_irregular = llantas.select_related("vehiculo__compania").annotate(punto_de_retiro=Case(When(nombre_de_eje="Dirección", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(nombre_de_eje="Tracción", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(nombre_de_eje="Arrastre", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(nombre_de_eje="Loco", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(nombre_de_eje="Retractil", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).values("numero_economico").annotate(min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")).filter(punto_de_retiro__lt=F("max_profundidad")-F("min_profundidad"))
    else:
        llantas_desgaste_irregular = llantas.select_related("vehiculo__compania").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")).filter(punto_de_retiro__gt=F("max_profundidad")-F("min_profundidad")).annotate(nombre_eje=Case(When(llanta_eje="S", then=Value("direccion")),When(llanta_eje="D", then=Value("traccion")),When(llanta_eje="T", then=Value("arrastre")),When(llanta_eje="C", then=Value("loco")),When(llanta_eje="L", then=Value("retractil")), output_field=CharField())).values("nombre_eje").annotate(total=Count("nombre_eje")).values("nombre_eje", "total")
    llantas_desgaste_ejes = llantas_desgaste_irregular.aggregate(direccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Dirección")), traccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Tracción")), arrastre=Count("nombre_de_eje",filter=Q(nombre_de_eje="Arrastre")), loco=Count("nombre_de_eje",filter=Q(nombre_de_eje="Loco")), retractil=Count("nombre_de_eje",filter=Q(nombre_de_eje="Retractil")))
    desgaste_ejes = {k: v for k, v in llantas_desgaste_ejes.items() if v != 0}
    return desgaste_ejes

def desgaste_irregular_producto(llantas):
    llantas_desgaste_irregular = llantas.select_related("vehiculo__compania").annotate(punto_de_retiro=Case(When(nombre_de_eje="Dirección", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(nombre_de_eje="Tracción", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(nombre_de_eje="Arrastre", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(nombre_de_eje="Loco", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(nombre_de_eje="Retractil", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).values("numero_economico").annotate(min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")).filter(punto_de_retiro__lt=F("max_profundidad")-F("min_profundidad")).count()
    resta = llantas.count() - llantas_desgaste_irregular
    try:
        porcentaje = round((resta / llantas.count()) * 100, 2)
    except:
        porcentaje = 0
    return porcentaje

def desgaste_mensual(inspecciones):
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__lte=2, count__gt=0)
    sin_regresion = inspecciones.select_related("llanta__vehiculo__compania").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llanta = sin_regresion.values("llanta").distinct()
    if llanta:
        fechas = sin_regresion.filter(llanta=llanta[0]["llanta"]).aggregate(primera_fecha=Min("fecha_hora"),ultima_fecha=Max("fecha_hora"))
        dias = abs(fechas["ultima_fecha"] - fechas["primera_fecha"]).days
        if dias == 0:
            dias = 1
        #print(dias)
        resta = sin_regresion.filter(llanta=llanta[0]["llanta"]).order_by("fecha_hora").annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).first().min_profundidad - sin_regresion.filter(llanta=llanta[0]["llanta"]).order_by("fecha_hora").annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).last().min_profundidad
        #print(resta)
        diario = resta/dias
        #print(diario)
        dias_30 = sin_regresion.filter(llanta=llanta[0]["llanta"]).order_by("fecha_hora").annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).last().min_profundidad - (diario * 30)
        return round(dias_30, 2)

def distribucion_cantidad(cpks):
    for cpk in cpks:
        if cpks[cpk]:
            min = np.quantile(cpks[cpk], 0)
            q1 = np.quantile(cpks[cpk], 0.25)
            q2 = np.quantile(cpks[cpk], 0.5)
            q3 = np.quantile(cpks[cpk], 0.75)
            max = np.quantile(cpks[cpk], 1)
            
            cpks[cpk] = [min, q1, q2, q3, max]

    return cpks


def doble_entrada(bitacoras, bitacoras2):
    bitacoras = bitacoras.order_by("id")
    entradas = {}
    dobles_entradas = []
    for bitacora in bitacoras:
        presion_de_entrada = bitacora.presion_de_entrada
        presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
        presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
        presion_establecida_3 = bitacora.vehiculo.presion_establecida_3
        presion_establecida_4 = bitacora.vehiculo.presion_establecida_4
        presion_establecida_5 = bitacora.vehiculo.presion_establecida_5
        presion_establecida_6 = bitacora.vehiculo.presion_establecida_6
        presion_establecida_7 = bitacora.vehiculo.presion_establecida_7
        try:
            entrada_correcta_1 = presion_de_entrada/presion_establecida_1
        except:
            entrada_correcta_1 = 1
        try:
            entrada_correcta_2 = presion_de_entrada/presion_establecida_2
        except:
            entrada_correcta_2 = 1
        try:
            entrada_correcta_3 = presion_de_entrada/presion_establecida_3
        except:
            entrada_correcta_3 = 1
        try:
            entrada_correcta_4 = presion_de_entrada/presion_establecida_4
        except:
            entrada_correcta_4 = 1
        try:
            entrada_correcta_5 = presion_de_entrada/presion_establecida_5
        except:
            entrada_correcta_5 = 1
        try:
            entrada_correcta_6 = presion_de_entrada/presion_establecida_6
        except:
            entrada_correcta_6 = 1
        try:
            entrada_correcta_7 = presion_de_entrada/presion_establecida_7
        except:
            entrada_correcta_7 = 1

        if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9:
            if bitacora.vehiculo.id in entradas:
                entradas[bitacora.vehiculo.id] += 1
            else:
                entradas[bitacora.vehiculo.id] = 1

        if bitacora.vehiculo.id in entradas:
            if entradas[bitacora.vehiculo.id] >= 2:
                dobles_entradas.append(bitacora.id)

    primera_bitacora = bitacoras.filter(id__in=dobles_entradas).values("id").annotate(max=Max("fecha_de_inflado")).annotate(mes=(ExtractYear(Now()) - ExtractYear("max")) * 12 + (ExtractMonth(Now()) - ExtractMonth("max")) + 1)
    meses1 = primera_bitacora.values("mes").aggregate(mes1=Count("mes",filter=Q(mes=1)), mes2=Count("mes",filter=Q(mes=2)), mes3=Count("mes",filter=Q(mes=3)), mes4=Count("mes",filter=Q(mes=4)), mes5=Count("mes",filter=Q(mes=5)), mes6=Count("mes",filter=Q(mes=6)), mes7=Count("mes",filter=Q(mes=7)), mes8=Count("mes",filter=Q(mes=8)))
    primera_bitacora = primera_bitacora.values("vehiculo")

    bitacoras2 = bitacoras2.order_by("id")
    for bitacora in bitacoras2:
        mala_entrada = False
        configuracion = bitacora.vehiculo.configuracion
        llantas = cantidad_llantas(configuracion)
        llantas_eje = cantidad_llantas_por_eje(configuracion)
        if llantas >= 2:
            presion_encontrada_1 = bitacora.presion_de_entrada_1
            presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
            if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                entrada_correcta_1 = 0
            else:
                entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
            presion_encontrada_2 = bitacora.presion_de_entrada_2
            if llantas_eje[0] >= 2:
                presion_establecida_2 = bitacora.vehiculo.presion_establecida_1
            elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
            if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                entrada_correcta_2 = 0
            else:
                entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
            if llantas >= 4:                    
                presion_encontrada_3 = bitacora.presion_de_entrada_3
                if llantas_eje[0] >= 3:
                    presion_establecida_3 = bitacora.vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                    presion_establecida_3 = bitacora.vehiculo.presion_establecida_2
                if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                    entrada_correcta_3 = 0
                else:
                    entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                presion_encontrada_4 = bitacora.presion_de_entrada_4
                if llantas_eje[0] >= 4:
                    presion_establecida_4 = bitacora.vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                    presion_establecida_4 = bitacora.vehiculo.presion_establecida_2
                if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                    entrada_correcta_4 = 0
                else:
                    entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                if llantas >= 6:      
                    presion_encontrada_5 = bitacora.presion_de_entrada_5
                    if (llantas_eje[0] + llantas_eje[1]) >= 5:
                        presion_establecida_5 = bitacora.vehiculo.presion_establecida_2
                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                        presion_establecida_5 = bitacora.vehiculo.presion_establecida_3
                    if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                        entrada_correcta_5 = 0
                    else:
                        entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                    presion_encontrada_6 = bitacora.presion_de_entrada_6
                    if (llantas_eje[0] + llantas_eje[1]) >= 6:
                        presion_establecida_6 = bitacora.vehiculo.presion_establecida_2
                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                        presion_establecida_6 = bitacora.vehiculo.presion_establecida_3
                    if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                        entrada_correcta_6 = 0
                    else:
                        entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                    if llantas >= 8:
                        presion_encontrada_7 = bitacora.presion_de_entrada_7
                        if (llantas_eje[0] + llantas_eje[1]) >= 7:
                            presion_establecida_7 = bitacora.vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                            presion_establecida_7 = bitacora.vehiculo.presion_establecida_3
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                            presion_establecida_7 = bitacora.vehiculo.presion_establecida_4
                        if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                            entrada_correcta_7 = 0
                        else:
                            entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                        presion_encontrada_8 = bitacora.presion_de_entrada_8
                        if (llantas_eje[0] + llantas_eje[1]) >= 8:
                            presion_establecida_8 = bitacora.vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                            presion_establecida_8 = bitacora.vehiculo.presion_establecida_3
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                            presion_establecida_8 = bitacora.vehiculo.presion_establecida_4
                        if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                            entrada_correcta_8 = 0
                        else:
                            entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                        if llantas >= 10:
                            presion_encontrada_9 = bitacora.presion_de_entrada_9
                            if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                presion_establecida_9 = bitacora.vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                presion_establecida_9 = bitacora.vehiculo.presion_establecida_4
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                presion_establecida_9 = bitacora.vehiculo.presion_establecida_5
                            if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                entrada_correcta_9 = 0
                            else:
                                entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                            presion_encontrada_10 = bitacora.presion_de_entrada_10
                            if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                presion_establecida_10 = bitacora.vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                presion_establecida_10 = bitacora.vehiculo.presion_establecida_4
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                presion_establecida_10 = bitacora.vehiculo.presion_establecida_5
                            if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                entrada_correcta_10 = 0
                            else:
                                entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                            if llantas >= 12:
                                presion_encontrada_11 = bitacora.presion_de_entrada_11
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_5
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_6
                                if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                    entrada_correcta_11 = 0
                                else:
                                    entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                presion_encontrada_12 = bitacora.presion_de_entrada_12
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_5
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_6
                                if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                    entrada_correcta_12 = 0
                                else:
                                    entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
        if llantas >= 12:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9 or entrada_correcta_11 < 0.9 or entrada_correcta_12 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 10:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 8:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 6:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 4:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 2:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        else:
            entradas[bitacora.vehiculo.id] = 0

        if bitacora.vehiculo.id in entradas:
            if entradas[bitacora.vehiculo.id] >= 2 and mala_entrada:
                dobles_entradas.append(bitacora.id)

    segunda_bitacora = bitacoras2.filter(id__in=dobles_entradas).values("id").annotate(max=Max("fecha_de_inflado")).annotate(mes=(ExtractYear(Now()) - ExtractYear("max")) * 12 + (ExtractMonth(Now()) - ExtractMonth("max")) + 1)
    meses2 = segunda_bitacora.values("mes").aggregate(mes1=Count("mes",filter=Q(mes=1)), mes2=Count("mes",filter=Q(mes=2)), mes3=Count("mes",filter=Q(mes=3)), mes4=Count("mes",filter=Q(mes=4)), mes5=Count("mes",filter=Q(mes=5)), mes6=Count("mes",filter=Q(mes=6)), mes7=Count("mes",filter=Q(mes=7)), mes8=Count("mes",filter=Q(mes=8)))
    segunda_bitacora = segunda_bitacora.values("vehiculo")

    return primera_bitacora, segunda_bitacora, meses1, meses2

def doble_mala_entrada(bitacoras, vehiculos):
    bitacoras = bitacoras.order_by("id")
    entradas = {}
    dobles_entradas = []
    for bitacora in bitacoras:
        presion_de_entrada = bitacora.presion_de_entrada
        presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
        presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
        presion_establecida_3 = bitacora.vehiculo.presion_establecida_3
        presion_establecida_4 = bitacora.vehiculo.presion_establecida_4
        presion_establecida_5 = bitacora.vehiculo.presion_establecida_5
        presion_establecida_6 = bitacora.vehiculo.presion_establecida_6
        presion_establecida_7 = bitacora.vehiculo.presion_establecida_7
        try:
            entrada_correcta_1 = presion_de_entrada/presion_establecida_1
        except:
            entrada_correcta_1 = 1
        try:
            entrada_correcta_2 = presion_de_entrada/presion_establecida_2
        except:
            entrada_correcta_2 = 1
        try:
            entrada_correcta_3 = presion_de_entrada/presion_establecida_3
        except:
            entrada_correcta_3 = 1
        try:
            entrada_correcta_4 = presion_de_entrada/presion_establecida_4
        except:
            entrada_correcta_4 = 1
        try:
            entrada_correcta_5 = presion_de_entrada/presion_establecida_5
        except:
            entrada_correcta_5 = 1
        try:
            entrada_correcta_6 = presion_de_entrada/presion_establecida_6
        except:
            entrada_correcta_6 = 1
        try:
            entrada_correcta_7 = presion_de_entrada/presion_establecida_7
        except:
            entrada_correcta_7 = 1

        if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9:
            if bitacora.vehiculo.id in entradas:
                entradas[bitacora.vehiculo.id] += 1
            else:
                entradas[bitacora.vehiculo.id] = 1

        if bitacora.vehiculo.id in entradas:
            if entradas[bitacora.vehiculo.id] >= 2:
                dobles_entradas.append(bitacora.id)

    try:
        vehiculos = vehiculos.filter(id__in=Bitacora.objects.filter(id__in=dobles_entradas).values("vehiculo"))
        return vehiculos
    except:
        if len(entradas) >= 1:
            return []

def doble_mala_entrada2(bitacoras, vehiculos):
    bitacoras = bitacoras.order_by("id")
    entradas = {}
    dobles_entradas = []
    for bitacora in bitacoras:
        presion_de_entrada = bitacora.presion_de_entrada
        presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
        presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
        presion_establecida_3 = bitacora.vehiculo.presion_establecida_3
        presion_establecida_4 = bitacora.vehiculo.presion_establecida_4
        presion_establecida_5 = bitacora.vehiculo.presion_establecida_5
        presion_establecida_6 = bitacora.vehiculo.presion_establecida_6
        presion_establecida_7 = bitacora.vehiculo.presion_establecida_7
        try:
            entrada_correcta_1 = presion_de_entrada/presion_establecida_1
        except:
            entrada_correcta_1 = 1
        try:
            entrada_correcta_2 = presion_de_entrada/presion_establecida_2
        except:
            entrada_correcta_2 = 1
        try:
            entrada_correcta_3 = presion_de_entrada/presion_establecida_3
        except:
            entrada_correcta_3 = 1
        try:
            entrada_correcta_4 = presion_de_entrada/presion_establecida_4
        except:
            entrada_correcta_4 = 1
        try:
            entrada_correcta_5 = presion_de_entrada/presion_establecida_5
        except:
            entrada_correcta_5 = 1
        try:
            entrada_correcta_6 = presion_de_entrada/presion_establecida_6
        except:
            entrada_correcta_6 = 1
        try:
            entrada_correcta_7 = presion_de_entrada/presion_establecida_7
        except:
            entrada_correcta_7 = 1

        if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9:
            if bitacora.vehiculo.id in entradas:
                entradas[bitacora.vehiculo.id] += 1
            else:
                entradas[bitacora.vehiculo.id] = 1

        if bitacora.vehiculo.id in entradas:
            if entradas[bitacora.vehiculo.id] >= 2:
                dobles_entradas.append(bitacora.id)

    try:
        vehiculos = vehiculos.filter(id__in=Bitacora.objects.filter(id__in=dobles_entradas).values("vehiculo"))
        return vehiculos
    except:
        if len(entradas) >= 1:
            return vehiculos

def doble_mala_entrada_pro(bitacoras, vehiculos):
    bitacoras = bitacoras.order_by("id")
    entradas = {}
    dobles_entradas = []
    for bitacora in bitacoras:
        mala_entrada = False
        configuracion = bitacora.vehiculo.configuracion
        llantas = cantidad_llantas(configuracion)
        llantas_eje = cantidad_llantas_por_eje(configuracion)
        if llantas >= 2:
            presion_encontrada_1 = bitacora.presion_de_entrada_1
            presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
            if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                entrada_correcta_1 = 0
            else:
                entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
            presion_encontrada_2 = bitacora.presion_de_entrada_2
            if llantas_eje[0] >= 2:
                presion_establecida_2 = bitacora.vehiculo.presion_establecida_1
            elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
            if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                entrada_correcta_2 = 0
            else:
                entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
            if llantas >= 4:                    
                presion_encontrada_3 = bitacora.presion_de_entrada_3
                if llantas_eje[0] >= 3:
                    presion_establecida_3 = bitacora.vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                    presion_establecida_3 = bitacora.vehiculo.presion_establecida_2
                if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                    entrada_correcta_3 = 0
                else:
                    entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                presion_encontrada_4 = bitacora.presion_de_entrada_4
                if llantas_eje[0] >= 4:
                    presion_establecida_4 = bitacora.vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                    presion_establecida_4 = bitacora.vehiculo.presion_establecida_2
                if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                    entrada_correcta_4 = 0
                else:
                    entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                if llantas >= 6:      
                    presion_encontrada_5 = bitacora.presion_de_entrada_5
                    if (llantas_eje[0] + llantas_eje[1]) >= 5:
                        presion_establecida_5 = bitacora.vehiculo.presion_establecida_2
                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                        presion_establecida_5 = bitacora.vehiculo.presion_establecida_3
                    if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                        entrada_correcta_5 = 0
                    else:
                        entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                    presion_encontrada_6 = bitacora.presion_de_entrada_6
                    if (llantas_eje[0] + llantas_eje[1]) >= 6:
                        presion_establecida_6 = bitacora.vehiculo.presion_establecida_2
                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                        presion_establecida_6 = bitacora.vehiculo.presion_establecida_3
                    if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                        entrada_correcta_6 = 0
                    else:
                        entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                    if llantas >= 8:
                        presion_encontrada_7 = bitacora.presion_de_entrada_7
                        if (llantas_eje[0] + llantas_eje[1]) >= 7:
                            presion_establecida_7 = bitacora.vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                            presion_establecida_7 = bitacora.vehiculo.presion_establecida_3
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                            presion_establecida_7 = bitacora.vehiculo.presion_establecida_4
                        if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                            entrada_correcta_7 = 0
                        else:
                            entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                        presion_encontrada_8 = bitacora.presion_de_entrada_8
                        if (llantas_eje[0] + llantas_eje[1]) >= 8:
                            presion_establecida_8 = bitacora.vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                            presion_establecida_8 = bitacora.vehiculo.presion_establecida_3
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                            presion_establecida_8 = bitacora.vehiculo.presion_establecida_4
                        if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                            entrada_correcta_8 = 0
                        else:
                            entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                        if llantas >= 10:
                            presion_encontrada_9 = bitacora.presion_de_entrada_9
                            if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                presion_establecida_9 = bitacora.vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                presion_establecida_9 = bitacora.vehiculo.presion_establecida_4
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                presion_establecida_9 = bitacora.vehiculo.presion_establecida_5
                            if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                entrada_correcta_9 = 0
                            else:
                                entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                            presion_encontrada_10 = bitacora.presion_de_entrada_10
                            if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                presion_establecida_10 = bitacora.vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                presion_establecida_10 = bitacora.vehiculo.presion_establecida_4
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                presion_establecida_10 = bitacora.vehiculo.presion_establecida_5
                            if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                entrada_correcta_10 = 0
                            else:
                                entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                            if llantas >= 12:
                                presion_encontrada_11 = bitacora.presion_de_entrada_11
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_5
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                    presion_establecida_11 = bitacora.vehiculo.presion_establecida_6
                                if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                    entrada_correcta_11 = 0
                                else:
                                    entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                presion_encontrada_12 = bitacora.presion_de_entrada_12
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_5
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                    presion_establecida_12 = bitacora.vehiculo.presion_establecida_6
                                if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                    entrada_correcta_12 = 0
                                else:
                                    entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
        if llantas >= 12:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9 or entrada_correcta_11 < 0.9 or entrada_correcta_12 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 10:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 8:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 6:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 4:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        elif llantas >= 2:
            if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9:
                mala_entrada = True
                if bitacora.vehiculo.id in entradas:
                    entradas[bitacora.vehiculo.id] += 1
                else:
                    entradas[bitacora.vehiculo.id] = 1
        else:
            entradas[bitacora.vehiculo.id] = 0

        if bitacora.vehiculo.id in entradas:
            if entradas[bitacora.vehiculo.id] >= 2 and mala_entrada:
                dobles_entradas.append(bitacora.id)
    try:
        vehiculos = vehiculos.filter(id__in=Bitacora_Pro.objects.filter(id__in=dobles_entradas[0]).values("vehiculo"))
        return vehiculos
    except:
        if dobles_entradas:
            return dobles_entradas
        if len(entradas) >= 1:
            return []

def duales(llantas):
    dual = llantas.values("numero_economico", "vehiculo", "posicion").annotate(eje_dual=Substr(F("posicion"),1,2)).values("vehiculo", "eje_dual").order_by().annotate(Count("numero_economico"), llanta_1=Max("numero_economico"), llanta_2=Min("numero_economico")).filter(numero_economico__count=2)
    dual_1 = dual.values_list("llanta_1", flat=True)
    dual_2 = dual.values_list("llanta_2", flat=True)
    llantas_dual_1 = llantas.filter(numero_economico__in=dual_1)
    llantas_dual_2 = llantas.filter(numero_economico__in=dual_2)
    zip_llantas = zip(dual_1, dual_2)
    llantas_dictionary = dict(zip_llantas)
    return llantas_dual_1, llantas_dual_2, llantas_dictionary


def eliminarCarrito(inventario:str, perfil):
    print('Hey simon si entro')
    carrito = LlantasSeleccionadas.objects.get(perfil=perfil, inventario=inventario)
    carrito.llantas.clear()

def eliminarElementoCarrito(id:int, inventario:str, perfil):
    print('Hey simon si entro')
    carrito = LlantasSeleccionadas.objects.get(perfil=perfil, inventario=inventario)
    llanta = Llanta.objects.get(pk=id)
    carrito.llantas.remove(llanta)

def embudo_vidas(llantas):
    llantas_abajo_del_punto = llantas.select_related("vehiculo__compania", "vehiculo__ubicacion").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro"))
    llantas_vida = llantas_abajo_del_punto.aggregate(nueva=Count("vida",filter=Q(vida="Nueva")), r1=Count("vida",filter=Q(vida="1R")), r2=Count("vida",filter=Q(vida="2R")), r3=Count("vida",filter=Q(vida="3R")), r4=Count("vida",filter=Q(vida="4R")), r5=Count("vida",filter=Q(vida="5R")), total=Count("vida"))
    renovado = llantas_abajo_del_punto.annotate(renovado1=Round(Cast(F("vehiculo__ubicacion__rendimiento_de_nueva"),FloatField()) * Cast(llantas_vida["nueva"],FloatField()) / 100), renovado2=Round(Cast(F("vehiculo__ubicacion__rendimiento_de_primera"),FloatField()) * Cast(llantas_vida["r1"],FloatField()) / 100), renovado3=Round(Cast(F("vehiculo__ubicacion__rendimiento_de_segunda"),FloatField()) * Cast(llantas_vida["r2"],FloatField()) / 100), renovado4=Round(Cast(F("vehiculo__ubicacion__rendimiento_de_tercera"),FloatField()) * Cast(llantas_vida["r3"],FloatField()) / 100), renovado5=Round(Cast(F("vehiculo__ubicacion__rendimiento_de_cuarta"),FloatField()) * Cast(llantas_vida["r4"],FloatField()) / 100)).annotate(renovadonuevo=llantas_vida["total"]-F("renovado1")-F("renovado2")-F("renovado3")-F("renovado4")-F("renovado5")).values("renovadonuevo", "renovado1", "renovado2", "renovado3", "renovado4", "renovado5").distinct()
    if not(llantas_abajo_del_punto):
        llantas_abajo_del_punto = 0
    if renovado:
        return llantas_abajo_del_punto, renovado[0]
    else:
        return llantas_abajo_del_punto, {'renovado1': 0, 'renovado2': 0, 'renovado3': 0, 'renovado4': 0, 'renovado5': 0, 'renovadonuevo': 0}

def embudo_vidas_con_regresion(inspecciones, ubicacion, days):
    vehiculos_sospechosos = []
    triplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=2)
    regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=triplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = regresion.values("llanta").distinct()
    for llanta in llantas:
        x = []
        y = []
        primera_fecha = regresion.filter(llanta=llanta["llanta"]).aggregate(primera_fecha=Min("fecha_hora"))
        fecha_llanta = regresion.filter(llanta=llanta["llanta"]).values("fecha_hora")
        for r in fecha_llanta:
            resta = abs(r["fecha_hora"] - primera_fecha["primera_fecha"]).days
            x.append(resta)
        profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
        for p in profundidades:
            y.append(p["min_profundidad"])
        
        x = np.array(x)
        y = np.array(y)

        if len(x) > 2:
            dia = x[-1]
        
            try:

                f = np.polyfit(x, y, 3)
                p = np.poly1d(f)
                termino = []
                for numero in p:
                    numero = round(numero, 4)
                    termino.append(numero)
                regresion_resultado = (termino[0]*(dia**2))+(termino[1]*dia)+termino[2]
                resta = y[0]-regresion_resultado
                diario = resta/dia
                dias_30 = resta - (diario * 30)
                dias_60 = resta - diario * 60
                dias_90 = resta - diario * 90

            except:
                pass

            #vehiculos_sospechosos = regresion.filter(min_profundidad__gt=desgaste_normal).values("llanta__vehiculo").distinct()
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__lte=2, count__gt=0)
    sin_regresion = inspecciones.select_related("llanta__vehiculo__compania").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = sin_regresion.values("llanta").distinct()
    vehiculos_lista = []
    if vehiculos_sospechosos:
        vehiculos_sospechosos_iteracion = True
    else:
        vehiculos_sospechosos_iteracion = False
    dict_vidas = {'renovado1': 0, 'renovado2': 0, 'renovado3': 0, 'renovado4': 0, 'renovado5': 0, 'renovadonuevo': 0}
    lista_llantas = []
    total = 0
    for llanta in llantas:
        l = Llanta.objects.get(id=llanta["llanta"])
        fechas = sin_regresion.filter(llanta=llanta["llanta"]).aggregate(primera_fecha=Min("fecha_hora"),ultima_fecha=Max("fecha_hora"))
        dias = abs(fechas["ultima_fecha"] - fechas["primera_fecha"]).days
        if dias == 0:
            dias = 1

        resta = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").first()) - min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").last())
        diario = resta/dias
        #print(diario)
        dias_30 = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").last()) - (diario * 30)
        dias_60 = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").last()) - (diario * 60)
        dias_90 = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").last()) - (diario * 90)
        """print("llanta", l.numero_economico)
        print("dias", dias)
        print("diario", diario)
        print("dias_30", dias_30)
        print("dias_60", dias_60)
        print("dias_90", dias_90)"""

        """print("llanta", llanta["llanta"])
        print("resta", resta)
        print("dias_30", dias_30)
        print("dias_60", dias_60)
        print("dias_90", dias_90)"""

        if days == 30:
            if dias_30 <= 3:
                lista_llantas.append(l)
                if l.vida == "Nueva":
                    dict_vidas["renovadonuevo"] += 1
                elif l.vida == "1R":
                    dict_vidas["renovado1"] += 1
                elif l.vida == "2R":
                    dict_vidas["renovado2"] += 1
                elif l.vida == "3R":
                    dict_vidas["renovado3"] += 1
                elif l.vida == "4R":
                    dict_vidas["renovado4"] += 1
                elif l.vida == "5R":
                    dict_vidas["renovado5"] += 1
                total += 1
        elif days == 60:
            if dias_60 <= 3:
                lista_llantas.append(l)
                if l.vida == "Nueva":
                    dict_vidas["renovadonuevo"] += 1
                elif l.vida == "1R":
                    dict_vidas["renovado1"] += 1
                elif l.vida == "2R":
                    dict_vidas["renovado2"] += 1
                elif l.vida == "3R":
                    dict_vidas["renovado3"] += 1
                elif l.vida == "4R":
                    dict_vidas["renovado4"] += 1
                elif l.vida == "5R":
                    dict_vidas["renovado5"] += 1
                total += 1
        if days == 90:
            if dias_90 <= 3:
                lista_llantas.append(l)
                if l.vida == "Nueva":
                    dict_vidas["renovadonuevo"] += 1
                elif l.vida == "1R":
                    dict_vidas["renovado1"] += 1
                elif l.vida == "2R":
                    dict_vidas["renovado2"] += 1
                elif l.vida == "3R":
                    dict_vidas["renovado3"] += 1
                elif l.vida == "4R":
                    dict_vidas["renovado4"] += 1
                elif l.vida == "5R":
                    dict_vidas["renovado5"] += 1
                total += 1

    dict_vidas["renovado5"] = round(dict_vidas["renovado4"] * (ubicacion.rendimiento_de_cuarta / 100))
    dict_vidas["renovado4"] = round(dict_vidas["renovado3"] * (ubicacion.rendimiento_de_tercera / 100))
    dict_vidas["renovado3"] = round(dict_vidas["renovado2"] * (ubicacion.rendimiento_de_segunda / 100))
    dict_vidas["renovado2"] = round(dict_vidas["renovado1"] * (ubicacion.rendimiento_de_primera / 100))
    dict_vidas["renovado1"] = round(dict_vidas["renovadonuevo"] * (ubicacion.rendimiento_de_nueva / 100))
    dict_vidas["renovadonuevo"] = round(total - dict_vidas["renovado1"] - dict_vidas["renovado2"] - dict_vidas["renovado3"] - dict_vidas["renovado4"] - dict_vidas["renovado5"])
    return lista_llantas, dict_vidas

def entrada_correcta(vehiculos, vehiculos2):
    try:
        entradas = {}
        loop_entradas = 0
        bitacoras = vehiculos.order_by("-id")
        for bitacora in bitacoras:
            presion_de_entrada = bitacora.presion_de_entrada
            presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
            presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
            presion_establecida_3 = bitacora.vehiculo.presion_establecida_3
            presion_establecida_4 = bitacora.vehiculo.presion_establecida_4
            presion_establecida_5 = bitacora.vehiculo.presion_establecida_5
            presion_establecida_6 = bitacora.vehiculo.presion_establecida_6
            presion_establecida_7 = bitacora.vehiculo.presion_establecida_7
            if presion_de_entrada == 0 or presion_establecida_1 == 0 or presion_establecida_2 == 0 or presion_establecida_3 == 0 or presion_establecida_4 == 0 or presion_establecida_5 == 0 or presion_establecida_6 == 0 or presion_establecida_7 == 0:
                entrada_correcta = 0
            else:
                
                try:
                    entrada_correcta_1 = presion_de_entrada/presion_establecida_1
                except:
                    entrada_correcta_1 = 1
                try:
                    entrada_correcta_2 = presion_de_entrada/presion_establecida_2
                except:
                    entrada_correcta_2 = 1
                try:
                    entrada_correcta_3 = presion_de_entrada/presion_establecida_3
                except:
                    entrada_correcta_3 = 1
                try:
                    entrada_correcta_4 = presion_de_entrada/presion_establecida_4
                except:
                    entrada_correcta_4 = 1
                try:
                    entrada_correcta_5 = presion_de_entrada/presion_establecida_5
                except:
                    entrada_correcta_5 = 1
                try:
                    entrada_correcta_6 = presion_de_entrada/presion_establecida_6
                except:
                    entrada_correcta_6 = 1
                try:
                    entrada_correcta_7 = presion_de_entrada/presion_establecida_7
                except:
                    entrada_correcta_7 = 1

            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9:
                loop_entradas = 0
                entradas[bitacora.id] = True
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora.id] = "Doble"
                else:
                    entradas[bitacora.id] = False

        try:
            bitacoras2 = vehiculos2.order_by("-id")
            for bitacora in bitacoras2:
                configuracion = bitacora.vehiculo.configuracion
                llantas = cantidad_llantas(configuracion)
                llantas_eje = cantidad_llantas_por_eje(configuracion)
                if llantas >= 2:
                    presion_encontrada_1 = bitacora.presion_de_entrada_1
                    presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
                    if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                        entrada_correcta_1 = 0
                    else:
                        entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
                    presion_encontrada_2 = bitacora.presion_de_entrada_2
                    if llantas_eje[0] >= 2:
                        presion_establecida_2 = bitacora.vehiculo.presion_establecida_1
                    elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                        presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
                    if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                        entrada_correcta_2 = 0
                    else:
                        entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
                    if llantas >= 4:                    
                        presion_encontrada_3 = bitacora.presion_de_entrada_3
                        if llantas_eje[0] >= 3:
                            presion_establecida_3 = bitacora.vehiculo.presion_establecida_1
                        elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                            presion_establecida_3 = bitacora.vehiculo.presion_establecida_2
                        if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                            entrada_correcta_3 = 0
                        else:
                            entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                        presion_encontrada_4 = bitacora.presion_de_entrada_4
                        if llantas_eje[0] >= 4:
                            presion_establecida_4 = bitacora.vehiculo.presion_establecida_1
                        elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                            presion_establecida_4 = bitacora.vehiculo.presion_establecida_2
                        if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                            entrada_correcta_4 = 0
                        else:
                            entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                        if llantas >= 6:      
                            presion_encontrada_5 = bitacora.presion_de_entrada_5
                            if (llantas_eje[0] + llantas_eje[1]) >= 5:
                                presion_establecida_5 = bitacora.vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                                presion_establecida_5 = bitacora.vehiculo.presion_establecida_3
                            if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                                entrada_correcta_5 = 0
                            else:
                                entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                            presion_encontrada_6 = bitacora.presion_de_entrada_6
                            if (llantas_eje[0] + llantas_eje[1]) >= 6:
                                presion_establecida_6 = bitacora.vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                                presion_establecida_6 = bitacora.vehiculo.presion_establecida_3
                            if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                                entrada_correcta_6 = 0
                            else:
                                entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                            if llantas >= 8:
                                presion_encontrada_7 = bitacora.presion_de_entrada_7
                                if (llantas_eje[0] + llantas_eje[1]) >= 7:
                                    presion_establecida_7 = bitacora.vehiculo.presion_establecida_2
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                                    presion_establecida_7 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                                    presion_establecida_7 = bitacora.vehiculo.presion_establecida_4
                                if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                                    entrada_correcta_7 = 0
                                else:
                                    entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                                presion_encontrada_8 = bitacora.presion_de_entrada_8
                                if (llantas_eje[0] + llantas_eje[1]) >= 8:
                                    presion_establecida_8 = bitacora.vehiculo.presion_establecida_2
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                                    presion_establecida_8 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                                    presion_establecida_8 = bitacora.vehiculo.presion_establecida_4
                                if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                                    entrada_correcta_8 = 0
                                else:
                                    entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                                if llantas >= 10:
                                    presion_encontrada_9 = bitacora.presion_de_entrada_9
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                        presion_establecida_9 = bitacora.vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                        presion_establecida_9 = bitacora.vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                        presion_establecida_9 = bitacora.vehiculo.presion_establecida_5
                                    if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                        entrada_correcta_9 = 0
                                    else:
                                        entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                                    presion_encontrada_10 = bitacora.presion_de_entrada_10
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                        presion_establecida_10 = bitacora.vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                        presion_establecida_10 = bitacora.vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                        presion_establecida_10 = bitacora.vehiculo.presion_establecida_5
                                    if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                        entrada_correcta_10 = 0
                                    else:
                                        entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                                    if llantas >= 12:
                                        presion_encontrada_11 = bitacora.presion_de_entrada_11
                                        if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_3
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_4
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_5
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_6
                                        if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                            entrada_correcta_11 = 0
                                        else:
                                            entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                        presion_encontrada_12 = bitacora.presion_de_entrada_12
                                        if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_3
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_4
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_5
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_6
                                        if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                            entrada_correcta_12 = 0
                                        else:
                                            entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
                if llantas >= 12:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9 and entrada_correcta_11 >= 0.9 and entrada_correcta_12 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = True
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = False
                elif llantas >= 10:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = True
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = False
                elif llantas >= 8:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = True
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = False
                elif llantas >= 6:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = True
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = False
                elif llantas >= 4:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = True
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = False
                elif llantas >= 2:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = True
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = False
        except:
            pass
        return entradas
    except:
        try:
            presion_encontrada = vehiculos.presion_de_entrada
            presion_establecida = vehiculos.presion_establecida
            entrada_correcta = presion_encontrada/presion_establecida

            if entrada_correcta >= 0.9:
                entradas = "good"
            else:
                entradas = "bad"
            return entradas
        except:
            return None

def entrada_correcta_ambas(bitacoras):
    entradas = {}
    loop_entradas = 0

    for bitacora in bitacoras:
        configuracion = bitacora["vehiculo__configuracion"]
        llantas = cantidad_llantas(configuracion)
        llantas_eje = cantidad_llantas_por_eje(configuracion)
        if llantas >= 2:
            presion_encontrada_1 = bitacora["presion_de_entrada_1"]
            presion_establecida_1 = bitacora["vehiculo__presion_establecida_1"]
            if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                entrada_correcta_1 = 0
            else:
                entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
            presion_encontrada_2 = bitacora["presion_de_entrada_2"]

            if presion_encontrada_2 == None:
                llantas = 2
            else:
                if llantas_eje[0] >= 2:
                    presion_establecida_2 = bitacora["vehiculo__presion_establecida_1"]
                elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                    presion_establecida_2 = bitacora["vehiculo__presion_establecida_2"]
                if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                    entrada_correcta_2 = 0
                else:
                    entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
                if llantas >= 4:                    
                    presion_encontrada_3 = bitacora["presion_de_entrada_3"]
                    if llantas_eje[0] >= 3:
                        presion_establecida_3 = bitacora["vehiculo__presion_establecida_1"]
                    elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                        presion_establecida_3 = bitacora["vehiculo__presion_establecida_2"]
                    if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                        entrada_correcta_3 = 0
                    else:
                        entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                    presion_encontrada_4 = bitacora["presion_de_entrada_4"]
                    if llantas_eje[0] >= 4:
                        presion_establecida_4 = bitacora["vehiculo__presion_establecida_1"]
                    elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                        presion_establecida_4 = bitacora["vehiculo__presion_establecida_2"]
                    if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                        entrada_correcta_4 = 0
                    else:
                        entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                    if llantas >= 6:      
                        presion_encontrada_5 = bitacora["presion_de_entrada_5"]
                        if (llantas_eje[0] + llantas_eje[1]) >= 5:
                            presion_establecida_5 = bitacora["vehiculo__presion_establecida_2"]
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                            presion_establecida_5 = bitacora["vehiculo__presion_establecida_3"]
                        if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                            entrada_correcta_5 = 0
                        else:
                            entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                        presion_encontrada_6 = bitacora["presion_de_entrada_6"]
                        if (llantas_eje[0] + llantas_eje[1]) >= 6:
                            presion_establecida_6 = bitacora["vehiculo__presion_establecida_2"]
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                            presion_establecida_6 = bitacora["vehiculo__presion_establecida_3"]
                        if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                            entrada_correcta_6 = 0
                        else:
                            entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                        if llantas >= 8:
                            presion_encontrada_7 = bitacora["presion_de_entrada_7"]
                            if (llantas_eje[0] + llantas_eje[1]) >= 7:
                                presion_establecida_7 = bitacora["vehiculo__presion_establecida_2"]
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                                presion_establecida_7 = bitacora["vehiculo__presion_establecida_3"]
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                                presion_establecida_7 = bitacora["vehiculo__presion_establecida_4"]
                            if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                                entrada_correcta_7 = 0
                            else:
                                entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                            presion_encontrada_8 = bitacora["presion_de_entrada_8"]
                            if (llantas_eje[0] + llantas_eje[1]) >= 8:
                                presion_establecida_8 = bitacora["vehiculo__presion_establecida_2"]
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                                presion_establecida_8 = bitacora["vehiculo__presion_establecida_3"]
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                                presion_establecida_8 = bitacora["vehiculo__presion_establecida_4"]
                            if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                                entrada_correcta_8 = 0
                            else:
                                entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                            if llantas >= 10:
                                presion_encontrada_9 = bitacora["presion_de_entrada_9"]
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                    presion_establecida_9 = bitacora["vehiculo__presion_establecida_3"]
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                    presion_establecida_9 = bitacora["vehiculo__presion_establecida_4"]
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                    presion_establecida_9 = bitacora["vehiculo__presion_establecida_5"]
                                if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                    entrada_correcta_9 = 0
                                else:
                                    entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                                presion_encontrada_10 = bitacora["presion_de_entrada_10"]
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                    presion_establecida_10 = bitacora["vehiculo__presion_establecida_3"]
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                    presion_establecida_10 = bitacora["vehiculo__presion_establecida_4"]
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                    presion_establecida_10 = bitacora["vehiculo__presion_establecida_5"]
                                if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                    entrada_correcta_10 = 0
                                else:
                                    entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                                if llantas >= 12:
                                    presion_encontrada_11 = bitacora["presion_de_entrada_11"]
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                        presion_establecida_11 = bitacora["vehiculo__presion_establecida_3"]
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                        presion_establecida_11 = bitacora["vehiculo__presion_establecida_4"]
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                        presion_establecida_11 = bitacora["vehiculo__presion_establecida_5"]
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                        presion_establecida_11 = bitacora["vehiculo__presion_establecida_6"]
                                    if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                        entrada_correcta_11 = 0
                                    else:
                                        entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                    presion_encontrada_12 = bitacora["presion_de_entrada_12"]
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                        presion_establecida_12 = bitacora["vehiculo__presion_establecida_3"]
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                        presion_establecida_12 = bitacora["vehiculo__presion_establecida_4"]
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                        presion_establecida_12 = bitacora["vehiculo__presion_establecida_5"]
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                        presion_establecida_12 = bitacora["vehiculo__presion_establecida_6"]
                                    if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                        entrada_correcta_12 = 0
                                    else:
                                        entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
        if llantas >= 12:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9 and entrada_correcta_11 >= 0.9 and entrada_correcta_12 >= 0.9:
                loop_entradas = 0
                entradas[bitacora["id"]] = True
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora["id"]] = "Doble"            
                else:
                    entradas[bitacora["id"]] = False
        elif llantas >= 10:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9:
                loop_entradas = 0
                entradas[bitacora["id"]] = True
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora["id"]] = "Doble"            
                else:
                    entradas[bitacora["id"]] = False
        elif llantas >= 8:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9:
                loop_entradas = 0
                entradas[bitacora["id"]] = True
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora["id"]] = "Doble"            
                else:
                    entradas[bitacora["id"]] = False
        elif llantas >= 6:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9:
                loop_entradas = 0
                entradas[bitacora["id"]] = True
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora["id"]] = "Doble"            
                else:
                    entradas[bitacora["id"]] = False
        elif llantas >= 4:
            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9:
                loop_entradas = 0
                entradas[bitacora["id"]] = True
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora["id"]] = "Doble"            
                else:
                    entradas[bitacora["id"]] = False
        elif llantas >= 2:
            if presion_encontrada_2 == None:
                if entrada_correcta_1 >= 0.9:
                    loop_entradas = 0
                    entradas[bitacora["id"]] = True
                else:
                    loop_entradas += 1
                    if loop_entradas >= 2:
                        entradas[bitacora["id"]] = "Doble"            
                    else:
                        entradas[bitacora["id"]] = False
            else:
                if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9:
                    loop_entradas = 0
                    entradas[bitacora["id"]] = True
                else:
                    loop_entradas += 1
                    if loop_entradas >= 2:
                        entradas[bitacora["id"]] = "Doble"            
                    else:
                        entradas[bitacora["id"]] = False
    return entradas

def entrada_correcta_api(vehiculos, vehiculos2):
    try:
        entradas = {}
        loop_entradas = 0
        bitacoras = vehiculos.order_by("id")
        for bitacora in bitacoras:
            presion_de_entrada = bitacora.presion_de_entrada
            presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
            presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
            presion_establecida_3 = bitacora.vehiculo.presion_establecida_3
            presion_establecida_4 = bitacora.vehiculo.presion_establecida_4
            presion_establecida_5 = bitacora.vehiculo.presion_establecida_5
            presion_establecida_6 = bitacora.vehiculo.presion_establecida_6
            presion_establecida_7 = bitacora.vehiculo.presion_establecida_7
            if presion_de_entrada == 0 or presion_establecida_1 == 0 or presion_establecida_2 == 0 or presion_establecida_3 == 0 or presion_establecida_4 == 0 or presion_establecida_5 == 0 or presion_establecida_6 == 0 or presion_establecida_7 == 0:
                entrada_correcta = 0
            else:
                
                try:
                    entrada_correcta_1 = presion_de_entrada/presion_establecida_1
                except:
                    entrada_correcta_1 = 1
                try:
                    entrada_correcta_2 = presion_de_entrada/presion_establecida_2
                except:
                    entrada_correcta_2 = 1
                try:
                    entrada_correcta_3 = presion_de_entrada/presion_establecida_3
                except:
                    entrada_correcta_3 = 1
                try:
                    entrada_correcta_4 = presion_de_entrada/presion_establecida_4
                except:
                    entrada_correcta_4 = 1
                try:
                    entrada_correcta_5 = presion_de_entrada/presion_establecida_5
                except:
                    entrada_correcta_5 = 1
                try:
                    entrada_correcta_6 = presion_de_entrada/presion_establecida_6
                except:
                    entrada_correcta_6 = 1
                try:
                    entrada_correcta_7 = presion_de_entrada/presion_establecida_7
                except:
                    entrada_correcta_7 = 1

            if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9:
                loop_entradas = 0
                entradas[bitacora.id] = "Buena"
            else:
                loop_entradas += 1
                if loop_entradas >= 2:
                    entradas[bitacora.id] = "Doble"
                else:
                    entradas[bitacora.id] = "Mala"

        try:
            bitacoras2 = vehiculos2.order_by("id")
            for bitacora in bitacoras2:
                configuracion = bitacora.vehiculo.configuracion
                llantas = cantidad_llantas(configuracion)
                llantas_eje = cantidad_llantas_por_eje(configuracion)
                if llantas >= 2:
                    presion_encontrada_1 = bitacora.presion_de_entrada_1
                    presion_establecida_1 = bitacora.vehiculo.presion_establecida_1
                    if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                        entrada_correcta_1 = 0
                    else:
                        entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
                    presion_encontrada_2 = bitacora.presion_de_entrada_2
                    if llantas_eje[0] >= 2:
                        presion_establecida_2 = bitacora.vehiculo.presion_establecida_1
                    elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                        presion_establecida_2 = bitacora.vehiculo.presion_establecida_2
                    if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                        entrada_correcta_2 = 0
                    else:
                        entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
                    if llantas >= 4:                    
                        presion_encontrada_3 = bitacora.presion_de_entrada_3
                        if llantas_eje[0] >= 3:
                            presion_establecida_3 = bitacora.vehiculo.presion_establecida_1
                        elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                            presion_establecida_3 = bitacora.vehiculo.presion_establecida_2
                        if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                            entrada_correcta_3 = 0
                        else:
                            entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                        presion_encontrada_4 = bitacora.presion_de_entrada_4
                        if llantas_eje[0] >= 4:
                            presion_establecida_4 = bitacora.vehiculo.presion_establecida_1
                        elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                            presion_establecida_4 = bitacora.vehiculo.presion_establecida_2
                        if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                            entrada_correcta_4 = 0
                        else:
                            entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                        if llantas >= 6:      
                            presion_encontrada_5 = bitacora.presion_de_entrada_5
                            if (llantas_eje[0] + llantas_eje[1]) >= 5:
                                presion_establecida_5 = bitacora.vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                                presion_establecida_5 = bitacora.vehiculo.presion_establecida_3
                            if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                                entrada_correcta_5 = 0
                            else:
                                entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                            presion_encontrada_6 = bitacora.presion_de_entrada_6
                            if (llantas_eje[0] + llantas_eje[1]) >= 6:
                                presion_establecida_6 = bitacora.vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                                presion_establecida_6 = bitacora.vehiculo.presion_establecida_3
                            if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                                entrada_correcta_6 = 0
                            else:
                                entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                            if llantas >= 8:
                                presion_encontrada_7 = bitacora.presion_de_entrada_7
                                if (llantas_eje[0] + llantas_eje[1]) >= 7:
                                    presion_establecida_7 = bitacora.vehiculo.presion_establecida_2
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                                    presion_establecida_7 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                                    presion_establecida_7 = bitacora.vehiculo.presion_establecida_4
                                if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                                    entrada_correcta_7 = 0
                                else:
                                    entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                                presion_encontrada_8 = bitacora.presion_de_entrada_8
                                if (llantas_eje[0] + llantas_eje[1]) >= 8:
                                    presion_establecida_8 = bitacora.vehiculo.presion_establecida_2
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                                    presion_establecida_8 = bitacora.vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                                    presion_establecida_8 = bitacora.vehiculo.presion_establecida_4
                                if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                                    entrada_correcta_8 = 0
                                else:
                                    entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                                if llantas >= 10:
                                    presion_encontrada_9 = bitacora.presion_de_entrada_9
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                        presion_establecida_9 = bitacora.vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                        presion_establecida_9 = bitacora.vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                        presion_establecida_9 = bitacora.vehiculo.presion_establecida_5
                                    if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                        entrada_correcta_9 = 0
                                    else:
                                        entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                                    presion_encontrada_10 = bitacora.presion_de_entrada_10
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                        presion_establecida_10 = bitacora.vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                        presion_establecida_10 = bitacora.vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                        presion_establecida_10 = bitacora.vehiculo.presion_establecida_5
                                    if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                        entrada_correcta_10 = 0
                                    else:
                                        entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                                    if llantas >= 12:
                                        presion_encontrada_11 = bitacora.presion_de_entrada_11
                                        if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_3
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_4
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_5
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                            presion_establecida_11 = bitacora.vehiculo.presion_establecida_6
                                        if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                            entrada_correcta_11 = 0
                                        else:
                                            entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                        presion_encontrada_12 = bitacora.presion_de_entrada_12
                                        if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_3
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_4
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_5
                                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                            presion_establecida_12 = bitacora.vehiculo.presion_establecida_6
                                        if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                            entrada_correcta_12 = 0
                                        else:
                                            entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
                if llantas >= 12:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9 and entrada_correcta_11 >= 0.9 and entrada_correcta_12 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = "Buena"
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = "Mala"
                elif llantas >= 10:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9 and entrada_correcta_9 >= 0.9 and entrada_correcta_10 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = "Buena"
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = "Mala"
                elif llantas >= 8:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9 and entrada_correcta_7 >= 0.9 and entrada_correcta_8 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = "Buena"
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = "Mala"
                elif llantas >= 6:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9 and entrada_correcta_5 >= 0.9 and entrada_correcta_6 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = "Buena"
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = "Mala"
                elif llantas >= 4:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9 and entrada_correcta_3 >= 0.9 and entrada_correcta_4 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = "Buena"
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = "Mala"
                elif llantas >= 2:
                    if entrada_correcta_1 >= 0.9 and entrada_correcta_2 >= 0.9:
                        loop_entradas = 0
                        entradas[bitacora.id] = "Buena"
                    else:
                        loop_entradas += 1
                        if loop_entradas >= 2:
                            entradas[bitacora.id] = "Doble"            
                        else:
                            entradas[bitacora.id] = "Mala"
        except:
            pass
        return entradas
    except:
        try:
            presion_encontrada = vehiculos.presion_de_entrada
            presion_establecida = vehiculos.presion_establecida
            entrada_correcta = presion_encontrada/presion_establecida

            if entrada_correcta >= 0.9:
                entradas = "good"
            else:
                entradas = "bad"
            return entradas
        except:
            return None

def entrada_correcta_actual(vehiculo):
    try:
        if vehiculo.ultima_bitacora_pro:
            fecha_1 = vehiculo.fecha_de_inflado
            fecha_2 = vehiculo.ultima_bitacora_pro.fecha_de_inflado
            if fecha_1 > fecha_2:
                presion_de_entrada = vehiculo.presion_de_entrada
                presion_de_salida = vehiculo.presion_de_salida
                entrada_correcta = presion_de_entrada/presion_de_salida
                if entrada_correcta >= 0.9:
                    entradas = "good"
                else:
                    entradas = "bad"
                return entradas
            else:
                presion_de_entrada_1 = vehiculo.ultima_bitacora_pro.presion_de_entrada_1
                presion_de_salida_1 = vehiculo.ultima_bitacora_pro.presion_de_salida_1
                entrada_correcta_1 = presion_de_entrada_1/presion_de_salida_1
                presion_de_entrada_2 = vehiculo.ultima_bitacora_pro.presion_de_entrada_2
                presion_de_salida_2 = vehiculo.ultima_bitacora_pro.presion_de_salida_2
                entrada_correcta_2 = presion_de_entrada_2/presion_de_salida_2
                presion_de_entrada_3 = vehiculo.ultima_bitacora_pro.presion_de_entrada_3
                presion_de_salida_3 = vehiculo.ultima_bitacora_pro.presion_de_salida_3
                entrada_correcta_3 = presion_de_entrada_3/presion_de_salida_3
                presion_de_entrada_4 = vehiculo.ultima_bitacora_pro.presion_de_entrada_4
                presion_de_salida_4 = vehiculo.ultima_bitacora_pro.presion_de_salida_4
                entrada_correcta_4 = presion_de_entrada_4/presion_de_salida_4
                presion_de_entrada_5 = vehiculo.ultima_bitacora_pro.presion_de_entrada_5
                presion_de_salida_5 = vehiculo.ultima_bitacora_pro.presion_de_salida_5
                entrada_correcta_5 = presion_de_entrada_5/presion_de_salida_5
                presion_de_entrada_6 = vehiculo.ultima_bitacora_pro.presion_de_entrada_6
                presion_de_salida_6 = vehiculo.ultima_bitacora_pro.presion_de_salida_6
                entrada_correcta_6 = presion_de_entrada_6/presion_de_salida_6
                presion_de_entrada_7 = vehiculo.ultima_bitacora_pro.presion_de_entrada_7
                presion_de_salida_7 = vehiculo.ultima_bitacora_pro.presion_de_salida_7
                entrada_correcta_7 = presion_de_entrada_7/presion_de_salida_7
                presion_de_entrada_8 = vehiculo.ultima_bitacora_pro.presion_de_entrada_8
                presion_de_salida_8 = vehiculo.ultima_bitacora_pro.presion_de_salida_8
                entrada_correcta_8 = presion_de_entrada_8/presion_de_salida_8
                presion_de_entrada_9 = vehiculo.ultima_bitacora_pro.presion_de_entrada_9
                presion_de_salida_9 = vehiculo.ultima_bitacora_pro.presion_de_salida_9
                entrada_correcta_9 = presion_de_entrada_9/presion_de_salida_9
                presion_de_entrada_10 = vehiculo.ultima_bitacora_pro.presion_de_entrada_10
                presion_de_salida_10 = vehiculo.ultima_bitacora_pro.presion_de_salida_10
                entrada_correcta_10 = presion_de_entrada_10/presion_de_salida_10
                presion_de_entrada_11 = vehiculo.ultima_bitacora_pro.presion_de_entrada_11
                presion_de_salida_11 = vehiculo.ultima_bitacora_pro.presion_de_salida_11
                entrada_correcta_11 = presion_de_entrada_11/presion_de_salida_11
                presion_de_entrada_12 = vehiculo.ultima_bitacora_pro.presion_de_entrada_12
                presion_de_salida_12 = vehiculo.ultima_bitacora_pro.presion_de_salida_12
                entrada_correcta_12 = presion_de_entrada_12/presion_de_salida_12
                if entrada_correcta_1 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_2 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_3 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_4 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_5 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_6 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_7 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_8 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_9 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_10 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_11 < 0.9:
                    entradas = "bad"
                elif entrada_correcta_12 < 0.9:
                    entradas = "bad"
                else:
                    entradas = "good"
                return entradas

    except:
        return None

def estatus_profundidad(llantas):
    estatus = llantas.select_related("ultima_inspeccion", "vehiculo__compania").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil"))), nombre_eje=Case(When(llanta_eje="S", then=Value("direccion")),When(llanta_eje="D", then=Value("traccion")),When(llanta_eje="T",then=Value("arrastre")),When(llanta_eje="C", then=Value("loco")),When(llanta_eje="L", then=Value("retractil")), output_field=CharField())).annotate(estatus=Case(When(ultima_inspeccion__min_profundidad__gt=F("punto_de_retiro"), then=Value("verde")),When(ultima_inspeccion__min_profundidad__gte=F("punto_de_retiro"),then=Value("amarillo")),When(ultima_inspeccion__min_profundidad__lte=F("punto_de_retiro"),then=Value("rojo")), output_field=CharField())).values("nombre_eje").annotate(num_verde=Count("estatus",filter=Q(estatus="verde")),num_amarillo=Count("estatus",filter=Q(estatus="amarillo")),num_rojo=Count("estatus",filter=Q(estatus="rojo")))
    return estatus

def exist_edicion_manual(inspeccion_vehiculo):
    inspecciones = Inspeccion.objects.filter(inspeccion_vehiculo=inspeccion_vehiculo)
    for inspeccion in inspecciones:
        if inspeccion.edicion_manual == True:
            return True
    return False

def exist_edicion_manual_one(inspeccion):
    if inspeccion.edicion_manual == True:
        return True
    return False


def exist_context(user):
    perfil = Perfil.objects.get(user = user)
    print(perfil)
    return False

def folio():
    pass

def inflado_inicio(POST):
    #? Lista de ids
    fecha = ''
    list_fechas_str = []
    if 'inflado-inicio' in POST and POST['inflado-inicio'] != '' and POST['inflado-inicio'] != None:
        fecha = POST['inflado-inicio']
    fecha = str(fecha).replace(' ', '').replace('\'', '')
    return fecha


def inflado_final(POST):
    #? Lista de ids
    fecha = ''
    if 'inflado-final' in POST and POST['inflado-final'] != '' and POST['inflado-final'] != None:
        fecha = POST['inflado-final']
    fecha = str(fecha).replace(' ', '').replace('\'', '')
    return fecha


def inspeccion_inicio(POST):
    #? Lista de ids
    fecha = ''
    if 'inspeccion-inicio' in POST and POST['inspeccion-inicio'] != '' and POST['inspeccion-inicio'] != None:
        fecha = POST['inspeccion-inicio']
    fecha = str(fecha).replace(' ', '').replace('\'', '')
    return fecha


def inspeccion_final(POST):
    #? Lista de ids
    fecha = ''
    if 'inspeccion-final' in POST and POST['inspeccion-final'] != '' and POST['inspeccion-final'] != None:
        fecha = POST['inspeccion-final']
    fecha = str(fecha).replace(' ', '').replace('\'', '')
    return fecha


def alineacion_inicio(POST):
    #? Lista de ids
    fecha = ''
    if 'alineacion-inicio' in POST and POST['alineacion-inicio'] != '' and POST['alineacion-inicio'] != None:
        fecha = POST['alineacion-inicio']
    fecha = str(fecha).replace(' ', '').replace('\'', '')
    return fecha


def alineacion_final(POST):
    #? Lista de ids
    fecha = ''
    if 'alineacion-final' in POST and POST['alineacion-final'] != '' and POST['alineacion-final'] != None:
        fecha = POST['alineacion-final']
    fecha = str(fecha).replace(' ', '').replace('\'', '')
    return fecha



def inflado_inicio_get(GET):
    return GET.get('inflado_inicio', '')

def inflado_final_get(GET):
    return GET.get('inflado_final', '')

def inspeccion_inicio_get(GET):
    return GET.get('inspeccion_inicio', '')

def inspeccion_final_get(GET):
    return GET.get('inspeccion_final', '')

def alineacion_inicio_get(GET):
    return GET.get('alineacion_inicio', '')

def alineacion_final_get(GET):
    return GET.get('alineacion_final', '')



def get_product_list(productos):
    list_temp = []
    for producto in productos:
        list_temp.append(producto['producto__producto'])
    return list_temp


def inflado_promedio(vehiculo):
    tiempo_promedio = 0
    promedio_contar = 0
    try:
        for tiempo in vehiculo:
            try:
                tiempo_promedio += tiempo.tiempo_de_inflado
                promedio_contar +=1
            except:
                pass
    except:
        try:
            tiempo_promedio += vehiculo.tiempo_de_inflado
            promedio_contar +=1
        except:
            pass
    try:
        for tiempo in vehiculo:
            tiempo_promedio += tiempo.ultima_bitacora_pro.tiempo_de_inflado
            promedio_contar +=1
    except:
        try:
            tiempo_promedio += vehiculo.ultima_bitacora_pro.tiempo_de_inflado
            promedio_contar +=1
        except:
            pass
    try:
        return round(tiempo_promedio/promedio_contar, 2)
    except:
        return None

def juntar_bitacoras(vehiculos, bitacora, bitacora_pro):
    nueva_bitacora = []
    values_bitacora = bitacora.values()
    for value in values_bitacora:
        nueva_bitacora.append(value)
    for b in nueva_bitacora:
        print(b)


    vehiculos_bitacora = bitacora.values_list("vehiculo__numero_economico", flat=True).distinct()
    vehiculos_bitacora_pro = bitacora_pro.values_list("vehiculo__numero_economico", flat=True).distinct()
    vehiculos = vehiculos.filter(numero_economico__in=vehiculos_bitacora) & vehiculos.filter(numero_economico__in=vehiculos_bitacora_pro)

    for vehiculo in vehiculos:
        print(vehiculo)
        fecha_bitacora = bitacora.filter(vehiculo=vehiculo).order_by("fecha_de_inflado").values("fecha_de_inflado")
        fecha_bitacora_pro = bitacora_pro.filter(vehiculo=vehiculo).order_by("fecha_de_inflado").values("fecha_de_inflado")

        fecha_bitacora = bitacora.filter(vehiculo=vehiculo).order_by("fecha_de_inflado")[0].fecha_de_inflado
        fecha_bitacora_pro = bitacora_pro.filter(vehiculo=vehiculo).order_by("fecha_de_inflado")[0].fecha_de_inflado
        print(fecha_bitacora)
        print(fecha_bitacora_pro)

        if fecha_bitacora > fecha_bitacora_pro:
            print(True)
        else:
            print(False)


def int_list_element(lista):
    list_temp = []
    for num in lista:
        list_temp.append(int(float(num)))
    return list_temp


def inventario_list(stock):
    inv = []
    inventarios = [
        "Nueva",
        "Antes de Renovar", 
        "Antes de Desechar", 
        "Renovada", 
        "Con renovador", 
        "Desecho final", 
        "Servicio",
        "Rodante", 
        "Archivado", 
    ]
    for inventario in inventarios:
        if inventario != stock:
            inv.append(inventario)
    return inv

def km_actual(inspecciones):
    try:
        duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=1)
        regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
        llantas = regresion.values("llanta").distinct()
        for llanta in llantas:
            llanta_completa = Llanta.objects.get(id=llanta["llanta"])
            valores_llanta = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
            min_mm = valores_llanta.last().min_profundidad
            max_mm = valores_llanta.first().min_profundidad
            min_km = valores_llanta.first().km_vehiculo
            max_km = valores_llanta.last().km_vehiculo
            if min_mm <= max_mm:
                if min_km <= max_km:
                    km_recorrido = abs(max_km - min_km)
                    mm_desgastados = abs(max_mm - min_mm)
                    if mm_desgastados == 0:
                        mm_desgastados = 1
                    km_x_mm = km_recorrido / mm_desgastados
                    profundidad_inicial = llanta_completa.producto.profundidad_inicial
                    km_teorico_actual = int((profundidad_inicial - min_mm) * km_x_mm)
                    return km_teorico_actual
                else:
                    return None
            else:
                return None
    except:
        return None

def km_proyectado(inspecciones, mediana):
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=1)
    regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = regresion.values("llanta").distinct()
    llantas_limpias = []
    kms_proyectados = []
    llanta_kms_proyectados = {}
    kms_x_mm = []
    cpks = []   
    min_profundidades = []
    for llanta in llantas:
        llanta_completa = Llanta.objects.get(id=llanta["llanta"])
        if llanta_completa.km_montado or llanta_completa.km_montado == 0:
            try:
                x = []
                y = []
                x.append(llanta_completa.km_montado)
                y.append(llanta_completa.producto.profundidad_inicial)
                km_llanta = regresion.filter(llanta=llanta["llanta"]).values("km_vehiculo")
                for r in km_llanta:
                    suma = abs(r["km_vehiculo"] - llanta_completa.km_montado)
                    y.append(suma)
                profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
                for p in profundidades:
                    x.append(p["min_profundidad"])
                
                x = np.array(x)
                y = np.array(y)

                f = np.polyfit(x, y, 2)
                p = np.poly1d(f)
                termino = []
                for numero in p:
                    numero = round(numero, 4)
                    termino.append(numero)
                km_actual = y[-1]
                km_proyectado = (termino[0]*(3**2))+(termino[1]*3)+termino[2]

                if profundidades.last()["min_profundidad"] <= 3:
                    km_proyectado = km_actual
                
                km_x_mm = km_proyectado / (llanta_completa.producto.profundidad_inicial - 3)
                precio = llanta_completa.producto.precio
                cpk = round((precio / km_proyectado), 3)

                if km_actual >= 20000:

                    print("llanta", llanta_completa)
                    print("km_x_mm", km_x_mm)
                    print("profundidad_inicial", llanta_completa.producto.profundidad_inicial)
                    print("km_actual", km_actual)
                    print("km_proyectado", km_proyectado)
                    #print("cpk", cpk)

                    llantas_limpias.append(llanta_completa)
                    kms_proyectados.append(km_proyectado)
                    llanta_kms_proyectados[llanta_completa] = km_proyectado
                    kms_x_mm.append(km_x_mm)
                    cpks.append(cpk)
                    min_profundidades.append(profundidades.last()["min_profundidad"])
            except:
                pass
        else:
            try:
                valores_llanta = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
                profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
                min_mm = valores_llanta.last().min_profundidad
                max_mm = valores_llanta.first().min_profundidad
                min_km = valores_llanta.first().km_vehiculo
                max_km = valores_llanta.last().km_vehiculo
                km_recorrido = abs(max_km - min_km)
                mm_desgastados = abs(max_mm - min_mm)
                if mm_desgastados == 0:
                    mm_desgastados = 0.01
                km_x_mm = km_recorrido / mm_desgastados
                profundidad_inicial = llanta_completa.producto.profundidad_inicial
                km_teorico_actual = int((profundidad_inicial - min_mm) * km_x_mm)
                km_teorico_proyectado = int((profundidad_inicial - 3) * km_x_mm)

                if profundidades.last()["min_profundidad"] <= 3:
                    km_teorico_proyectado = km_teorico_actual

                precio = llanta_completa.producto.precio
                try:
                    cpk = round((precio / km_teorico_proyectado), 3)
                except:
                    cpk = None

                #print("min_km", min_km)
                #print("max_km", max_km)
                #print("mm_desgastados", mm_desgastados)
                #print("km_recorrido", km_recorrido)
                #print("km_x_mm", km_x_mm)
                #print("profundidad_inicial", profundidad_inicial)
                #print("cpk", cpk)

                if km_teorico_actual >= 20000:
                    #print("llanta", llanta_completa, "vehiculo", llanta_completa.vehiculo)
                    #print("km_teorico_actual", km_teorico_actual)
                    #print("km_proyectado", km_teorico_proyectado)
                
                    llantas_limpias.append(llanta_completa)
                    kms_proyectados.append(km_teorico_proyectado)
                    llanta_kms_proyectados[llanta_completa] = km_teorico_proyectado
                    kms_x_mm.append(km_x_mm)
                    cpks.append(cpk)
                    min_profundidades.append(profundidades.last()["min_profundidad"])
            except:
                pass

    """print("km proyectados: ", kms_proyectados)
    print("cpks: ", cpks)"""
    if inspecciones:
        if mediana:
            try:
                mediana_km_proyectado = km_proyectado_mediana(llanta_kms_proyectados)
                llantas_limpias = list(mediana_km_proyectado[0].keys())
                mediana_km_proyectado = mediana_km_proyectado[1]
            except:
                try:
                    mediana_km_proyectado = int(statistics.median(kms_proyectados))
                except:
                    mediana_km_proyectado = 0            
        else:
            try:
                mediana_km_proyectado = int(statistics.median(kms_proyectados))
            except:
                mediana_km_proyectado = 0
    else:
        mediana_km_proyectado = 0

    try:
        mediana_kms_x_mm = int(statistics.median(kms_x_mm))
    except:
        mediana_kms_x_mm = 0
    try:
        mediana_cpks = round(statistics.median(cpks), 3)
    except:
        mediana_cpks = 0
    try:
        mediana_mms = round(statistics.median(min_profundidades), 3)
    except:
        mediana_mms = 0
    return mediana_km_proyectado, mediana_kms_x_mm, mediana_cpks, cpks, llantas_limpias, kms_proyectados, mediana_mms

def km_proyectado_llanta(inspecciones):
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=1)
    regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = regresion.values("llanta").distinct()
    kms_proyectados = []
    kms_x_mm = []
    cpks = []
    min_profundidades = []
    for llanta in llantas:
        llanta_completa = Llanta.objects.get(id=llanta["llanta"])
        if llanta_completa.km_montado:
            x = []
            y = []
            x.append(llanta_completa.km_montado)
            y.append(llanta_completa.producto.profundidad_inicial)
            km_llanta = regresion.filter(llanta=llanta["llanta"]).values("km_vehiculo")
            for r in km_llanta:
                suma = abs(r["km_vehiculo"] - llanta_completa.km_montado)
                y.append(suma)
            profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
            for p in profundidades:
                x.append(p["min_profundidad"])
            
            x = np.array(x)
            y = np.array(y)

            f = np.polyfit(x, y, 2)
            p = np.poly1d(f)
            termino = []
            for numero in p:
                numero = round(numero, 4)
                termino.append(numero)
            km_actual = y[-1]
            km_proyectado = (termino[0]*(3**2))+(termino[1]*3)+termino[2]

            if profundidades.last()["min_profundidad"] <= 3:
                km_proyectado = km_actual

            km_x_mm = km_proyectado / (llanta_completa.producto.profundidad_inicial - 3)
            precio = llanta_completa.producto.precio
            cpk = round((precio / km_proyectado), 3)

            """print("llanta", llanta)
            print("km_x_mm", km_x_mm)
            print("profundidad_inicial", llanta_completa.producto.profundidad_inicial)
            print("km_teorico_actual", km_actual)
            print("km_proyectado", km_proyectado)
            print("cpk", cpk)"""

            return km_proyectado, km_x_mm, cpk

        else:
            valores_llanta = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).aggregate(max_mm=Max("min_profundidad"), km_recorrido=Max("km_vehiculo")-Min("km_vehiculo"), min_mm=Min("min_profundidad"))
            profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
            mm_desgastados = valores_llanta["max_mm"] - valores_llanta["min_mm"]
            if mm_desgastados == 0:
                mm_desgastados = 1
            try:
                km_recorrido = valores_llanta["km_recorrido"]
                km_x_mm = km_recorrido / mm_desgastados
                profundidad_inicial = llanta_completa.producto.profundidad_inicial
                km_teorico_actual = int((profundidad_inicial - valores_llanta["min_mm"]) * km_x_mm)
                km_teorico_proyectado = int((profundidad_inicial - 3) * km_x_mm)
                precio = llanta_completa.producto.precio
                cpk = round((precio / km_teorico_proyectado), 3)
    
                """print("llanta", llanta)
                print("mm_desgastados", mm_desgastados)
                print("km_recorrido", km_recorrido)
                print("km_x_mm", km_x_mm)
                print("profundidad_inicial", profundidad_inicial)
                print("km_teorico_actual", km_teorico_actual)
                print("km_proyectado", km_teorico_proyectado)
                print("cpk", cpk)"""
                return km_teorico_proyectado, km_x_mm, cpk
                
            except:
                return 0, 0, 0

def km_proyectado_mediana(kms_proyectados):
    q1 =  np.quantile(list(kms_proyectados.values()), 0.25)
    primer_mediana = round(statistics.median(list(kms_proyectados.values())), 2)
    q3 =  np.quantile(list(kms_proyectados.values()), 0.75)
    sigma = round(statistics.pstdev(list(kms_proyectados.values())), 2)
    
    nuevos_kms_proyectados = {}
    for km in kms_proyectados:
        if q1 <= kms_proyectados[km] <= q3:
            nuevos_kms_proyectados[km] = kms_proyectados[km]

    segunda_mediana = round(statistics.median(list(nuevos_kms_proyectados.values())), 2)
    desvest = round(statistics.pstdev(list(nuevos_kms_proyectados.values())), 2)
    limite_inferior = round(segunda_mediana - (3 * desvest), 2)
    limite_superior = round(segunda_mediana + (3 * desvest), 2)

    kms_proyectados_final = {}
    for km in nuevos_kms_proyectados:
        if limite_inferior <= nuevos_kms_proyectados[km] <= limite_superior:
            kms_proyectados_final[km] = nuevos_kms_proyectados[km]

    mediana_final = int(statistics.median(list(kms_proyectados_final.values())))

    """print("kms_proyectados", kms_proyectados)
    print()
    print("q1", q1)
    print("primer_mediana", primer_mediana)
    print("q3", q3)
    print("sigma", sigma)
    print()
    print("nuevos_kms_proyectados", nuevos_kms_proyectados)
    print()
    print("limite_inferior", limite_inferior)
    print("segunda_mediana", segunda_mediana)
    print("limite_superior", limite_superior)
    print("desvest", desvest)
    print()
    print("kms_proyectados_final", kms_proyectados_final)
    print("mediana_final", mediana_final)"""

    return kms_proyectados_final, mediana_final


def km_max_template(inspeccion_vehiculo):
    km_max_diario = inspeccion_vehiculo.vehiculo.km_diario_maximo
    fecha = inspeccion_vehiculo.fecha.date()
    hoy = date.today()
    remaining_days = (hoy - fecha).days
    km_max_total = km_max_diario * remaining_days
    if km_max_total != 0:
        return km_max_total + inspeccion_vehiculo.km
    else:
        return inspeccion_vehiculo.km
    


def lista_problemas_taller(servicios_llanta, servicio):
    problemas = []
    if servicio.alineacion == True:
        problemas.append({'posicion':f'Vehiculo {servicio.vehiculo}', 'icono': '', 'accion': f'El vehiculo se alineo'})
    for servicio in servicios_llanta:
        if servicio.inflado == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Se inflo la llanta'})
        if servicio.balanceado == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Se balanceo la llanta'})
        if servicio.reparado == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Se reparo la llanta'})
        if servicio.valvula_reparada == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Se reparo la valvula'})
        if servicio.costado_reparado == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Se reparo el costado de la llanta'})
        if servicio.rotar == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Se roto la llanta por {servicio.llanta_cambio}-{servicio.llanta_cambio.producto}'})
        if servicio.desmontaje == True:
            problemas.append({'posicion': servicio.llanta.posicion, 'icono': '', 'accion': f'Esta llanta se desmonto por la {servicio.llanta_cambio}-{servicio.llanta_cambio.producto}'})
    return problemas

def list_vehicles_valid_filter(vehiculos, filtro, query2):
    ids_vehiculos_validos = []
    ids = list_vehicle_id(vehiculos)
    filtro_query = ({'observaciones__id__in': filtro.split(',')} if filtro != '' and  filtro != None else {})
    
    for id in ids:
        llantas = Llanta.objects.filter(vehiculo__id = id, inventario = 'Rodante')
        llantas = llantas.filter(query2, **filtro_query)
        num_llantas =  llantas.count()
        if num_llantas > 0:
            ids_vehiculos_validos.append(id)
            
    return ids_vehiculos_validos


def list_vehicle_id(vehiculos):
    """AI is creating summary for list_vehicle_id

    Args:
        vehiculos (QuerySet): Consulta a la base de datos que contiene los ids de los vehiculos
    Returns:
        vehicle (list): Lista con los ids de los vehiculos
    """
    vehicle = []
    try:
        for vehiculo in vehiculos:
            vehicle.append(vehiculo['id'])
    except:
        for vehiculo in vehiculos:
            vehicle.append(vehiculo['vehiculo__id'])
    return vehicle


def lista_de_id_observaciones_get(GET):
    return GET.get('filtro', '')

def lista_de_id_observaciones(POST):
    #? Lista de ids
    alta_presion = 5
    baja_presion = 4
    baja_profundidad = 7
    en_punto_retiro = 8
    d_alta_presion = 13
    d_costilla_interna = 12
    d_inclinado_derecha = 11
    d_inclinado_izquierda = 10
    dualizacion = 9
    list_obs = []
    if 'alta-presion' in POST:
        list_obs.append(alta_presion)
    if 'baja-presion' in POST:
        list_obs.append(baja_presion)
    if 'profundidad-baja' in POST:
        list_obs.append(baja_profundidad)
    if 'profundidad-punto-retiro' in POST:
        list_obs.append(en_punto_retiro)
    if 'profundidad-desgaste-irregular' in POST:
        list_obs.append(d_alta_presion)
        list_obs.append(d_costilla_interna)
        list_obs.append(d_inclinado_derecha)
        list_obs.append(d_inclinado_izquierda)
    if 'dualizacion' in POST:
        dua = POST['dualizacion']
        if dua == 'con-dualizacion':
            list_obs.append(dualizacion)
    list_obs.sort()
    list_obs = str(list_obs).replace('[', '').replace(']', '').replace(' ', '')
    return list_obs


def lista_de_id_observaciones_exclude_get(GET):
    return GET.get('exclude', '')

def lista_de_id_observaciones_exclude(POST):
    #? Lista de ids
    dualizacion = 9
    list_obs = []
    if 'dualizacion' in POST:
        dua = POST['dualizacion']
        if dua == 'sin-dualizacion':
            list_obs.append(dualizacion)
    list_obs = str(list_obs).replace('[', '').replace(']', '').replace(' ', '')
    return list_obs


def lista_de_ejes_get(GET):
    return GET.get('ejes', '')

       
def lista_de_ejes(POST):
    ejes = []
    
    if 'r-libre' in POST:
        ejes.append('C')
    if 'r-direccion' in POST:
        ejes.append('S')
    if 'r-traccion' in POST:
        ejes.append('D')
    if 'r-retractil' in POST:
        ejes.append('L')
    if 'r-arrastre' in POST:
        ejes.append('T')
    ejes = str(ejes).replace('[', '').replace(']', '').replace(' ', '').replace('\'', '')
    return(ejes)

def mala_entrada(vehiculos):
    entradas = {}
    for vehiculo in vehiculos:
        presion_de_entrada = vehiculo.presion_de_entrada
        presion_establecida_1 = vehiculo.presion_establecida_1
        presion_establecida_2 = vehiculo.presion_establecida_2
        presion_establecida_3 = vehiculo.presion_establecida_3
        presion_establecida_4 = vehiculo.presion_establecida_4
        presion_establecida_5 = vehiculo.presion_establecida_5
        presion_establecida_6 = vehiculo.presion_establecida_6
        presion_establecida_7 = vehiculo.presion_establecida_7
        try:
            entrada_correcta_1 = presion_de_entrada/presion_establecida_1
        except:
            entrada_correcta_1 = 1
        try:
            entrada_correcta_2 = presion_de_entrada/presion_establecida_2
        except:
            entrada_correcta_2 = 1
        try:
            entrada_correcta_3 = presion_de_entrada/presion_establecida_3
        except:
            entrada_correcta_3 = 1
        try:
            entrada_correcta_4 = presion_de_entrada/presion_establecida_4
        except:
            entrada_correcta_4 = 1
        try:
            entrada_correcta_5 = presion_de_entrada/presion_establecida_5
        except:
            entrada_correcta_5 = 1
        try:
            entrada_correcta_6 = presion_de_entrada/presion_establecida_6
        except:
            entrada_correcta_6 = 1
        try:
            entrada_correcta_7 = presion_de_entrada/presion_establecida_7
        except:
            entrada_correcta_7 = 1

        if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9:
            if vehiculo.id in entradas:
                entradas[vehiculo.id] += 1
            else:
                entradas[vehiculo.id] = 1

    vehiculos_fallidos = vehiculos.filter(id__in=entradas)
    return vehiculos_fallidos

def mala_entrada_pro(vehiculos):
    entradas = {}
    for vehiculo in vehiculos:
        if vehiculo.ultima_bitacora_pro:
            configuracion = vehiculo.configuracion
            llantas = cantidad_llantas(configuracion)
            llantas_eje = cantidad_llantas_por_eje(configuracion)
            if llantas >= 2:
                presion_encontrada_1 = vehiculo.ultima_bitacora_pro.presion_de_entrada_1
                presion_establecida_1 = vehiculo.presion_establecida_1
                if presion_encontrada_1 == 0 or presion_establecida_1 == 0:
                    entrada_correcta_1 = 0
                else:
                    entrada_correcta_1 = presion_encontrada_1/presion_establecida_1
                presion_encontrada_2 = vehiculo.ultima_bitacora_pro.presion_de_entrada_2
                if llantas_eje[0] >= 2:
                    presion_establecida_2 = vehiculo.presion_establecida_1
                elif (llantas_eje[0] + llantas_eje[1]) >= 2:
                    presion_establecida_2 = vehiculo.presion_establecida_2
                if presion_encontrada_2 == 0 or presion_establecida_2 == 0:
                    entrada_correcta_2 = 0
                else:
                    entrada_correcta_2 = presion_encontrada_2/presion_establecida_2
                if llantas >= 4:                    
                    presion_encontrada_3 = vehiculo.ultima_bitacora_pro.presion_de_entrada_3
                    if llantas_eje[0] >= 3:
                        presion_establecida_3 = vehiculo.presion_establecida_1
                    elif (llantas_eje[0] + llantas_eje[1]) >= 3:
                        presion_establecida_3 = vehiculo.presion_establecida_2
                    if presion_encontrada_3 == 0 or presion_establecida_3 == 0:
                        entrada_correcta_3 = 0
                    else:
                        entrada_correcta_3 = presion_encontrada_3/presion_establecida_3
                    presion_encontrada_4 = vehiculo.ultima_bitacora_pro.presion_de_entrada_4
                    if llantas_eje[0] >= 4:
                        presion_establecida_4 = vehiculo.presion_establecida_1
                    elif (llantas_eje[0] + llantas_eje[1]) >= 4:
                        presion_establecida_4 = vehiculo.presion_establecida_2
                    if presion_encontrada_4 == 0 or presion_establecida_4 == 0:
                        entrada_correcta_4 = 0
                    else:
                        entrada_correcta_4 = presion_encontrada_4/presion_establecida_4
                    if llantas >= 6:      
                        presion_encontrada_5 = vehiculo.ultima_bitacora_pro.presion_de_entrada_5
                        if (llantas_eje[0] + llantas_eje[1]) >= 5:
                            presion_establecida_5 = vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 5:
                            presion_establecida_5 = vehiculo.presion_establecida_3
                        if presion_encontrada_5 == 0 or presion_establecida_5 == 0:
                            entrada_correcta_5 = 0
                        else:
                            entrada_correcta_5 = presion_encontrada_5/presion_establecida_5
                        presion_encontrada_6 = vehiculo.ultima_bitacora_pro.presion_de_entrada_6
                        if (llantas_eje[0] + llantas_eje[1]) >= 6:
                            presion_establecida_6 = vehiculo.presion_establecida_2
                        elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 6:
                            presion_establecida_6 = vehiculo.presion_establecida_3
                        if presion_encontrada_6 == 0 or presion_establecida_6 == 0:
                            entrada_correcta_6 = 0
                        else:
                            entrada_correcta_6 = presion_encontrada_6/presion_establecida_6
                        if llantas >= 8:
                            presion_encontrada_7 = vehiculo.ultima_bitacora_pro.presion_de_entrada_7
                            if (llantas_eje[0] + llantas_eje[1]) >= 7:
                                presion_establecida_7 = vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 7:
                                presion_establecida_7 = vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 7:
                                presion_establecida_7 = vehiculo.presion_establecida_4
                            if presion_encontrada_7 == 0 or presion_establecida_7 == 0:
                                entrada_correcta_7 = 0
                            else:
                                entrada_correcta_7 = presion_encontrada_7/presion_establecida_7
                            presion_encontrada_8 = vehiculo.ultima_bitacora_pro.presion_de_entrada_8
                            if (llantas_eje[0] + llantas_eje[1]) >= 8:
                                presion_establecida_8 = vehiculo.presion_establecida_2
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 8:
                                presion_establecida_8 = vehiculo.presion_establecida_3
                            elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 8:
                                presion_establecida_8 = vehiculo.presion_establecida_4
                            if presion_encontrada_8 == 0 or presion_establecida_8 == 0:
                                entrada_correcta_8 = 0
                            else:
                                entrada_correcta_8 = presion_encontrada_8/presion_establecida_8
                            if llantas >= 10:
                                presion_encontrada_9 = vehiculo.ultima_bitacora_pro.presion_de_entrada_9
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 9:
                                    presion_establecida_9 = vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 9:
                                    presion_establecida_9 = vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 9:
                                    presion_establecida_9 = vehiculo.presion_establecida_5
                                if presion_encontrada_9 == 0 or presion_establecida_9 == 0:
                                    entrada_correcta_9 = 0
                                else:
                                    entrada_correcta_9 = presion_encontrada_9/presion_establecida_9
                                presion_encontrada_10 = vehiculo.ultima_bitacora_pro.presion_de_entrada_10
                                if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 10:
                                    presion_establecida_10 = vehiculo.presion_establecida_3
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 10:
                                    presion_establecida_10 = vehiculo.presion_establecida_4
                                elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 10:
                                    presion_establecida_10 = vehiculo.presion_establecida_5
                                if presion_encontrada_10 == 0 or presion_establecida_10 == 0:
                                    entrada_correcta_10 = 0
                                else:
                                    entrada_correcta_10 = presion_encontrada_10/presion_establecida_10
                                if llantas >= 12:
                                    presion_encontrada_11 = vehiculo.ultima_bitacora_pro.presion_de_entrada_11
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 11:
                                        presion_establecida_11 = vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 11:
                                        presion_establecida_11 = vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 11:
                                        presion_establecida_11 = vehiculo.presion_establecida_5
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 11:
                                        presion_establecida_11 = vehiculo.presion_establecida_6
                                    if presion_encontrada_11 == 0 or presion_establecida_11 == 0:
                                        entrada_correcta_11 = 0
                                    else:
                                        entrada_correcta_11 = presion_encontrada_11/presion_establecida_11
                                    presion_encontrada_12 = vehiculo.ultima_bitacora_pro.presion_de_entrada_12
                                    if (llantas_eje[0] + llantas_eje[1] + llantas_eje[2]) >= 12:
                                        presion_establecida_12 = vehiculo.presion_establecida_3
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3]) >= 12:
                                        presion_establecida_12 = vehiculo.presion_establecida_4
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4]) >= 12:
                                        presion_establecida_12 = vehiculo.presion_establecida_5
                                    elif (llantas_eje[0] + llantas_eje[1] + llantas_eje[2] + llantas_eje[3] + llantas_eje[4] + llantas_eje[5]) >= 12:
                                        presion_establecida_12 = vehiculo.presion_establecida_6
                                    if presion_encontrada_12 == 0 or presion_establecida_12 == 0:
                                        entrada_correcta_12 = 0
                                    else:
                                        entrada_correcta_12 = presion_encontrada_12/presion_establecida_12
            if llantas >= 12:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9 or entrada_correcta_11 < 0.9 or entrada_correcta_12 < 0.9:
                    if vehiculo.id in entradas:
                        entradas[vehiculo.id] += 1
                    else:
                        entradas[vehiculo.id] = 1
            elif llantas >= 10:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9 or entrada_correcta_9 < 0.9 or entrada_correcta_10 < 0.9:
                    if vehiculo.id in entradas:
                        entradas[vehiculo.id] += 1
                    else:
                        entradas[vehiculo.id] = 1
            elif llantas >= 8:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9 or entrada_correcta_7 < 0.9 or entrada_correcta_8 < 0.9:
                    if vehiculo.id in entradas:
                        entradas[vehiculo.id] += 1
                    else:
                        entradas[vehiculo.id] = 1
            elif llantas >= 6:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9 or entrada_correcta_5 < 0.9 or entrada_correcta_6 < 0.9:
                    if vehiculo.id in entradas:
                        entradas[vehiculo.id] += 1
                    else:
                        entradas[vehiculo.id] = 1
            elif llantas >= 4:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9 or entrada_correcta_3 < 0.9 or entrada_correcta_4 < 0.9:
                    if vehiculo.id in entradas:
                        entradas[vehiculo.id] += 1
                    else:
                        entradas[vehiculo.id] = 1
            elif llantas >= 2:
                if entrada_correcta_1 < 0.9 or entrada_correcta_2 < 0.9:
                    if vehiculo.id in entradas:
                        entradas[vehiculo.id] += 1
                    else:
                        entradas[vehiculo.id] = 1
            else:
                entradas[vehiculo.id] = 0

    vehiculos_fallidos = vehiculos.filter(id__in=entradas)
    return vehiculos_fallidos

def mala_entrada_ejes(llantas, periodo):
    if periodo:
        llantas_malas = llantas.annotate(entrada=Cast(F("presion_de_entrada"),FloatField())/Cast(F("presion_de_salida"),FloatField())).filter(entrada__lt=0.9)
    llantas_malas_ejes = llantas_malas.aggregate(direccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Dirección")), traccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Tracción")), arrastre=Count("nombre_de_eje",filter=Q(nombre_de_eje="Arrastre")), loco=Count("nombre_de_eje",filter=Q(nombre_de_eje="Loco")), retractil=Count("nombre_de_eje",filter=Q(nombre_de_eje="Retractil")))
    print(llantas_malas_ejes)
    mala_entrada_ejes = {k: v for k, v in llantas_malas_ejes.items() if v != 0}
    print(mala_entrada_ejes)
    return mala_entrada_ejes

def max_profundidad(llanta):
    profundidad_derecha = llanta.profundidad_derecha
    profundidad_central = llanta.profundidad_central
    profundidad_izquierda = llanta.profundidad_izquierda
    profundidades = []
    
    if profundidad_izquierda != None:
        profundidades.append(profundidad_izquierda)
        
    if profundidad_central != None:
        profundidades.append(profundidad_central)
    if profundidad_derecha != None:
        
        profundidades.append(profundidad_derecha)
    
    if len(profundidades) >= 1:
        return(max(profundidades))
    else:
        return 0

def mes_anterior(fecha):
    primer_dia = fecha.replace(day=1)
    return primer_dia - timedelta(days=1)

def min_presion(llanta):
    presion_establecida_act = presion_establecida(llanta)
    objetivo = llanta.vehiculo.compania.objetivo / 100
    presion_minima = presion_establecida_act - (presion_establecida_act * objetivo)
    return presion_minima

def max_presion(llanta):
    presion_establecida_act = presion_establecida(llanta)
    objetivo = llanta.vehiculo.compania.objetivo / 100
    presion_maxima = presion_establecida_act + (presion_establecida_act * objetivo)
    return presion_maxima


def min_profundidad(llanta):
    profundidad_derecha = llanta.profundidad_derecha
    profundidad_central = llanta.profundidad_central
    profundidad_izquierda = llanta.profundidad_izquierda
    profundidades = []
    
    if profundidad_izquierda != None:
        profundidades.append(float(profundidad_izquierda))
        
    if profundidad_central != None:
        profundidades.append(float(profundidad_central))
        
    if profundidad_derecha != None:
        profundidades.append(float(profundidad_derecha))
    
    if len(profundidades) >= 1:
        return(float(min(profundidades)))
    else:
        return None

def min_profundidad_template(llanta):
    if llanta.profundidad_izquierda != None:
        min_izquierda = llanta.profundidad_izquierda
    else:
        min_izquierda = min_profundidad(llanta)
        
    if llanta.profundidad_central != None:
        min_central = llanta.profundidad_central
    else:
        min_central = min_profundidad(llanta)
        
    if llanta.profundidad_derecha != None:
        min_derecha = llanta.profundidad_derecha
    else:
        min_derecha = min_profundidad(llanta)
    return {
        'min_izquierda': min_izquierda,
        'min_central': min_central,
        'min_derecha': min_derecha
    }


def nunca_vistos(vehiculos):
    nunca_visto = vehiculos.filter(ultima_inspeccion__fecha_hora__isnull=True).count()
    return nunca_visto

def observaciones_vehiculo(vehiculo):
    vehiculo.observaciones_llanta.clear()
    llantas = Llanta.objects.filter(vehiculo__id = vehiculo.id)
    for llanta in llantas:
        for obs in llanta.observaciones.all():
            vehiculo.observaciones_llanta.add(obs)

def origen_option(origen):
    if origen == 'antesDeRenovar':
        return 'Antes de Renovar'
    else:
        return ''


def opciones_redireccion(inventario:str):
    if inventario == 'Nueva':
        return[
            'Taller Destino'
        ]
        
    elif inventario == 'Antes de Renovar':
        return[
            'Enviar con renovador',
            'Taller Destino',
            'Stock Destino',
        ]
        
    elif inventario == 'Con renovador':
        return[
            'Panel de Renovado'
        ]
        
    elif inventario == 'Antes de Desechar':
        return[
            'Panel de Desecho',
            'Taller Destino',
            'Stock Destino'
        ]

def ordenar_por_status(vehiculos):
    bitacora = Bitacora.objects.filter(vehiculo__in=vehiculos)
    bitacora_pro = Bitacora_Pro.objects.filter(vehiculo__in=vehiculos)
    llantas = Llanta.objects.filter(vehiculo__in=vehiculos, tirecheck=False)
    inspecciones = Inspeccion.objects.filter(llanta__in=llantas , llanta__tirecheck=False)

    filtro_sospechoso = vehiculo_sospechoso(inspecciones)
    vehiculos_sospechosos = vehiculos.filter(id__in=filtro_sospechoso)
    vehiculos_sospechosos_list = list(vehiculos_sospechosos.values_list("id", flat=True))

    doble_entrada = doble_mala_entrada(bitacora, vehiculos)
    #filtro_rojo = vehiculo_rojo(llantas, doble_entrada, vehiculos)
    doble_entrada_pro = doble_mala_entrada_pro(bitacora_pro, vehiculos)
    filtro_rojo = vehiculo_rojo_ordenamiento(llantas, vehiculos, doble_entrada, doble_entrada_pro)
    try:
        vehiculos_rojos = filtro_rojo.exclude(id__in=vehiculos_sospechosos)
        vehiculos_rojos_list = list(vehiculos_rojos.values_list("id", flat=True))
    except:
        vehiculos_rojos_list = []

    filtro_amarillo = vehiculo_amarillo_ordenamiento(llantas, vehiculos)
    try:
        vehiculos_amarillos = filtro_amarillo.exclude(id__in=vehiculos_rojos).exclude(id__in=vehiculos_sospechosos)
        vehiculos_amarillos_list = list(vehiculos_amarillos.values_list("id", flat=True))
    except:
        vehiculos_amarillos_list = []

    vehiculos_verdes = vehiculos.exclude(id__in=vehiculos_rojos).exclude(id__in=vehiculos_sospechosos).exclude(id__in=vehiculos_amarillos)
    vehiculos_verdes_list = list(vehiculos_verdes.values_list("id", flat=True))

    vehiculos_list = []
    vehiculos_list.extend(vehiculos_sospechosos_list)
    vehiculos_list.extend(vehiculos_rojos_list)
    vehiculos_list.extend(vehiculos_amarillos_list)
    vehiculos_list.extend(vehiculos_verdes_list)

    q_list = ordenar_queryset(vehiculos_list)
    vehiculos = vehiculos.filter(id__in=vehiculos_list).order_by(q_list)
    return vehiculos
   
def ordenar_queryset(queryset_list):
    q_list = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(queryset_list)])
    return q_list

def pagination(page, pages):
    pagination = {}
        
    if (page - 1) >= 1:
        pagination['prev'] = f'/api/historicodeorden?page={page - 1}'
    else:
        pagination['prev'] = None
    if (page + 1) <= pages:
        pagination['next'] = f'/api/historicodeorden?page={page + 1}'
    else:
        pagination['next'] = None 
        
    return pagination

def pagination_url(filtro, 
                    exclude, 
                    ejes, 
                    search, 
                    inflado_inicio,
                    inflado_final,
                    inspeccion_inicio,
                    inspeccion_final,
                    alineacion_inicio,
                    alineacion_final):
    """Funcion que recibe los parametros de los filtros u devuelve una cadena para poder respetarlos

    Args:
        filtro (str): Filtros utilizados
        exclude (str): Excluciones en la consulta
        ejes (str): Tipos de eje
        search (str): Filtro de busqueda

    Returns:
        str: Cadena concatenada de los diferentes filtros
    """
    if (
        filtro == None 
        and exclude == None 
        and ejes == None 
        and search == None 
        and inflado_inicio == None 
        and inflado_final == None 
        and inspeccion_inicio == None 
        and inspeccion_final == None 
        and alineacion_inicio == None 
        and alineacion_final == None
        ) or (
        filtro == '' 
        and exclude == '' 
        and ejes == '' 
        and search == ''
        and inflado_inicio == '' 
        and inflado_final == '' 
        and inspeccion_inicio == '' 
        and inspeccion_final == '' 
        and alineacion_inicio == '' 
        and alineacion_final == ''):
        return ''
    if search == None:
        search=''
    return f'&filtro={filtro}&exclude={exclude}&ejes={ejes}&search={search}&inflado_inicio={inflado_inicio}&inflado_final={inflado_final}&inspeccion_inicio={inspeccion_inicio}&inspeccion_final={inspeccion_final}&alineacion_inicio={alineacion_inicio}&alineacion_final={alineacion_final}'

def pagination_prev(page, pages, url_complemento):
    if (page - 1) >= 1:
        prev = f'{page - 1}{url_complemento}'
    else:
        prev = None
    return prev
def pagination_next(page, pages, url_complemento):
    if (page + 1) <= pages:
        next = f'{page + 1}{url_complemento}'
    else:
        next = None
    return next

def porcentaje(divisor, dividendo):
    try:
        return int((divisor/dividendo)*100)
    except:
        return "Nada"

def presion_establecida(llanta):
    vehiculo = llanta.vehiculo
    presiones_establecidas = [
        vehiculo.presion_establecida_1,
        vehiculo.presion_establecida_2,
        vehiculo.presion_establecida_3,
        vehiculo.presion_establecida_4,
        vehiculo.presion_establecida_5,
        vehiculo.presion_establecida_6,
        vehiculo.presion_establecida_7,
    ]
    eje = (llanta.eje - 1)
    return presiones_establecidas[eje]

def presion_llantas(llantas, periodo):
    if periodo:
        llantas_presion_actual = llantas.select_related("vehiculo__compania").filter(vehiculo__compania__objetivo__lt=F("presion_de_salida") - F("presion_de_entrada")).annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(nombre_eje=Case(When(llanta_eje="S", then=Value("direccion")),When(llanta_eje="D", then=Value("traccion")),When(llanta_eje="T", then=Value("arrastre")),When(llanta_eje="C", then=Value("loco")),When(llanta_eje="L", then=Value("retractil")),output_field=CharField())).values("nombre_eje").annotate(total=Count("nombre_eje")).values("nombre_eje", "total")
        return llantas_presion_actual
    else:
        llantas_presion_encontrada = llantas.select_related("vehiculo__compania").filter(vehiculo__compania__objetivo__lt=F("presion_de_salida") - F("presion_de_entrada")).annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(nombre_eje=Case(When(llanta_eje="S", then=Value("direccion")),When(llanta_eje="D", then=Value("traccion")),When(llanta_eje="T", then=Value("arrastre")),When(llanta_eje="C", then=Value("loco")),When(llanta_eje="L", then=Value("retractil")),output_field=CharField())).values("nombre_eje").annotate(total=Count("nombre_eje")).values("nombre_eje", "total")
        return llantas_presion_encontrada

def presupuesto(vidas, ubicacion):
    try:
        presupuesto_r1 = 0
        presupuesto_r2 = 0
        presupuesto_r3 = 0
        presupuesto_r4 = 0
        presupuesto_r5 = 0
        presupuesto_nuevo = 0
        if "renovado1" in vidas:
            presupuesto_r1 = vidas["renovado1"]*ubicacion.precio_renovada
        if "renovado2" in vidas:
            presupuesto_r2 = vidas["renovado2"]*ubicacion.precio_renovada
        if "renovado3" in vidas:
            presupuesto_r3 = vidas["renovado3"]*ubicacion.precio_renovada
        if "renovado4" in vidas:
            presupuesto_r4 = vidas["renovado4"]*ubicacion.precio_renovada
        if "renovado5" in vidas:
            presupuesto_r5 = vidas["renovado5"]*ubicacion.precio_renovada
        if "renovadonuevo" in vidas:
            presupuesto_nuevo = vidas["renovadonuevo"]*ubicacion.precio_nueva
        presupuesto_total = presupuesto_r1 + presupuesto_r2 + presupuesto_r3 + presupuesto_r4 + presupuesto_r5 + presupuesto_nuevo
        return presupuesto_total
    except:
        return 0

def pronostico_de_consumo(embudo):
    try:
        ejes = embudo.aggregate(direccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Dirección")), traccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Tracción")), arrastre=Count("nombre_de_eje",filter=Q(nombre_de_eje="Arrastre")), loco=Count("nombre_de_eje",filter=Q(nombre_de_eje="Loco")), retractil=Count("nombre_de_eje",filter=Q(nombre_de_eje="Retractil")))
        return ejes
    except:
        return {'direccion': 0, 'traccion': 0, 'arrastre': 0, 'loco': 0, 'retractil': 0}

def punto_de_retiro(llanta_actual):
    compania = llanta_actual.vehiculo.compania
    if "S" in llanta_actual.tipo_de_eje:
        punto_retiro = compania.punto_retiro_eje_direccion
    elif "D" in llanta_actual.tipo_de_eje:
        punto_retiro = compania.punto_retiro_eje_traccion
    elif "T" in llanta_actual.tipo_de_eje:
        punto_retiro = compania.punto_retiro_eje_arrastre
    elif "C" in llanta_actual.tipo_de_eje:
        punto_retiro = compania.punto_retiro_eje_loco
    elif "L" in llanta_actual.tipo_de_eje:
        punto_retiro = compania.punto_retiro_eje_retractil
    return(punto_retiro)



def quitar_desgaste(llanta, llanta_rotar):
    d_alta_presion = Observacion.objects.get(observacion = 'Desgaste alta presión') #?Amarillo
    d_costilla_interna = Observacion.objects.get(observacion = 'Desgaste  costilla interna') #?Amarillo
    d_inclinado_derecha = Observacion.objects.get(observacion = 'Desgaste inclinado a la derecha') #?Amarillo
    d_inclinado_izquierda = Observacion.objects.get(observacion = 'Desgaste inclinado a la izquierda') #?Amarillo

    
    #? Llanta
    llanta.observaciones.remove(d_alta_presion)
    llanta.observaciones.remove(d_costilla_interna)
    llanta.observaciones.remove(d_inclinado_derecha)
    llanta.observaciones.remove(d_inclinado_izquierda)
    
    #? Llanta rotada
    llanta_rotar.observaciones.remove(d_alta_presion)
    llanta_rotar.observaciones.remove(d_costilla_interna)
    llanta_rotar.observaciones.remove(d_inclinado_derecha)
    llanta_rotar.observaciones.remove(d_inclinado_izquierda)


def radar_min(vehiculo_fecha, compania):
    try:
        clases = clases_mas_frecuentes(vehiculo_fecha, compania)
        clases_min = min(clases.keys(), key=lambda k: clases[k])
        return clases[clases_min]
    except:
        return None

def radar_max(vehiculo_fecha, compania):
    try:
        clases = clases_mas_frecuentes(vehiculo_fecha, compania)
        clases_max = max(clases.keys(), key=lambda k: clases[k])
        return clases[clases_max]
    except:
        return None

def radar_min_resta(min, max):
    try:
        resta = max - min
        resta = resta / 2.3
        if resta == 0:
            resta = 1
        return min - resta
    except:
        return None

def reduce(func, items):
    result = items.pop()
    for item in items:
        result = func(result, item)

    return result

def reemplazo_actual(llantas):
    reemplazo_actual_llantas = llantas.annotate(punto_de_retiro=Case(When(nombre_de_eje="Dirección", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(nombre_de_eje="Tracción", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(nombre_de_eje="Arrastre", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(nombre_de_eje="Loco", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(nombre_de_eje="Retractil", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro"))
    reemplazo_actual_ejes = reemplazo_actual_llantas.aggregate(direccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Dirección")),traccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Tracción")),arrastre=Count("nombre_de_eje",filter=Q(nombre_de_eje="Arrastre")),loco=Count("nombre_de_eje",filter=Q(nombre_de_eje="Loco")),retractil=Count("nombre_de_eje",filter=Q(nombre_de_eje="Retractil")),total=Count("nombre_de_eje"))
    return reemplazo_actual_llantas, reemplazo_actual_ejes

def reemplazo_actual2(llantas):
    reemplazo_actual_llantas = llantas.annotate(punto_de_retiro=Case(When(nombre_de_eje="Dirección", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(nombre_de_eje="Tracción", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(nombre_de_eje="Arrastre", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(nombre_de_eje="Loco", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(nombre_de_eje="Retractil", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro"))
    reemplazo_actual_ejes = reemplazo_actual_llantas.aggregate(direccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Dirección")),traccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Tracción")),arrastre=Count("nombre_de_eje",filter=Q(nombre_de_eje="Arrastre")),loco=Count("nombre_de_eje",filter=Q(nombre_de_eje="Loco")),retractil=Count("nombre_de_eje",filter=Q(nombre_de_eje="Retractil")))
    return reemplazo_actual_ejes


def reemplazo_dual(llantas, reemplazo_actual):
    try:
        llantas = Llanta.objects.filter(id__in=llantas)
        llantas_duales = duales(llantas)
        reemplazo_dual_1 = llantas_duales[0].filter(id__in=reemplazo_actual)
        reemplazo_dual_2 = llantas_duales[1].filter(id__in=reemplazo_actual)
        dual_dictionary = llantas_duales[2]
        reemplazo_dual_1_list = reemplazo_dual_1.values_list("numero_economico", flat=True)
        reemplazo_dual_2_list = reemplazo_dual_2.values_list("numero_economico", flat=True)
        array_of_qs = []
        for k, v in dual_dictionary.items():
            array_of_qs.append(reemplazo_dual_1.filter(numero_economico=k).annotate(pareja=ExpressionWrapper(Value(v),output_field=CharField())).exclude(pareja__in=reemplazo_dual_2_list).values("id"))
        for k, v in dual_dictionary.items():
            array_of_qs.append(reemplazo_dual_2.filter(numero_economico=v).annotate(pareja=ExpressionWrapper(Value(k),output_field=CharField())).exclude(pareja__in=reemplazo_dual_1_list).values("id"))
        reemplazo_dual = array_of_qs[0].union(*array_of_qs[1:])
        reemplazo_dual_llantas = llantas.filter(id__in=reemplazo_dual)
        reemplazo_dual_ejes = reemplazo_dual_llantas.aggregate(direccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Dirección")),traccion=Count("nombre_de_eje",filter=Q(nombre_de_eje="Tracción")),arrastre=Count("nombre_de_eje",filter=Q(nombre_de_eje="Arrastre")),loco=Count("nombre_de_eje",filter=Q(nombre_de_eje="Loco")),retractil=Count("nombre_de_eje",filter=Q(nombre_de_eje="Retractil")),total=Count("nombre_de_eje"))
        reemplazo_dual_ejes = {k: v for k, v in reemplazo_dual_ejes.items() if v != 0}
        return reemplazo_dual_ejes
    except:
        return {}


def reemplazo_total(reemplazo_actual, reemplazo_dual):
    cantidad_total = {}
    try:
        for reemplazo in reemplazo_actual:
            r = reemplazo_actual[reemplazo]
            cantidad_total[reemplazo] = r
        for reemplazo in reemplazo_dual:
            if not(reemplazo in cantidad_total):
                cantidad_total[reemplazo] = reemplazo_dual[reemplazo]
            else:
                cantidad_total[reemplazo] += reemplazo_dual[reemplazo]
        
        return cantidad_total
    except:
        return None

def renovables(llantas, vehiculos_amarillos):
    cantidad_renovables = llantas.select_related("vehiculo").filter(vehiculo__in=vehiculos_amarillos).count()
    return cantidad_renovables

def sacar_eje(posicion, vehiculo):
    configuracion = vehiculo.configuracion
    ejes = configuracion.split(".")
    eje = ejes[posicion - 1]
    return eje

def salida_correcta(vehiculos):
    try:
        presion_de_salida = vehiculos.presion_de_salida
        presion_establecida = vehiculos.numero_economico.presion_establecida_1
        entrada_correcta = presion_de_salida/presion_establecida

        if entrada_correcta >= 0.9:
            entradas = "good"
        else:
            entradas = "bad"
        return entradas
    except:
        return None

def send_mail(bitacora, tipo):
    thread = threading.Thread(target=mail, args=(bitacora, tipo))
    print('Crear hilo')
    thread.start()

def eje_a_str(vehiculo_acomodado):
    vehiculo_id = vehiculo_acomodado[0]['vehiculo'].id
    vehiculo_acomodado[0]['vehiculo'] = vehiculo_id
    for eje in vehiculo_acomodado[0]['ejes']:
        for llanta in eje:
            id_llanta = llanta['llanta'].id
            llanta['llanta'] = id_llanta
    return str(vehiculo_acomodado)


def eje_a_list(configuracion):
    #? Se obtiene la configuracion y se convierte a una lista de diccionarios
    orden_raw = configuracion
    orden_raw = orden_raw.replace("\'", "\"")
    configuracion = json.loads(orden_raw)
    #? Se obtiene el id del vehiculo y se cambia en la lista
    vehiculo_id = configuracion[0]['vehiculo']
    vehiculo = Vehiculo.objects.get(pk =vehiculo_id )
    configuracion[0]['vehiculo'] = vehiculo
    #? Se cambian las llantas
    for eje in configuracion[0]['ejes']:
        for llanta in eje:
            id_llanta = llanta['llanta']
            llanta_ = Llanta.objects.get(pk = id_llanta)
            llanta['llanta'] = llanta_
    return configuracion
    


def bitacora_servicios(pk: int, request, acciones_vehiculo: list, dataPOST: list, llantas_desmontadas: list):
    """Esta funcion junta todas las demas que tienen que ver con la bitacora de servicio

    Args:
        pk (int): Id del vehiculo
        request (_type_): Objeto request de Django
        acciones_vehiculo (list): Acciones que se realizaran a nivel vehiculo
        dataPOST (list): Datos de las  acciones a nivel llanta 
        llantas_desmontadas (list): Lista de las llantas desmontadas
    """
    servicio_de_vehiculo = servicio_vehiculo(pk, request, acciones_vehiculo)
    servicio_llanta_desmomtaje(dataPOST, servicio_de_vehiculo)
    servicio_llanta_servicio(dataPOST, llantas_desmontadas, servicio_de_vehiculo)


def fecha_str_vehiculo(vehiculo_acomodado):
    for vehiculo in vehiculo_acomodado:
        try:
            vehiculo['fecha_inflado'] = date.strftime(vehiculo['fecha_inflado'], '%Y-%m-%d')
        except:
            vehiculo['fecha_inflado'] = 'N/A'
    return vehiculo_acomodado
        
def servicio_vehiculo(pk: int, request, acciones_vehiculo: list):
    """Esta funcion realiza las funciones del guardado del servicio a nivel vehiculo

    Args:
        pk (int): Id del vehiculo 
        request (WSGIRequest): Request
        acciones_vehiculo (list): Lista de las acciones del vehiculo

    Returns:
        ServicioVehiculo: Es el servicio que se creo
    """
    vehiculo = Vehiculo.objects.get(pk=pk)
    vehiculo_acomodado = vehiculo_con_ejes_acomodados(pk)
    vehiculo_acomodado = fecha_str_vehiculo(vehiculo_acomodado)
    #? Se obtiene la fecha y la hora
    hoja = request.POST['hoja']
    hoja = json.loads(hoja)
    dateString = f"{hoja['fecha']}, {hoja['hora']}:00"
    dateFormatter = "%Y-%m-%d, %H:%M:%S"
    fecha = datetime.strptime(dateString, dateFormatter)
    
    dateStringEnd = f"{hoja['fecha_end']}, {hoja['hora_end']}:00"
    dateFormatterEnd = "%Y-%m-%d, %H:%M:%S"
    fecha_end = datetime.strptime(dateStringEnd, dateFormatterEnd)
    
    
    #? Se guardan los servicios
    servicio = ServicioVehiculo.objects.create(
        vehiculo = vehiculo,
        usuario = request.user,
        fecha_inicio = fecha.date(),
        horario_inicio = fecha.time(),
        fecha_final = fecha_end.date(),
        horario_final = fecha_end.time(),
        ubicacion = vehiculo.ubicacion,
        aplicacion = vehiculo.aplicacion,
        configuracion = eje_a_str(vehiculo_acomodado),
        estado = 'cerrado'
    )
    
    folio = f'SRP{date.today().year}{date.today().month}{date.today().day}{servicio.id}-{vehiculo.id}'
    servicio.folio = folio
    
    #? Guardado de las acciones del vehiculo  
    if 'alinearVehiculo' in acciones_vehiculo:
        servicio.alineacion = True
    servicio.save()
    calendarioTaller(servicio)
    return servicio


def servicio_vehiculo_preguardado(pk: int, request):
    """Esta funcion realiza las funciones del guardado del servicio a nivel vehiculo

    Args:
        pk (int): Id del vehiculo 
        request (WSGIRequest): Request
        acciones_vehiculo (list): Lista de las acciones del vehiculo

    Returns:
        ServicioVehiculo: Es el servicio que se creo
    """
    vehiculo = Vehiculo.objects.get(pk=pk)
    #? Se obtiene la fecha y la hora
    hoja = request.POST['hoja']
    hoja = json.loads(hoja)
    dateString = f"{hoja['fecha']}, {hoja['hora']}:00"
    dateFormatter = "%Y-%m-%d, %H:%M:%S"
    fecha = datetime.strptime(dateString, dateFormatter)
    
    dateStringEnd = f"{hoja['fecha_end']}, {hoja['hora_end']}:00"
    dateFormatterEnd = "%Y-%m-%d, %H:%M:%S"
    fecha_end = datetime.strptime(dateStringEnd, dateFormatterEnd)
    
    
    #? Se guardan los servicios
    servicio = ServicioVehiculo.objects.create(
        vehiculo = vehiculo,
        usuario = request.user,
        fecha_inicio = fecha.date(),
        horario_inicio = fecha.time(),
        fecha_final = fecha_end.date(),
        horario_final = fecha_end.time(),
        ubicacion = vehiculo.ubicacion,
        aplicacion = vehiculo.aplicacion,
        estado ='abierto'
    )
    
    folio = f'SRP{date.today().year}{date.today().month}{date.today().day}{servicio.id}-{vehiculo.id}'
    servicio.folio = folio
    return servicio

def calendarioTaller(servicio):
    titulo = f'Servicio al vehiculo {servicio.vehiculo}'
    dateFormatter = "%Y-%m-%d,%H:%M:%S"
    dateStringStart = str(servicio.fecha_inicio) + ',' + str(servicio.horario_inicio)
    start = datetime.strptime(dateStringStart, dateFormatter)
    dateStringEnd = str(servicio.fecha_final) + ',' + str(servicio.horario_final)
    end = datetime.strptime(dateStringEnd, dateFormatter)
    horario_start_str = str(servicio.fecha_inicio) + 'T' + str(servicio.horario_inicio) + '-05:00'
    horario_end_str = str(servicio.fecha_final) + 'T' + str(servicio.horario_final) + '-05:00'
    Calendario.objects.create(
        servicio = servicio,
        vehiculo = servicio.vehiculo,
        start = start,
        end = end,
        title = titulo,
        horario_start_str = horario_start_str,
        horario_end_str = horario_end_str,
        compania = servicio.vehiculo.compania
    )


def servicio_llanta_desmomtaje(dataPOST, servicio_vehiculo_id):
    for data in dataPOST:
        if data['tipoServicio'] == 'desmontaje':
            #? Se llama la llanta actual
            llanta = Llanta.objects.get(pk=data['llantaId'])
            
            #? Se llama la llanta a montar
            nuevaLlanta = data['nuevaLlanta']
            llanta_nueva = Llanta.objects.get(numero_economico = nuevaLlanta)
            
            #? Se obtienen los datos del desmontaje
            razon = data['razon']
            almacen_desmontaje = data['almacen_desmontaje']
            taller_desmontaje = Taller.objects.get(id = int(data['taller_desmontaje']))
            
           
            ServicioLlanta.objects.create(
                serviciovehiculo = servicio_vehiculo_id,
                llanta = llanta,
                desmontaje = True,
                llanta_cambio = llanta_nueva,
                inventario_de_desmontaje = almacen_desmontaje,
                taller_de_desmontaje = taller_desmontaje,
                razon_de_desmontaje = razon
            )


def servicio_llanta_servicio(dataPOST, llantas_desmontadas, servicio_vehiculo_id):
        llantas_rotadas = []
        for data in dataPOST:
            if data['tipoServicio'] == 'sr':
                #?Se llama la llanta
                llanta = Llanta.objects.get(pk=data['llantaId'])
                #? Se verifican que servicios se realizaron
                inflar = True if data['inflar'] == 'on' else False
                balancear = True if data['balancear'] == 'on' else False
                reparar = True if data['reparar'] == 'on' else False
                valvula = True if data['valvula'] == 'on' else False
                costado = True if data['costado'] == 'on' else False
                rotar = data['rotar'] if data['rotar'] != 'no' else False
                rotar_bool = True if rotar == 'mismo' or rotar == 'otro' else False
                rotar_mismo = False
                rotar_otro = False
                llanta_rotar = None
                #? Rotar en el mismo vehiculo
                if rotar == 'mismo':
                    id_llanta_rotar = int(data['origenLlanta'])
                    llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)
                    
                    if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                        llanta_rotar = None
                        continue
                    
                    rotar_mismo = True
                    
                    llantas_rotadas.append(llanta)
                    llantas_rotadas.append(llanta_rotar)
                    
                #? Rotar en diferente vehiculo
                if rotar == 'otro':
                    id_llanta_rotar = int(data['llantaOrigen'])
                    llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)
                    
                    if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                        llanta_rotar = None
                        continue
                    
                    rotar_otro = True
                    
                    llantas_rotadas.append(llanta)
                    llantas_rotadas.append(llanta_rotar)
                    
                ServicioLlanta.objects.create(
                    serviciovehiculo = servicio_vehiculo_id,
                    llanta = llanta,
                    inflado = inflar,
                    balanceado = balancear,
                    reparado = reparar,
                    valvula_reparada = valvula,
                    costado_reparado = costado,
                    rotar = rotar_bool,
                    rotar_mismo = rotar_mismo,
                    rotar_otro = rotar_otro,
                    llanta_cambio = llanta_rotar
                )


def mail(bitacora, tipo):
    vehiculo = Vehiculo.objects.get(pk = bitacora.vehiculo.id)
    llantas = Llanta.objects.filter(vehiculo = vehiculo, inventario="Rodante")
    objetivo = vehiculo.compania.objetivo
    ubicacion = vehiculo.ubicacion
    num_ejes = vehiculo.configuracion.split('.')
    ejes_no_ordenados = []
    ejes = []
    eje = 1
    if tipo == 'pulpo':
        evento = 'Pulpo'
    elif tipo == 'pulpopro':
        evento = 'Pulpo Pro'
    presiones_establecida=[
            vehiculo.presion_establecida_1,
            vehiculo.presion_establecida_2,
            vehiculo.presion_establecida_3,
            vehiculo.presion_establecida_4,
            vehiculo.presion_establecida_5,
            vehiculo.presion_establecida_6,
            vehiculo.presion_establecida_7,
        ]
    if ubicacion.email != None:
        numero = 0
        if tipo == 'pulpo':
            print(evento)
            for num in num_ejes:
                list_temp = []
                for llanta in llantas:
                    precion_establecida = presiones_establecida[numero]
                    presion_minima = precion_establecida - (precion_establecida * (objetivo/100))
                    presion_maxima = precion_establecida + (precion_establecida * (objetivo/100))
                    if float(bitacora.presion_de_entrada) >= presion_minima and float(bitacora.presion_de_entrada) <= presion_maxima:
                        signo_entrada = 'checkmark--v1.png'
                    else:
                        signo_entrada = 'delete-sign--v1.png'
                    if float(bitacora.presion_de_salida) >= presion_minima and float(bitacora.presion_de_salida) <= presion_maxima:
                        signo_salida = 'checkmark--v1.png'
                    else:
                        signo_salida = 'delete-sign--v1.png'
                    if llanta.eje == eje:
                        list_temp.append(
                            [llanta, 
                             bitacora.presion_de_entrada,
                             signo_entrada, 
                             bitacora.presion_de_salida,
                             signo_salida
                             ])
                eje += 1
                numero += 1
                ejes_no_ordenados.append(list_temp)
        elif tipo == 'pulpopro':
            for num in num_ejes:
                list_temp = []
                for llanta in llantas:
                
                    if llanta.eje == eje:
                        list_temp.append(
                            [llanta])
                eje += 1
                ejes_no_ordenados.append(list_temp)

        for eje in ejes_no_ordenados:
            if len(eje) == 2:
                lista_temp = ['', '']
                for llanta_act in eje:
                    if 'LI' in llanta_act[0].posicion:
                        #print(llanta_act)
                        lista_temp[0] = llanta_act

                    elif 'RI' in llanta_act[0].posicion:
                        lista_temp[1] = llanta_act
                ejes.append(lista_temp)
            else:
                lista_temp = ['', '', '', '']
                for llanta_act in eje:
                    if 'LO' in llanta_act[0].posicion:
                        lista_temp[0] = llanta_act
                    elif 'LI' in llanta_act[0].posicion:
                        lista_temp[1] = llanta_act
                    elif 'RI' in llanta_act[0].posicion:
                        lista_temp[2] = llanta_act
                    elif 'RO' in llanta_act[0].posicion:
                        lista_temp[3] = llanta_act
                ejes.append(lista_temp)

        if tipo == 'pulpopro':
            presiones_entrada = [
                bitacora.presion_de_entrada_1,
                bitacora.presion_de_entrada_2,
                bitacora.presion_de_entrada_3,
                bitacora.presion_de_entrada_4,
                bitacora.presion_de_entrada_5,
                bitacora.presion_de_entrada_6,
                bitacora.presion_de_entrada_7,
                bitacora.presion_de_entrada_8,
                bitacora.presion_de_entrada_9,
                bitacora.presion_de_entrada_10,
                bitacora.presion_de_entrada_11,
                bitacora.presion_de_entrada_12,
            ]
            presiones_salida = [
                bitacora.presion_de_salida_1,
                bitacora.presion_de_salida_2,
                bitacora.presion_de_salida_3,
                bitacora.presion_de_salida_4,
                bitacora.presion_de_salida_5,
                bitacora.presion_de_salida_6,
                bitacora.presion_de_salida_7,
                bitacora.presion_de_salida_8,
                bitacora.presion_de_salida_9,
                bitacora.presion_de_salida_10,
                bitacora.presion_de_salida_11,
                bitacora.presion_de_salida_12,
            ]
            eje_act = 0
            numero = 0       
            for eje in ejes:
                for ej in eje:
                    precion_establecida = presiones_establecida[eje_act]
                    presion_minima = precion_establecida - (precion_establecida * (objetivo/100))
                    presion_maxima = precion_establecida + (precion_establecida * (objetivo/100))
                    print(presion_minima)
                    print(presion_maxima)
                    if float(presiones_entrada[numero]) >= presion_minima and float(presiones_entrada[numero]) <= presion_maxima:
                        signo_entrada = 'checkmark--v1.png'
                    else:
                        signo_entrada = 'delete-sign--v1.png'
                    if float(presiones_salida[numero]) >= presion_minima and float(presiones_salida[numero]) <= presion_maxima:
                        signo_salida = 'checkmark--v1.png'
                    else:
                        signo_salida = 'delete-sign--v1.png'
                    ej.append(presiones_entrada[numero])
                    ej.append(signo_entrada)
                    ej.append(presiones_salida[numero])
                    ej.append(signo_salida)
                    numero += 1
                #print(objetivo)
                #print(precion_establecida)
                eje_act += 1
        try:
            templete = get_template('email.html')
            context = {'ejes': ejes, 'ubicacion': ubicacion, 'vehiculo': vehiculo, 'bitacora': bitacora.id, 'tipo': tipo}
            content = templete.render(context)
            email = EmailMultiAlternatives(
                    f'Un evento {evento} en el vehiculo {vehiculo} de la sucursal {vehiculo.ubicacion}',
                    'AETOWEB',
                    settings.EMAIL_HOST_USER,
                    [str(ubicacion.email)],
                )
            email.attach_alternative(content, "text/html")
            email.send()
            return print("Envio de email correcto".center(50, '-')) 
        except Exception as e:
            return print(f'No se envio email. Error tipo {e}'.center(50, '-'))
    else:
        return print('No hay email definido')
    #!Terminar funcion
    

def sin_informacion(llantas):
    llantas_sin_informacion = llantas.filter(producto__isnull=True).count()
    return llantas_sin_informacion

def signo_pulpo(bitacora, num_eje):
    vehiculo = bitacora.vehiculo
    objetivo = vehiculo.compania.objetivo
    establecidas = [
       vehiculo.presion_establecida_1, 
       vehiculo.presion_establecida_2,
       vehiculo.presion_establecida_3,
       vehiculo.presion_establecida_4,
       vehiculo.presion_establecida_5,
       vehiculo.presion_establecida_6,
       vehiculo.presion_establecida_7
    ]
    presion_establecida = establecidas[num_eje-1]
    presion_minima = presion_establecida - (presion_establecida * (objetivo / 100))
    presion_maxima = presion_establecida + (presion_establecida * (objetivo / 100))
    presion_de_entrada = bitacora.presion_de_entrada
    presion_de_salida = bitacora.presion_de_salida
    
    if (
        (presion_de_entrada >= presion_minima and presion_de_entrada <= presion_maxima)
        and
        (presion_de_salida >= presion_minima and presion_de_salida <= presion_maxima)
        ):
        return 'icon-checkmark good-text'
    else:
        return 'icon-cross bad-text'

def signo_pulpo_pro(bitacora, num_llanta, num_eje):
    vehiculo = bitacora.vehiculo
    objetivo = vehiculo.compania.objetivo
    establecidas = [
       vehiculo.presion_establecida_1, 
       vehiculo.presion_establecida_2,
       vehiculo.presion_establecida_3,
       vehiculo.presion_establecida_4,
       vehiculo.presion_establecida_5,
       vehiculo.presion_establecida_6,
       vehiculo.presion_establecida_7
    ]
    
    
    presiones_entrada =[
        bitacora.presion_de_entrada_1,
        bitacora.presion_de_entrada_2,
        bitacora.presion_de_entrada_3,
        bitacora.presion_de_entrada_4,
        bitacora.presion_de_entrada_5,
        bitacora.presion_de_entrada_6,
        bitacora.presion_de_entrada_7,
        bitacora.presion_de_entrada_8,
        bitacora.presion_de_entrada_9,
        bitacora.presion_de_entrada_10,
        bitacora.presion_de_entrada_11,
        bitacora.presion_de_entrada_12,
    ]
    
    presiones_salidas =[
        bitacora.presion_de_salida_1,
        bitacora.presion_de_salida_2,
        bitacora.presion_de_salida_3,
        bitacora.presion_de_salida_4,
        bitacora.presion_de_salida_5,
        bitacora.presion_de_salida_6,
        bitacora.presion_de_salida_7,
        bitacora.presion_de_salida_8,
        bitacora.presion_de_salida_9,
        bitacora.presion_de_salida_10,
        bitacora.presion_de_salida_11,
        bitacora.presion_de_salida_12,
    ]
    presion_establecida = establecidas[num_eje-1]
    presion_minima = presion_establecida - (presion_establecida * (objetivo / 100))
    presion_maxima = presion_establecida + (presion_establecida * (objetivo / 100))
    presion_de_entrada = presiones_entrada[num_llanta-1]
    presion_de_salida = presiones_salidas[num_llanta-1]
    
    if (
        (presion_de_salida >= presion_minima and presion_de_salida <= presion_maxima)
        and
        (presion_de_entrada >= presion_minima and presion_de_entrada <= presion_maxima)
        ):
        return 'icon-checkmark good-text'
    else:
        return 'icon-cross bad-text'


def vehiculo_con_ejes_acomodados(pk):
    """Funcion que obtiene un vehiculo y acomoda sus ejes internos

    Args:
        pk (int): Id del vehiculo

    Returns:
        list: Lista de diccionarios de los ejes
    """
    #? Se obtiene el vehiculo con un filter, por convicciones de la funcion
    vehiculo = Vehiculo.objects.filter(pk=pk)
    print(vehiculo)
    #? Se convirte el id en una lista(Por convenvion de las funciones)
    ids_vehiculo = list_vehicle_id(vehiculo.values('id'))
    #? Se obtiene las llantas 
    llantas = Llanta.objects.filter(
        vehiculo__id__in = ids_vehiculo,
        inventario = 'Rodante'
        ).annotate(
            min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")
            ) 
    #? Se acomodan las llantas
    vehiculos_llantas_acomodadas = acomodo_de_llantas_por_vehiculo(llantas, ids_vehiculo)
    acomodo_ejes_vehiculo = acomodo_ejes_vehicle(vehiculos_llantas_acomodadas)
    acomodo_posicion_ejes_vehicle = acomodo_pocisiones_vehicle(acomodo_ejes_vehiculo)
    return acomodo_posicion_ejes_vehicle


def vehiculo_amarillo(llantas):
    vehiculos_amarillos = []
    try:
        # Desgaste irregular
        llantas_desgaste = llantas.select_related("ultima_inspeccion", "vehiculo").annotate(min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")).annotate(resta=F("max_profundidad")-F("min_profundidad")).filter(resta__gt=3).values("vehiculo").distinct()

        # Arriba del punto de retiro
        llantas_retiro = llantas.select_related("ultima_inspeccion","vehiculo__compania").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro") + 1).values("vehiculo").distinct()
        vehiculos_amarillos = llantas_desgaste.union(llantas_retiro)
        
        # Desdualización
        dual = llantas.select_related("ultima_inspeccion", "vehiculo").annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("numero_economico", "vehiculo", "posicion").annotate(eje_dual=Substr(F("posicion"),1,2)).values("vehiculo", "eje_dual").order_by().annotate(Count("numero_economico"), diferencia=Max("min_profundidad") - Min("min_profundidad")).filter(numero_economico__count=2).filter(diferencia__gt=3).values("vehiculo").distinct()
        vehiculos_amarillos = vehiculos_amarillos.union(dual)
        return vehiculos_amarillos
    except:
        return []

def vehiculo_amarillo_ordenamiento(llantas, vehiculo):
    observaciones = llantas.filter(observaciones__isnull=False).filter(observaciones__color="Amarillo").values("numero_economico", "observaciones__observacion").distinct().values("vehiculo").annotate(cantidad=Count("observaciones__observacion")).order_by("-cantidad")
    q_list = ordenar_queryset(observaciones.values_list("vehiculo__id", flat=True))
    vehiculos = vehiculo.filter(id__in=observaciones.values("vehiculo__id")).order_by(q_list)
    return vehiculos

def vehiculo_amarillo_llanta(llantas):
    llantas_amarillas = []
    try:
        # Desgaste irregular
        llantas_desgaste = llantas.select_related("vehiculo").annotate(min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")).annotate(resta=F("max_profundidad")-F("min_profundidad")).filter(resta__gt=3).values("numero_economico").distinct()

        # Arriba del punto de retiro
        llantas_retiro = llantas.select_related("vehiculo__compania").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro") + 1).values("numero_economico").distinct()
        llantas_amarillas = llantas_desgaste.union(llantas_retiro)
        
        # Desdualización
        dual = llantas.select_related("vehiculo").values("numero_economico", "vehiculo", "posicion").annotate(eje_dual=Substr(F("posicion"),1,2)).values("vehiculo", "eje_dual").annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).order_by().annotate(Count("numero_economico"), diferencia=Max("ultima_inspeccion__min_profundidad") - Min("ultima_inspeccion__min_profundidad")).filter(numero_economico__count=2).filter(diferencia__gt=3).values("numero_economico").distinct()
        llantas_amarillas = llantas_amarillas.union(dual)
        return llantas_amarillas
    except:
        return []

def vehiculos_inspeccionados_por_aplicacion(vehiculos):
    porcentaje_aplicacion = vehiculos.select_related("ultima_inspeccion", "aplicacion").values("aplicacion__nombre").distinct().annotate(ins=Case(When(ultima_inspeccion__fecha_hora__gte=timezone.now()-timedelta(days=31),then=1),default=0,output_field=IntegerField())).annotate(inspeccionado=Count("ins",filter=Q(ins=1)),no_inspeccionado=Count("ins",filter=Q(ins=0))).values("aplicacion__nombre","inspeccionado").annotate(total=F("inspeccionado")+F("no_inspeccionado")).values("aplicacion__nombre","inspeccionado","total")
    return porcentaje_aplicacion

def vehiculos_inspeccionados_por_clase(vehiculos):
    porcentaje_clase = vehiculos.select_related("ultima_inspeccion").values("clase").distinct().annotate(ins=Case(When(ultima_inspeccion__fecha_hora__gte=timezone.now()-timedelta(days=31),then=1),default=0,output_field=IntegerField())).annotate(inspeccionado=Count("ins",filter=Q(ins=1)),no_inspeccionado=Count("ins",filter=Q(ins=0))).values("clase","inspeccionado").annotate(total=F("inspeccionado")+F("no_inspeccionado")).values("clase","inspeccionado","total")
    return porcentaje_clase

def vehiculos_por_aplicacion_sin_inspeccionar(vehiculos, hoy1, hoy2, hoy3):
    vehiculos_vencidos = vehiculos.filter(~Q(ultima_inspeccion__fecha_hora__month=hoy1)) | vehiculos.filter(~Q(ultima_inspeccion__fecha_hora__month=hoy2)) | vehiculos.filter(~Q(ultima_inspeccion__fecha_hora__month=hoy3)) | vehiculos.filter(ultima_inspeccion__isnull=True)
    vehiculos_aplicacion = vehiculos_vencidos.values("aplicacion__nombre").distinct().annotate(mes1=Count("numero_economico",filter=(~Q(ultima_inspeccion__fecha_hora__month=hoy1) | Q(ultima_inspeccion__isnull=True))),mes2=Count("numero_economico",filter=(~Q(ultima_inspeccion__fecha_hora__month=hoy2) | Q(ultima_inspeccion__isnull=True))),mes3=Count("numero_economico",filter=(~Q(ultima_inspeccion__fecha_hora__month=hoy3) | Q(ultima_inspeccion__isnull=True))))
    return vehiculos_aplicacion

def vehiculos_por_clase_sin_inspeccionar(vehiculos, hoy1, hoy2, hoy3):
    vehiculos_vencidos = vehiculos.filter(~Q(ultima_inspeccion__fecha_hora__month=hoy1)) | vehiculos.filter(~Q(ultima_inspeccion__fecha_hora__month=hoy2)) | vehiculos.filter(~Q(ultima_inspeccion__fecha_hora__month=hoy3)) | vehiculos.filter(ultima_inspeccion__isnull=True)
    vehiculos_clase = vehiculos_vencidos.values("clase").distinct().annotate(mes1=Count("numero_economico",filter=(~Q(ultima_inspeccion__fecha_hora__month=hoy1) | Q(ultima_inspeccion__isnull=True))),mes2=Count("numero_economico",filter=(~Q(ultima_inspeccion__fecha_hora__month=hoy2) | Q(ultima_inspeccion__isnull=True))),mes3=Count("numero_economico",filter=(~Q(ultima_inspeccion__fecha_hora__month=hoy3) | Q(ultima_inspeccion__isnull=True))))
    return vehiculos_clase

def vehiculo_rojo(llantas, doble_entrada, vehiculo):
    llantas = llantas.select_related("ultima_inspeccion","vehiculo__compania").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro") - 1).values("vehiculo").annotate(num=Count("vehiculo")).order_by("-num")
    q_list = ordenar_queryset(llantas.values_list("vehiculo__id", flat=True))
    vehiculos = vehiculo.filter(id__in=llantas.values("vehiculo__id")).order_by(q_list)
    try:
        union = vehiculos | doble_entrada
    except:
        union = vehiculos
    return union

def vehiculo_rojo_ordenamiento(llantas, vehiculo, doble_entrada, doble_entrada_pro):
    observaciones = llantas.filter(observaciones__isnull=False).filter(observaciones__color="Rojo").values("numero_economico", "observaciones__observacion").distinct().values("vehiculo").annotate(cantidad=Count("observaciones__observacion")).order_by("-cantidad")
    q_list = ordenar_queryset(observaciones.values_list("vehiculo__id", flat=True))
    vehiculos = vehiculo.filter(id__in=observaciones.values("vehiculo__id")).order_by(q_list)
    try:
        union = doble_entrada | vehiculos
        try:
            union = doble_entrada_pro | union
        except:
            pass
    except:
        try:
            union = doble_entrada_pro | vehiculos
        except:
            union = vehiculos
    return union

def vehiculo_rojo_llanta(llantas):
    llantas = llantas.select_related("vehiculo__compania").annotate(llanta_eje=Substr(F("tipo_de_eje"),1,1)).annotate(punto_de_retiro=Case(When(llanta_eje="S", then=F("vehiculo__compania__punto_retiro_eje_direccion")),When(llanta_eje="D", then=F("vehiculo__compania__punto_retiro_eje_traccion")),When(llanta_eje="T", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),When(llanta_eje="C", then=F("vehiculo__compania__punto_retiro_eje_loco")),When(llanta_eje="L", then=F("vehiculo__compania__punto_retiro_eje_retractil")))).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lte=F("punto_de_retiro") - 1).values("numero_economico").distinct()
    return llantas

def vehiculo_sospechoso(inspecciones):
    triplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=2)
    regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=triplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = regresion.values("llanta").distinct()
    vehiculos_sospechosos = []
    for llanta in llantas:
        x = []
        y = []
        primera_fecha = regresion.filter(llanta=llanta["llanta"]).aggregate(primera_fecha=Min("fecha_hora"))
        fecha_llanta = regresion.filter(llanta=llanta["llanta"]).values("fecha_hora")
        for r in fecha_llanta:
            resta = abs(r["fecha_hora"] - primera_fecha["primera_fecha"]).days
            x.append(resta)
        profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
        for p in profundidades:
            y.append(p["min_profundidad"])
        
        x = np.array(x)
        y = np.array(y)

        if len(x) > 2:
            dia = x[-1]

            try:
                f = np.polyfit(x, y, 2)
                p = np.poly1d(f)
                termino = []
                for numero in p:
                    numero = round(numero, 4)
                    termino.append(numero)
                regresion_resultado = (termino[0]*(dia**2))+(termino[1]*dia)+termino[2]
                resta = y[0]-regresion_resultado
                diario = resta/dia
                diferencia_dias = dia-x[-2]
                prediccion = diario*diferencia_dias
                desgaste_normal = prediccion*2.5
                try:
                    vehiculos_sospechosos = regresion.annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__gt=desgaste_normal).values("llanta__vehiculo").distinct()
                except:
                    pass
            except:
                pass
    # En un futuro poner el parámetro sospechoso para cuando es 1 inspección
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count=2)
    sin_regresion = inspecciones.select_related("llanta__vehiculo__compania").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = sin_regresion.values("llanta").distinct()
    vehiculos_lista = []
    if vehiculos_sospechosos:
        vehiculos_sospechosos_iteracion = True
    else:
        vehiculos_sospechosos_iteracion = False
    for llanta in llantas:
        fechas = sin_regresion.filter(llanta=llanta["llanta"]).aggregate(primera_fecha=Min("fecha_hora"),ultima_fecha=Max("fecha_hora"))
        dias = abs(fechas["ultima_fecha"] - fechas["primera_fecha"]).days
        #print("llanta: ", Llanta.objects.get(id=llanta["llanta"]))
        #print("dias: ", dias)
        primera_profundidad = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").first())
        ultima_profundidad = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").last())
        #print("primera_profundidad: ", primera_profundidad)
        #print("ultima_profundidad: ", ultima_profundidad)
        vehiculo = sin_regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lt = primera_profundidad - (F("llanta__vehiculo__compania__mm_parametro_sospechoso") * dias)).values("llanta__vehiculo").distinct()
        if vehiculo:
            if not(vehiculo[0]["llanta__vehiculo"] in vehiculos_lista):
                if vehiculos_sospechosos_iteracion:
                    vehiculos_sospechosos = vehiculos_sospechosos | vehiculo
                else:
                    vehiculos_sospechosos = vehiculo
                    vehiculos_sospechosos_iteracion = True
                vehiculos_lista.append(vehiculo[0]["llanta__vehiculo"])
    #print(vehiculos_sospechosos)
    return vehiculos_sospechosos

def vehiculo_sospechoso_llanta(inspecciones):
    triplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count__gt=2)
    regresion = inspecciones.select_related("llanta__vehiculo").annotate(poli=Case(When(llanta__in=triplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = regresion.values("llanta").distinct()
    llantas_sospechosas = []
    for llanta in llantas:
        x = []
        y = []
        primera_fecha = regresion.filter(llanta=llanta["llanta"]).aggregate(primera_fecha=Min("fecha_hora"))
        fecha_llanta = regresion.filter(llanta=llanta["llanta"]).values("fecha_hora")
        for r in fecha_llanta:
            resta = abs(r["fecha_hora"] - primera_fecha["primera_fecha"]).days
            x.append(resta)
        profundidades = regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).values("min_profundidad")
        for p in profundidades:
            y.append(p["min_profundidad"])
        
        x = np.array(x)
        y = np.array(y)

        if len(x) > 2:
            try:
                dia = x[-1]

                f = np.polyfit(x, y, 2)
                p = np.poly1d(f)
                termino = []
                for numero in p:
                    numero = round(numero, 4)
                    termino.append(numero)
                regresion_resultado = (termino[0]*(dia**2))+(termino[1]*dia)+termino[2]
                resta = y[0]-regresion_resultado
                diario = resta/dia
                diferencia_dias = dia-x[-2]
                prediccion = diario*diferencia_dias
                desgaste_normal = prediccion*2.5
                llantas_sospechosas = regresion.annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__gt=desgaste_normal).values("llanta__numero_economico").distinct()
            except:
                pass
    # En un futuro poner el parámetro sospechoso para cuando es 1 inspección
    duplicadas = inspecciones.select_related("llanta").values("llanta").annotate(count=Count("llanta")).filter(count=2)
    sin_regresion = inspecciones.select_related("llanta__vehiculo__compania").annotate(poli=Case(When(llanta__in=duplicadas.values("llanta"), then=1), default=0, output_field=IntegerField())).filter(poli=1)
    llantas = sin_regresion.values("llanta").distinct()
    llantas_lista = []
    if llantas_sospechosas:
        llantas_sospechosas_iteracion = True
    else:
        llantas_sospechosas_iteracion = False
    for llanta in llantas:
        fechas = sin_regresion.filter(llanta=llanta["llanta"]).aggregate(primera_fecha=Min("fecha_hora"),ultima_fecha=Max("fecha_hora"))
        dias = abs(fechas["ultima_fecha"] - fechas["primera_fecha"]).days
        #print("llanta: ", Llanta.objects.get(id=llanta["llanta"]))
        #print("dias: ", dias)
        primera_profundidad = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").first())
        ultima_profundidad = min_profundidad(sin_regresion.filter(llanta=llanta["llanta"]).order_by("fecha_hora").last())
        #print("primera_profundidad: ", primera_profundidad)
        #print("ultima_profundidad: ", ultima_profundidad)
        llanta_sospechosa = sin_regresion.filter(llanta=llanta["llanta"]).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField())).filter(min_profundidad__lt = primera_profundidad - (F("llanta__vehiculo__compania__mm_parametro_sospechoso") * dias)).values("llanta").distinct()
        if llanta_sospechosa:
            if not(llanta_sospechosa[0]["llanta"] in llantas_lista):
                if llantas_sospechosas_iteracion:
                    llantas_sospechosas = llantas_sospechosas | llanta_sospechosa
                else:
                    llantas_sospechosas = llanta_sospechosa
                    llantas_sospechosas_iteracion = True
                llantas_lista.append(llanta_sospechosa[0]["llanta"])
    #print(vehiculos_sospechosos)
    return llantas_sospechosas