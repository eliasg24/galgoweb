# Django
from ctypes import alignment
from operator import or_
from http.client import HTTPResponse
import re
import math
from tkinter import CENTER, N
import matplotlib.pyplot as plt
import numpy as np
from django import forms
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse, HttpResponse
from django.db.models.aggregates import Min, Max, Count
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Greatest, Least
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, TemplateView, DetailView, DeleteView, UpdateView, FormView
from django.views.generic.base import View
from psycopg2 import IntegrityError

# Rest Framework

# Functions
from dashboards.functions import functions, functions_ftp, functions_create, functions_excel, functions_api
from aeto import settings

# Forms
from dashboards.forms.forms import EdicionManual, ExcelForm, InspeccionForm, LlantaForm, VehiculoForm, ProductoForm, RenovadorForm, DesechoForm, DesechoEditForm, ObservacionForm, ObservacionEditForm, RechazoForm, RechazoEditForm, SucursalForm, TallerForm, UsuarioForm, AplicacionForm, CompaniaForm, UsuarioEditForm

# Models
from django.contrib.auth.models import User, Group
from dashboards.models import Aplicacion, Bitacora_Pro, Inspeccion, InspeccionVehiculo, Llanta, LlantasSeleccionadas, Producto, Ubicacion, Vehiculo, Perfil, Bitacora, Compania, Renovador, Desecho, Observacion, Rechazo, User, Observacion, Orden, Taller

# Utilities
from multi_form_view import MultiModelFormView
import csv
from datetime import date, datetime, timedelta
import datetime  
from ftplib import FTP as fileTP
import json
import logging
import mimetypes
import openpyxl
from openpyxl.chart import BarChart, Reference
import os
import pandas as pd
from random import sample, randint, uniform, random
from spyne import ComplexModel, Iterable, Array
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.fault import Fault
from spyne.model.primitive import Unicode, Integer, String, Float, Date
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11, Soap12
from spyne.server.django import DjangoApplication
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
import statistics
import xlwt


