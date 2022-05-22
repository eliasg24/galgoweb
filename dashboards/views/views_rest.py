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
from dashboards.functions import functions, functions_ftp, functions_create, functions_excel
from aeto import settings

# Forms
from dashboards.forms.forms import EdicionManual, ExcelForm, InspeccionForm, LlantaForm, VehiculoForm, ProductoForm, RenovadorForm, DesechoForm, DesechoEditForm, ObservacionForm, ObservacionEditForm, RechazoForm, RechazoEditForm, SucursalForm, TallerForm, UsuarioForm, AplicacionForm, CompaniaForm, UsuarioEditForm

# Models
from django.contrib.auth.models import User, Group
from dashboards.models import Aplicacion, Bitacora_Pro, Inspeccion, InspeccionVehiculo, Llanta, Producto, Ubicacion, Vehiculo, Perfil, Bitacora, Compania, Renovador, Desecho, Observacion, Rechazo, User, Observacion, Orden, Taller

# Utilities
from multi_form_view import MultiModelFormView
import csv
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

class SearchView(LoginRequiredMixin, View):
    # Vista del dashboard buscar_vehiculos

    def get(self, request):

        numero_economico = self.request.GET.get("numero_economico")
        fecha1 = self.request.GET.get("fecha_inicio")
        fecha2 = self.request.GET.get("fecha_final")
        color = self.request.GET.getlist("color")

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
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania = compania)
        total_llantas = llantas.count()
        nueva = llantas.filter(compania = compania, inventario = "Nueva").count()
        antes_de_renovar = llantas.filter(compania = compania, inventario = "Antes de Renovar").count()
        antes_de_desechar =llantas.filter(compania = compania, inventario = "Antes de Desechar").count()
        renovada = llantas.filter(compania = compania, inventario = "Renovada").count()
        con_renovador = llantas.filter(compania = compania, inventario = "Con renovador").count()
        desecho_final = llantas.filter(compania = compania, inventario = "Desecho final").count()
        servicio = llantas.filter(compania = compania, inventario = "Servicio").count()
        rodante = llantas.filter(compania = compania, inventario = "Rodante").count()
        archivado = llantas.filter(compania = compania, inventario = "Archivado").count()
        
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
        
        producto = (request.GET['producto'].split(',') if 'producto' in request.GET else None)
        producto_query = ({'producto__producto__in': producto} if  producto != None else {})
        
        min_prof = (request.GET['min_prof'] if 'min_prof' in request.GET else None)
        min_prof_query = ({'min_profundidad__gte': min_prof} if  min_prof != None else {})
        
        max_prof = (request.GET['max_prof'] if 'max_prof' in request.GET else None)
        max_prof_query = ({'min_profundidad__lte': max_prof} if  max_prof != None else {})
        
        start_date = ((request.GET['start_date']).split('/') if 'start_date' in request.GET else None)
        start_date_query = ({
            'fecha_de_entrada_inventario__gte': datetime.date(
                int(start_date[2]), int(start_date[1]), int(start_date[0])
                )} if  start_date != None else {})
        
        end_date = ((request.GET['end_date']).split('/') if 'end_date' in request.GET else None)
        end_date_query = ({
            'fecha_de_entrada_inventario__lte': datetime.date(
                int(end_date[2]), int(end_date[1]), int(end_date[0])
                )} if  end_date != None else {})

        #Color de llanta
        rojos = []
        amarillos = []
        azules = []
        
        for llanta in llantas:
            if llanta.ultima_inspeccion != None:
                color = functions.color_observaciones_all_one(llanta.ultima_inspeccion)
                if color == 'bad':
                    rojos.append(llanta.id)
                elif color == 'yellow':
                    amarillos.append(llanta.id)
                else:
                    azules.append(llanta.id)
            else:
               azules.append(llanta.id) 
                    
        #Resultado final
        search = llantas.filter(
            **eco_query).annotate(
                min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"), 
                max_profundidad=Greatest("profundidad_izquierda", "profundidad_central", "profundidad_derecha"),
                color=Case(
                    When(id__in=rojos, then=Value("bad")), 
                    When(id__in=amarillos, then=Value("yellow")), 
                    When(id__in=azules, then=Value("good"))
                    )).filter(
                    **inventario_query,
                    **producto_query,
                    **min_prof_query, 
                    **max_prof_query, 
                    **start_date_query,
                    **end_date_query
                    )
        
        
        #Paginacion
        
        
        datos = search.count()  
        pages = (math.ceil(datos/size))
        limit = page * size
        offset = limit - size
        
        pagination = functions.pagination(page, pages)
        
        #Serializar data
        search_list = list(search[offset:limit].values( "numero_economico","color", "id", 'producto__producto','min_profundidad', 'fecha_de_entrada_inventario'))
        
        productos = list(search.values(product=F('producto__producto')).distinct())
        
        dict_context = {
            'pagination': pagination,
            'result': search_list,
            'productos': productos
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
        ordenes = Orden.objects.filter(compania = compania).order_by('-pk')
        
        #search_list = list(ordenes.values("id", "datos"))
        size = (int(request.GET['size']) if 'size' in request.GET else 10)
        page = (int(request.GET['page']) if 'page' in request.GET else 1)
        
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