class ContextoApi(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        #Compañia
        companias = list(perfil.companias.all())
        companias_list = functions_api.companias_list(companias)
        
        #Select
        compania_select = request.GET.get('compania_select', None)
        ubicaciones_select = functions_api.list_select(request.GET.get('ubicaciones_select', None))
        aplicaciones_select = functions_api.list_select(request.GET.get('aplicaciones_select', None))
        talleres_select = functions_api.list_select(request.GET.get('talleres_select', None))

        #Ubicaciones
        ubicaciones = perfil.ubicaciones.all().filter(compania__compania = compania_select)
        ubicaciones_list = functions_api.ubicaciones_list(ubicaciones)
        
        #Aplicacion
        aplicaciones = perfil.aplicaciones.all().filter(ubicacion__nombre__in = ubicaciones_select)
        aplicaciones_list = functions_api.aplicaciones_list(aplicaciones, ubicaciones_select)
        
        #Taller
        taller = perfil.talleres.all().filter(compania__compania = compania_select)
        talleres = functions_api.taller_list(taller)
        dict_context = {
            'companias': companias_list,
            'ubicaciones': ubicaciones_list,
            'aplicaciones': aplicaciones_list,
            'talleres': talleres
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')


class SearchView(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):

        numero_economico = self.request.GET.get("numero_economico")
        fecha1 = self.request.GET.get("fecha_inicio")
        fecha2 = self.request.GET.get("fecha_final")
        color = self.request.GET.getlist("color")

        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        
        page = (int(request.GET['page']) if 'page' in request.GET else 1)

        vehiculos = Vehiculo.objects.filter(compania=Compania.objects.get(compania=self.request.user.perfil.compania), tirecheck=False)
        if numero_economico:
            vehiculos = vehiculos.filter(numero_economico__icontains=numero_economico)
        if fecha1 and fecha2:
            primera_fecha = datetime.datetime.strptime(str(fecha1),"%Y-%m-%d").date()
            segunda_fecha = datetime.datetime.strptime(str(fecha2),"%Y-%m-%d").date()
            vehiculos = vehiculos.filter(fecha_de_inflado__range=[primera_fecha, segunda_fecha]) | Vehiculo.objects.filter(ultima_bitacora_pro__fecha_de_inflado__range=[primera_fecha, segunda_fecha])
        bitacora = Bitacora.objects.filter(compania=Compania.objects.get(compania=self.request.user.perfil.compania))
        bitacora_pro = Bitacora_Pro.objects.filter(compania=Compania.objects.get(compania=self.request.user.perfil.compania))
        llantas = Llanta.objects.filter(vehiculo__compania=Compania.objects.get(compania=self.request.user.perfil.compania), tirecheck=False)
        inspecciones = Inspeccion.objects.filter(llanta__vehiculo__compania=Compania.objects.get(compania=self.request.user.perfil.compania), llanta__tirecheck=False)
        
        filtro_sospechoso = functions.vehiculo_sospechoso(inspecciones)
        vehiculos_sospechosos = vehiculos.filter(id__in=filtro_sospechoso)

        doble_mala_entrada = functions.doble_mala_entrada(bitacora, vehiculos)
        filtro_rojo = functions.vehiculo_rojo(llantas, doble_mala_entrada, vehiculos)
        doble_mala_entrada_pro = functions.doble_mala_entrada_pro(bitacora_pro, vehiculos)
        filtro_rojo_pro = functions.vehiculo_rojo(llantas, doble_mala_entrada_pro, vehiculos)
        vehiculos_rojos = vehiculos.filter(id__in=filtro_rojo).exclude(id__in=vehiculos_sospechosos) | vehiculos.filter(id__in=filtro_rojo_pro).exclude(id__in=vehiculos_sospechosos)

        filtro_amarillo = functions.vehiculo_amarillo(llantas)
        vehiculos_amarillos = vehiculos.filter(id__in=filtro_amarillo).exclude(id__in=vehiculos_rojos).exclude(id__in=vehiculos_sospechosos)

        vehiculos_verdes = vehiculos.exclude(id__in=vehiculos_rojos).exclude(id__in=vehiculos_sospechosos).exclude(id__in=vehiculos_amarillos)

        if "verde" in color:
            if "amarillo" in color:
                if "rojo" in color:
                    if "sospechoso" in color:
                        vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos).filter(id__in=vehiculos_rojos).filter(id__in=vehiculos_amarillos).filter(id__in=vehiculos_verdes)
                    else:
                        vehiculos = vehiculos.filter(id__in=vehiculos_rojos).filter(id__in=vehiculos_amarillos).filter(id__in=vehiculos_verdes)
                else:
                    vehiculos = vehiculos.filter(id__in=vehiculos_amarillos).filter(id__in=vehiculos_verdes)
            elif "rojo" in color:
                if "sospechoso" in color:
                    vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos).filter(id__in=vehiculos_rojos).filter(id__in=vehiculos_verdes)
                else:
                    vehiculos = vehiculos.filter(id__in=vehiculos_rojos).filter(id__in=vehiculos_verdes)
            elif "sospechoso" in color:
                vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos).filter(id__in=vehiculos_verdes)
            else:
                vehiculos = vehiculos.filter(id__in=vehiculos_verdes)
        elif "amarillo" in color:
            if "rojo" in color:
                if "sospechoso" in color:
                    vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos).filter(id__in=vehiculos_rojos).filter(id__in=vehiculos_amarillos)
                else:
                    vehiculos = vehiculos.filter(id__in=vehiculos_rojos).filter(id__in=vehiculos_amarillos)
            elif "sospechoso" in color:
                vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos).filter(id__in=vehiculos_amarillos)
            else:
                vehiculos = vehiculos.filter(id__in=vehiculos_amarillos)
        elif "rojo" in color:
            if "sospechoso" in color:
                vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos).filter(id__in=vehiculos_rojos)
            else:
                vehiculos = vehiculos.filter(id__in=vehiculos_rojos)
        elif "sospechoso" in color:
            vehiculos = vehiculos.filter(id__in=vehiculos_sospechosos)
        

        vehiculos = vehiculos.annotate(color=Case(When(id__in=vehiculos_sospechosos, then=Value("sospechoso")), When(id__in=vehiculos_rojos, then=Value("rojo")), When(id__in=vehiculos_amarillos, then=Value("amarillo")), When(id__in=vehiculos_verdes, then=Value("verde"))))
        try:
            vehiculos_json = list(vehiculos.annotate(fecha2=F("ultima_bitacora_pro__fecha_de_inflado")).annotate(ultima_fecha_de_inflado=Case(When(Q(fecha_de_inflado__gt=F("ultima_bitacora_pro__fecha_de_inflado")) | Q(ultima_bitacora_pro=None), then=F("fecha_de_inflado")), When(Q(ultima_bitacora_pro__fecha_de_inflado__gt=F("fecha_de_inflado")) | Q(fecha_de_inflado=None), then=F("ultima_bitacora_pro__fecha_de_inflado")))).values("id", "numero_economico", "ultima_fecha_de_inflado", "configuracion", "clase", "color"))
        except:
            vehiculos_json = []

        dict_context = {"vehiculos": vehiculos_json,
                        "cantidad_amarillos": len(vehiculos_amarillos),
                        "cantidad_rojos": len(vehiculos_rojos),
                        "cantidad_sospechosos": len(vehiculos_sospechosos),
                        "cantidad_total": len(vehiculos),
                        "cantidad_verdes": len(vehiculos_verdes)
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')
    
    
class NumTireStock(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):

       
        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        talleres = perfil.taller.all()
        compania = perfil.compania
        llantas = Llanta.objects.select_related().filter(compania = compania, taller__in = talleres)
        llantas_rodantes = Llanta.objects.select_related().filter(compania = compania, inventario = "Rodante")
        total_llantas = llantas.count()
        nueva = llantas.filter(inventario = "Nueva").count()
        antes_de_renovar = llantas.filter(inventario = "Antes de Renovar").count()
        antes_de_desechar =llantas.filter(inventario = "Antes de Desechar").count()
        renovada = llantas.filter(inventario = "Renovada").count()
        con_renovador = llantas.filter(inventario = "Con renovador").count()
        desecho_final = llantas.filter(inventario = "Desecho final").count()
        servicio = llantas.filter(inventario = "Servicio").count()
        rodante = llantas_rodantes.count()
        archivado = llantas.filter(inventario = "Archivado").count()
        
        stock_list = [
            {
                'almacen': 'nueva',
                'total': nueva
            },
            {
                'almacen': 'antes_de_renovar',
                'total': antes_de_renovar
            },
            {
                'almacen': 'antes_de_desechar',
                'total': antes_de_desechar
            },
            {
                'almacen': 'renovada',
                'total': renovada
            },
            {
                'almacen': 'con_renovador',
                'total': con_renovador
            },
            {
                'almacen': 'desecho_final',
                'total': desecho_final
            },
            {
                'almacen': 'servicio',
                'total': servicio
            },
            {
                'almacen': 'rodante',
                'total': rodante
            },
            {
                'almacen': 'archivado',
                'total': archivado
            }, 
            
           
        ]
        
        dict_context = {
            'result': stock_list,
            'total_llantas': total_llantas
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)


        return HttpResponse(json_context, content_type='application/json')
    

class TireSearch(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania = compania)
        
        #Queryparams
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        
        eco = (request.GET['eco'] if 'eco' in request.GET else None)
        eco_query = ({'numero_economico__icontains': eco} if  eco != None else {})
        
        inventario = (request.GET['inventario'] if 'inventario' in request.GET else None)
        inventario_query = ({'inventario': inventario} if  inventario != None else {})
        llantas_excluidas = []
        if inventario != None:
            llantas_excluidas = LlantasSeleccionadas.objects.get(perfil=perfil, inventario=inventario).llantas.all().values('numero_economico')
        
        if inventario != 'Rodante':
            taller_query = ({'taller__in': perfil.taller.all()} if  inventario != None else {})
        else:
            taller_query = ({})
        
        producto = (request.GET['producto'].split(',') if 'producto' in request.GET else None)
        producto_query = ({'producto__producto__in': producto} if  producto != None else {})
        
        min_prof = (request.GET['min_prof'] if 'min_prof' in request.GET else None)
        min_prof_query = ({'min_profundidad__gte': min_prof} if  min_prof != None else {})
        
        max_prof = (request.GET['max_prof'] if 'max_prof' in request.GET else None)
        max_prof_query = ({'min_profundidad__lte': max_prof} if  max_prof != None else {})
        
        start_date = ((request.GET['start_date']).split('-') if 'start_date' in request.GET else None)
        start_date_query = ({
            'fecha_de_entrada_inventario__gte': datetime.date(
                int(start_date[0]), int(start_date[1]), int(start_date[2])
                )} if  start_date != None else {})
        
        end_date = ((request.GET['end_date']).split('-') if 'end_date' in request.GET else None)
        end_date_query = ({
            'fecha_de_entrada_inventario__lte': datetime.date(
                int(end_date[0]), int(end_date[1]), int(end_date[2])
                )} if  end_date != None else {})

        
        renovador = (Renovador.objects.get(nombre=request.GET['renovador']) if 'renovador' in request.GET else None)
        renovador_query = ({'renovador': renovador} if  renovador != None else {})
        
        #Color de llanta
        rojos = []
        amarillos = []
        azules = []
        
        for llanta in llantas:
            color = functions.color_observaciones_all_one(llanta)            
            if color == 'bad':
                rojos.append(llanta.id)
            elif color == 'yellow':
                amarillos.append(llanta.id)
            else:
                azules.append(llanta.id)
                
        #Resultado final
        search_first = llantas.filter(
            **eco_query,
            **taller_query
            ).annotate(
                min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), 
                max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha"),
                color=Case(
                    When(id__in=rojos, then=Value("bad")), 
                    When(id__in=amarillos, then=Value("yellow")), 
                    When(id__in=azules, then=Value("good"))
                    )).filter(
                    **inventario_query,
                    **min_prof_query, 
                    **max_prof_query, 
                    **start_date_query,
                    **end_date_query,
                    **renovador_query
                    ).exclude(numero_economico__in = llantas_excluidas)
        
        search = search_first.filter(**producto_query)
        
        #Paginacion
        
        
        datos = search.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        
        print(f'datos: {datos}')
        print(f'size: {size}')
        print(f'pages: {pages}')
        print(f'page: {page}')
        
        pagination = functions.pagination(page, pages)
        
        #Serializar data
        search_list = list(search[offset:limit].values( "numero_economico","color", "id", 'producto__producto','min_profundidad', 'fecha_de_entrada_inventario'))
        
        productos = list(search_first.values(product=F('producto__producto')).distinct())
        
        dict_context = {
            'pagination': pagination,
            'result': search_list,
            'productos': productos
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
    
class TireSearchAlmacen(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania = compania)
        
        #Queryparams
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        
        eco = (request.GET['eco'] if 'eco' in request.GET else None)
        eco_query = ({'numero_economico__icontains': eco} if  eco != None else {})
        
        #Color de llanta
        rojos = []
        amarillos = []
        azules = []
        
        for llanta in llantas:
            color = functions.color_observaciones_all_one(llanta)            
            if color == 'bad':
                rojos.append(llanta.id)
            elif color == 'yellow':
                amarillos.append(llanta.id)
            else:
                azules.append(llanta.id)
                
        #Resultado final
        search_first = llantas.filter(
            **eco_query,
            ).annotate(
                min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), 
                max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha"),
                color=Case(
                    When(id__in=rojos, then=Value("bad")), 
                    When(id__in=amarillos, then=Value("yellow")), 
                    When(id__in=azules, then=Value("good"))
                    ),
                url=Case(
                    When(inventario="Nueva", then=Value("/nueva")),
                    When(inventario="Antes de Renovar", then=Value("/antesRenovar")), 
                    When(inventario="Antes de Desechar", then=Value("/antesDesechar")),
                    When(inventario="Renovada", then=Value("/renovada")),
                    When(inventario="Con renovador", then=Value("/conRenovador")),
                    When(inventario="Desecho final", then=Value("/desechoFinal")),
                    When(inventario="Servicio", then=Value("/servicio")),
                    When(inventario="Rodante", then=Value("/rodante")),
                    When(inventario="Archivado", then=Value("/archivado")),                    
                    )
                )
        
        search = search_first
        
        #Paginacion
        datos = search.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        
        print(f'datos: {datos}')
        print(f'size: {size}')
        print(f'pages: {pages}')
        print(f'page: {page}')
        
        pagination = functions.pagination(page, pages)
        
        #Serializar data
        search_list = list(search[offset:limit].values( "numero_economico","color", "id", 'producto__producto','min_profundidad', 'fecha_de_entrada_inventario', 'url'))

        
        dict_context = {
            'pagination': pagination,
            'result': search_list,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class TireSearchTaller(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania = compania)
        
        #Queryparams
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        
        eco = (request.GET['eco'] if 'eco' in request.GET else None)
        eco_query = ({'numero_economico__icontains': eco} if  eco != None else {})
        
        dimension = (request.GET['dimension'] if 'dimension' in request.GET else None)
        dimension_query = ({'producto__dimension': dimension} if  dimension != None else {})
        
        inventario = (request.GET['inventario'] if 'inventario' in request.GET else None)
        inventario_query = ({'inventario': inventario} if  inventario != None else {})
        
        if inventario != 'Rodante':
            taller_query = ({'taller__in': perfil.taller.all()} if  inventario != None else {})
        else:
            taller_query = ({})
        
        #Color de llanta
        rojos = []
        amarillos = []
        azules = []
        
        for llanta in llantas:
            color = functions.color_observaciones_all_one(llanta)            
            if color == 'bad':
                rojos.append(llanta.id)
            elif color == 'yellow':
                amarillos.append(llanta.id)
            else:
                azules.append(llanta.id)
                
        #Resultado final
        search_first = llantas.filter(
            **eco_query,
            **dimension_query,
            **inventario_query,
            **taller_query
            ).annotate(
                min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), 
                max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")
                )
        
        search = search_first
        
        #Paginacion
        datos = search.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        limit = datos #?Quitar luego
        print(f'datos: {datos}')
        print(f'size: {size}')
        print(f'pages: {pages}')
        print(f'page: {page}')
        
        pagination = functions.pagination(page, pages)
        
        #Serializar data
        search_list = list(search[offset:limit].values( "numero_economico", "id", 'inventario', 'producto__producto', 'producto__dimension', 'min_profundidad', 'fecha_de_entrada_inventario'))

        
        dict_context = {
            'pagination': pagination,
            'result': search_list,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
    
    
class OrdenLlantaNuevaView(LoginRequiredMixin, View):
    # Vista de la orden llanta nueva

    def get(self, request):

        usuario = self.request.user
        talleres = list(Taller.objects.filter(compania=Compania.objects.get(compania=self.request.user.perfil.compania)).values("nombre"))
        productos = list(Producto.objects.filter(compania=Compania.objects.get(compania=self.request.user.perfil.compania)).values("producto"))

        dict_context = {"usuario": usuario,
                        "talleres": talleres,
                        "productos": productos
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class GeneracionLlantaNuevaView(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        
        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        
        jd = json.loads(request.body)
        usuario = jd['usuario']
        fecha = jd['fecha']
        destino = jd['destino']
        productos = jd['producto']
        cantidades = jd['cantidad']

        print(productos)

        fecha = datetime.datetime.now()
        date = datetime.date.today()
        year = str(date.year)[2:]
        month = date.month
        if month < 10:
            month = f"0{month}"
        else:
            month = str(date.month)

        taller = Taller.objects.get(nombre=destino, compania=self.request.user.perfil.compania)
        codigo_taller = taller.codigo
    
        print(destino)

        try: 
            folio = "NT" + codigo_taller
        except: 
            folio = "NT"

        fecha_folio = ""
        for i in str(fecha):
            try:
                if len(fecha_folio) == 13:
                    break
                else:
                    j = int(i)
                    fecha_folio += i
            except:
                pass
        
        folio += fecha_folio

        folio_boolean = False
        folio_iteration = 1
        while folio_boolean == False:
            try:
                orden = Orden.objects.get(folio=folio + f"{folio_iteration}")
            except:
                folio += f"{folio_iteration}"
                folio_boolean = True
            folio_iteration += 1

        dict_data = []


        iteration = 0
        for p in productos:
            producto = productos[iteration]
            print('//////////')
            print(p)
            print(cantidades)
            cantidad = cantidades[iteration]
            num_economicos = []
            for i in range(int(cantidades[iteration])):
                try: 
                    num = codigo_taller + year + month
                except:
                    num = year + month

                num_boolean = False
                num_iteration = 1
                llantas = Llanta.objects.filter(compania=compania, numero_economico__icontains = num)
                print(llantas)                            
                #while num_boolean == False:
                #    try:
                #        llanta = Llanta.objects.get(numero_economico=num + f"{num_iteration}", compania=self.request.user.perfil.compania)
                #    except:
                #        num += f"{num_iteration}"
                #        num_boolean = True
                #    num_iteration += 1
            total = 0
            vuelta = 0
            if vuelta == 0:
                for i in cantidades:
                    total += int(i)
                if llantas.count() == 0:
                    for i in range(1, total+1):
                        num_economicos.append(num+str(i))
                else:
                    last = llantas.last().numero_economico
                    last_num = int(last[(len(codigo_taller) + 4): ])
                    print(last_num)
                    for i in range(1, total+1):
                        num_economicos.append(num+str(i+last_num))

            print(total)
        
            dict_data.append({"producto": producto, "cantidad": cantidades, "num_economicos": num_economicos})
            iteration += 1

        dict_context = {"folio": folio,
                    "usuario": usuario,
                    "fecha": fecha,
                    "destino": destino,
                    "productos": dict_data}
        
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        Orden.objects.create(status="PreOrden", folio=folio, datos=json_context, compania=compania, fecha=fecha.date(), taller=taller)

        return HttpResponse(json_context, content_type='application/json')
    
    
class OrderSearch(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        ordenes = Orden.objects.filter(compania = compania)
        
        #search_list = list(ordenes.values("id", "datos"))
                
        eco = (request.GET['eco'] if 'eco' in request.GET else None)
        eco_query = ({'numero_economico__icontains': eco} if  eco != None else {})
        

        en_espera = list(ordenes.filter(status='PreOrden').values('id', 'folio', 'fecha', 'taller__nombre'))
        historial = list(ordenes.filter(status='Orden').values('id', 'folio', 'fecha', 'taller__nombre').order_by('pk'))
        
        dict_context = {
            'en_espera': en_espera,
            'historial': historial,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class HistoricoDeOrdenApi(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        
        #search_list = list(ordenes.values("id", "datos"))
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        folio = request.GET.get('folio', None)
        folio_query = ({'folio__icontains': folio} if  folio != None else {})
        
        start_date = ((request.GET['start_date']).split('-') if 'start_date' in request.GET else None)
        start_date_query = ({
            'fecha__gte': datetime.date(
                int(start_date[0]), int(start_date[1]), int(start_date[2])
                )} if  start_date != None else {})
        
        end_date = ((request.GET['end_date']).split('-') if 'end_date' in request.GET else None)
        end_date_query = ({
            'fecha__lte': datetime.date(
                int(end_date[0]), int(end_date[1]), int(end_date[2])
                )} if  end_date != None else {})
        
        ordenes = Orden.objects.filter(
            compania = compania,
            **folio_query,
            **start_date_query,**end_date_query
            ).order_by('-pk')
        
        
        datos = ordenes.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        
        print(f'size {size}')
        print(f'page {page}')
        print(f'datos {datos}')
        print(f'pages {pages}')
        print(f'limit {limit}')
        print(f'offset {offset}')
        
        pagination = functions.pagination(page, pages)
        
        datos = list(ordenes[offset:limit].values('id', 'status', 'folio', 'fecha'))
        
        dict_context = {
            'pagination': pagination,
            'datos': datos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class CarritoLlantasApi(LoginRequiredMixin, View):
        # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        try:
            llanta = int(self.request.GET.get('llanta'))
            inventario = (self.request.GET.get('inventario', None))
            functions_api.inventario_none(inventario)
            llanta = Llanta.objects.get(pk=llanta)
            status:str
            try:
                LlantasSeleccionadas.objects.get(perfil=perfil, inventario=inventario).llantas.add(llanta)
                status = 'Llanta Agregada'
            except:
                status = 'Inventario no especificado'
        except:
            status = 'Llanta no encontrada'
        
        dict_context = {
            'status': status
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
    
class CarritoCountApi(LoginRequiredMixin, View):
        # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        inventario = (self.request.GET.get('inventario', None))
        print(inventario)
        try:
            num_llantas = LlantasSeleccionadas.objects.get(perfil=perfil, inventario=inventario).llantas.all().count()
            status = 'Llanta Agregada'
        except:
            status = 'Inventario no encontrado'
            json_context = json.dumps({'numm_llantas': status}, indent=None, sort_keys=False, default=str)

            return HttpResponse(json_context, content_type='application/json')
        
        dict_context = {
            'numm_llantas': num_llantas
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class PanelRenovadoApi(LoginRequiredMixin, View):
        # Vista del panel de renovado

    def get(self, request , *args, **kwargs):

        ids = self.request.GET.get('ids', [])
        ids = str(ids).replace("[", "")
        ids = str(ids).replace("]", "")
        ids_list = ids
        ids = str(ids).split(',')
        print(ids)
        ids = functions.int_list_element(ids)
        llantas = Llanta.objects.filter(id__in=ids)

        try:
            llantas_json = list(llantas.annotate(status=Value("No enviado")).values("id", "numero_economico", "producto__producto", "status"))
        except:
            llantas_json = []

        try:
            productos = list(Producto.objects.filter(compania=self.request.user.perfil.compania).values("producto"))
        except:
            productos = []
        try:
            razones = list(Rechazo.objects.all().values("razon"))
        except:
            razones = []
        try:
            talleres = list(Taller.objects.filter(compania=self.request.user.perfil.compania).values("nombre"))
        except:
            talleres = []

        dict_context = {
            'llantas': llantas_json,
            'productos': productos,
            'razones': razones,
            'talleres': talleres
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')


    
class ProcesoDesechoApi(LoginRequiredMixin, View):
        # Vista del panel de renovado

    def get(self, request , *args, **kwargs):
        
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        
        eco = self.request.GET.get('eco', None)
        eco_query = ({'numero_economico__icontains': eco} if  eco != None else {})
        
        perfil = self.request.GET.get('perfil', [])
        perfil = Perfil.objects.get(pk = int(perfil))
        
        llantas = LlantasSeleccionadas.objects.get(
                perfil = perfil, inventario='Antes de Desechar').llantas.all().annotate(
                    min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")
                        ).filter(
                            **eco_query).values(
                            'id',
                            'numero_economico',
                            'min_profundidad',
                            product=F('producto__producto')
                        )
            


        datos = llantas.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        pagination = functions.pagination(page, pages)
        
        llantas_list = list(llantas[offset:limit])
        
        dict_context = {
            'pagination': pagination,
            'llantas':llantas_list
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class OpcionesDesechoApi(LoginRequiredMixin, View):
        # Vista del panel de renovado

    def get(self, request , *args, **kwargs):
        #Queryparams
        condicion = self.request.GET.get('condicion', None)
        zona = self.request.GET.get('zona', None)
        
        
        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        #Trae todos el catalogo
        opciones_desecho = Desecho.objects.filter(compania = compania)
        condiciones = list(opciones_desecho.values('condicion').distinct())
        zonas = list(opciones_desecho.filter(condicion = condicion).values('zona_de_llanta').distinct())
        razones = list(opciones_desecho.filter(condicion = condicion, zona_de_llanta = zona).values('razon').distinct())
        dict_context = {
            'condiciones': condiciones,
            'zonas': zonas,
            'razones': razones
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class VaciadoCarrito(LoginRequiredMixin, View):
        # Vista del panel de renovado

    def get(self, request , *args, **kwargs):
        #Queryparams
        inventario = self.request.GET.get('inventario', None)
        
        
        
        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        #Trae todos el catalogo
        try:
            carrito = LlantasSeleccionadas.objects.get(perfil = perfil, inventario = inventario)
            carrito.llantas.clear()
            carrito.save()
            status = 'Borrado'
        except:
            status = 'Inventario no encontrado'
        dict_context = {
            'status': status 
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
    
class VehicleAndTireSearchTaller(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request , *args, **kwargs):

        usuario = self.request.user
        perfil = Perfil.objects.get(user = usuario)
        compania = perfil.compania
        
        
        #Queryparams
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        
        eco = (request.GET['eco'] if 'eco' in request.GET else None)
        eco_query = ({'numero_economico__icontains': eco} if  eco != None else {})
        
        id_seletct = (request.GET['id_select'] if 'id_select' in request.GET else -1)
        id_seletct_query = ({'vehiculo__id': id_seletct})
        print(id_seletct)
        print(id_seletct_query)
        
        vehiculos = Vehiculo.objects.filter(
            compania = compania,
            **eco_query
        ).values('id', 'numero_economico')
        
        #Paginacion
        datos = vehiculos.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        limit = datos #?Quitar luego
        print(f'datos: {datos}')
        print(f'size: {size}')
        print(f'pages: {pages}')
        print(f'page: {page}')
        
        pagination = functions.pagination(page, pages)
        
        #Llantas
        
        llantas = Llanta.objects.filter(
            **id_seletct_query
        )

        #Color de llanta
        rojos = []
        amarillos = []
        azules = []
        
        for llanta in llantas:
            color = functions.color_observaciones_all_one(llanta)            
            if color == 'bad':
                rojos.append(llanta.id)
            elif color == 'yellow':
                amarillos.append(llanta.id)
            else:
                azules.append(llanta.id)
               
        #Resultado final
        llantas = llantas.annotate(
                min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), 
                max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha")
                ) 
       
        #Serializar data
        vehiculos_list = list(vehiculos[offset:limit])
        
        llantas_list = list(llantas.values( "numero_economico", "id", "posicion"))

        
        dict_context = {
            'pagination': pagination,
            'vehiculos_list': vehiculos_list,
            'llantas': llantas_list,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class PulpoApiView(View):
    # Vista del dashboard pulpo
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, user):

        my_profile = Perfil.objects.get(user__username=self.kwargs['user'])
        compania = Compania.objects.get(compania=my_profile.compania)

        vehiculo = Vehiculo.objects.filter(compania=compania)
        bitacora = Bitacora.objects.filter(compania=compania)
        bitacora_pro = Bitacora_Pro.objects.filter(compania=compania)
        hoy = date.today()

        #functions_create.crear_de_bitacora_el_vehiculo()
        #functions_create.crear_inspecciones(self.request.my_profile)
        #functions_excel.excel_productos()
        #functions_excel.excel_observaciones()
        #functions_create.borrar_ultima_inspeccion_vehiculo()
        #functions_create.convertir_vehiculos()
        #functions_create.borrar_km_actuales()
        #functions_ftp.ftp_diario()
        ultimo_mes = hoy - timedelta(days=31)

        #functions_create.tirecheck_llanta()
        #functions_create.borrar_ultima_inspeccion_vehiculo()
        #functions_excel.excel_vehiculos()
        #functions_excel.excel_llantas(User.objects.get(username="equipo-logistico"))
        #functions_excel.excel_inspecciones()

        mes_1 = hoy.strftime("%b")
        mes_2 = functions.mes_anterior(hoy)
        mes_3 = functions.mes_anterior(mes_2)
        mes_4 = functions.mes_anterior(mes_3)
        mes_5 = functions.mes_anterior(mes_4)

        hoy1 = hoy.strftime("%m")
        hoy2 = mes_2.strftime("%m")
        hoy3 = mes_3.strftime("%m")
        hoy4 = mes_4.strftime("%m")
        hoy5 = mes_5.strftime("%m")

        vehiculo_fecha = vehiculo.filter(fecha_de_inflado__range=[ultimo_mes, hoy])
        vehiculo_fecha_pro = vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__range=[ultimo_mes, hoy])
        vehiculo_fecha_total = vehiculo.filter(fecha_de_inflado__range=[ultimo_mes, hoy]) | vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__range=[ultimo_mes, hoy])
        vehiculo_fecha_barras_1 = vehiculo.filter(fecha_de_inflado__month=hoy1) | vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__month=hoy1)
        vehiculo_fecha_barras_2 = vehiculo.filter(fecha_de_inflado__month=hoy2) | vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__month=hoy2)
        vehiculo_fecha_barras_3 = vehiculo.filter(fecha_de_inflado__month=hoy3) | vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__month=hoy3)
        vehiculo_fecha_barras_4 = vehiculo.filter(fecha_de_inflado__month=hoy4) | vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__month=hoy4)
        vehiculo_fecha_barras_5 = vehiculo.filter(fecha_de_inflado__month=hoy5) | vehiculo.filter(ultima_bitacora_pro__fecha_de_inflado__month=hoy5)
        
        vehiculo_mes1 = bitacora.filter(fecha_de_inflado__month=hoy1)
        vehiculo_mes2 = bitacora.filter(fecha_de_inflado__month=hoy2)
        vehiculo_mes3 = bitacora.filter(fecha_de_inflado__month=hoy3)
        vehiculo_mes4 = bitacora.filter(fecha_de_inflado__month=hoy4)

        vehiculo_pro_mes1 = bitacora_pro.filter(fecha_de_inflado__month=hoy1)
        vehiculo_pro_mes2 = bitacora_pro.filter(fecha_de_inflado__month=hoy2)
        vehiculo_pro_mes3 = bitacora_pro.filter(fecha_de_inflado__month=hoy3)
        vehiculo_pro_mes4 = bitacora_pro.filter(fecha_de_inflado__month=hoy4)

        entrada_correcta_contar = functions.contar_entrada_correcta(vehiculo_fecha)
        entrada_correcta_contar += functions.contar_entrada_correcta_pro(vehiculo_fecha_pro)
        mala_entrada_contar_mes1 = functions.contar_mala_entrada(vehiculo_mes1)
        mala_entrada_contar_mes2 = functions.contar_mala_entrada(vehiculo_mes2)
        mala_entrada_contar_mes3 = functions.contar_mala_entrada(vehiculo_mes3)
        mala_entrada_contar_mes4 = functions.contar_mala_entrada(vehiculo_mes4)

        mala_entrada_contar_mes1 += functions.contar_mala_entrada_pro(vehiculo_pro_mes1)
        mala_entrada_contar_mes2 += functions.contar_mala_entrada_pro(vehiculo_pro_mes2)
        mala_entrada_contar_mes3 += functions.contar_mala_entrada_pro(vehiculo_pro_mes3)
        mala_entrada_contar_mes4 += functions.contar_mala_entrada_pro(vehiculo_pro_mes4)

        entrada_correcta_contar_barras_mes1 = functions.contar_entrada_correcta(vehiculo_fecha_barras_1)
        entrada_correcta_contar_barras_mes2 = functions.contar_entrada_correcta(vehiculo_fecha_barras_2)
        entrada_correcta_contar_barras_mes3 = functions.contar_entrada_correcta(vehiculo_fecha_barras_3)
        entrada_correcta_contar_barras_mes4 = functions.contar_entrada_correcta(vehiculo_fecha_barras_4)
        entrada_correcta_contar_barras_mes5 = functions.contar_entrada_correcta(vehiculo_fecha_barras_5)

        doble_entrada = functions.doble_entrada(bitacora, bitacora_pro) 
        doble_mala_entrada = functions.doble_mala_entrada(bitacora, vehiculo)

        doble_mala_entrada_pro = functions.doble_mala_entrada_pro(bitacora_pro, vehiculo)

        vehiculo_periodo = vehiculo.filter(fecha_de_inflado__lte=ultimo_mes).filter(ultima_bitacora_pro=None) | vehiculo.filter(fecha_de_inflado=None).filter(ultima_bitacora_pro__fecha_de_inflado__lte=ultimo_mes) | vehiculo.filter(fecha_de_inflado=None).filter(ultima_bitacora_pro=None) | vehiculo.filter(fecha_de_inflado__lte=ultimo_mes).filter(ultima_bitacora_pro__fecha_de_inflado__lte=ultimo_mes)
        vehiculo_periodo_status = []
        mala_entrada_periodo = functions.mala_entrada(vehiculo_periodo) | functions.mala_entrada_pro(vehiculo_periodo)
        for v in vehiculo_periodo:
            v = {"id":v.id, "numero_economico":v.numero_economico, "clase":v.clase}
            try:
                if v in doble_mala_entrada or v in doble_mala_entrada_pro:
                    v["status"] = "Doble Entrada"
                elif v in mala_entrada_periodo:
                    v["status"] = "Mala Entrada"
                else:
                    v["status"] = "Entrada Correctas"
            except:
                v["status"] = "Entrada Correctas"
            vehiculo_periodo_status.append(v)

        vehiculo_malos_status = []
        mala_entrada = functions.mala_entrada(vehiculo) | functions.mala_entrada_pro(vehiculo)
        for v in vehiculo:
            v = {"id":v.id, "numero_economico":v.numero_economico, "clase":v.clase}
            try:
                if v in doble_mala_entrada or v in doble_mala_entrada_pro:
                    v["status"] = "Doble Entrada"
                elif v in mala_entrada:
                    v["status"] = "Mala Entrada"
            except:
                pass
            vehiculo_malos_status.append(v)


        radar_min = functions.radar_min(vehiculo_fecha_total, my_profile.compania)
        radar_max = functions.radar_max(vehiculo_fecha_total, my_profile.compania)
        radar_min_resta = functions.radar_min_resta(radar_min, radar_max)

        """functions.crear_1(numero_economico="P5",
        compania="pruebacal",
        ubicacion="DOS",
        aplicacion="FORANEO",
        clase="CAMIONETA",
        configuracion="S2.D2", 
        tiempo_de_inflado=2.5,
        presion_de_entrada=100,
        presion_de_salida=100,
        presion_establecida=100)"""

        #functions.crear_3(Vehiculo.objects.get(numero_economico="P5"))

        try:
            aplicaciones = list(functions.aplicaciones_mas_frecuentes(vehiculo_fecha_total, vehiculo, my_profile.compania))
        except:
            aplicaciones = []

        try:
            bitacoras = list(bitacora.values("id", "fecha_de_inflado"))
        except:
            bitacoras = []

        try:
            bitacoras_pro = list(bitacora_pro.values("id", "fecha_de_inflado"))
        except:
            bitacoras_pro = []

        try:
            vehiculos = list(vehiculo.values("id", "fecha_de_inflado", "ultima_bitacora_pro__fecha_de_inflado"))
        except:
            vehiculos = []

        clases_compania_list = []
        clases_compania = functions.clases_mas_frecuentes(vehiculo, my_profile.compania)
        for c in clases_compania:
            clase_compania = {"clase": c, "porcentaje": clases_compania[c]}
            clases_compania_list.append(clase_compania)

        clases_mas_frecuentes_infladas_list = []
        clases_mas_frecuentes_infladas = functions.clases_mas_frecuentes(vehiculo_fecha_total, my_profile.compania)
        for c in clases_mas_frecuentes_infladas:
            clase_mas_frecuente = {"clase": c, "porcentaje": clases_mas_frecuentes_infladas[c]}
            clases_mas_frecuentes_infladas_list.append(clase_mas_frecuente)


        dict_context = {
            "aplicaciones_mas_frecuentes_infladas": aplicaciones,
            "bitacoras": bitacoras,
            "bitacoras_pro": bitacoras_pro,
            "boton_intuitivo": "Vehículos Vencidos",
            "cantidad_inflado": vehiculo_fecha_total.count(),
            "cantidad_inflado_1": vehiculo_fecha_barras_1.count(),
            "cantidad_inflado_2": vehiculo_fecha_barras_2.count(),
            "cantidad_inflado_3": vehiculo_fecha_barras_3.count(),
            "cantidad_inflado_4": vehiculo_fecha_barras_4.count(),
            "cantidad_inflado_5": vehiculo_fecha_barras_5.count(),
            "cantidad_entrada": entrada_correcta_contar,
            "cantidad_entrada_barras_mes1": entrada_correcta_contar_barras_mes1,
            "cantidad_entrada_barras_mes2": entrada_correcta_contar_barras_mes2,
            "cantidad_entrada_barras_mes3": entrada_correcta_contar_barras_mes3,
            "cantidad_entrada_barras_mes4": entrada_correcta_contar_barras_mes4,
            "cantidad_entrada_barras_mes5": entrada_correcta_contar_barras_mes5,
            "cantidad_entrada_mes1": mala_entrada_contar_mes1,
            "cantidad_entrada_mes2": mala_entrada_contar_mes2,
            "cantidad_entrada_mes3": mala_entrada_contar_mes3,
            "cantidad_entrada_mes4": mala_entrada_contar_mes4,
            "cantidad_total": vehiculo.count(),
            "clases_compania": clases_compania_list,
            "clases_mas_frecuentes_infladas": clases_mas_frecuentes_infladas_list,
            "compania": my_profile.compania,
            "doble_entrada": [doble_entrada[2], doble_entrada[3]],
            "flotas": list(Ubicacion.objects.filter(compania=compania)),
            "hoy": hoy,
            "mes_1": mes_1,
            "mes_2": mes_2.strftime("%b"),
            "mes_3": mes_3.strftime("%b"),
            "mes_4": mes_4.strftime("%b"),
            "mes_5": mes_5.strftime("%b"),
            "porcentaje_inflado": functions.porcentaje(vehiculo_fecha_total.count(), vehiculo.count()),
            "porcentaje_entrada_correcta": functions.porcentaje(entrada_correcta_contar, vehiculo_fecha_total.count()),
            "radar_min": radar_min_resta,
            "radar_max": radar_max,
            "rango_1": my_profile.compania.periodo1_inflado,
            "rango_2": my_profile.compania.periodo2_inflado,
            "rango_3": my_profile.compania.periodo1_inflado + 1,
            "rango_4": my_profile.compania.periodo2_inflado + 1,
            "tiempo_promedio": functions.inflado_promedio(vehiculo_fecha_total),
            "vehiculos_malos": vehiculo_malos_status,
            "vehiculos_periodo": vehiculo_periodo_status,
            "vehiculos_todos": vehiculos
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')