from datetime import date
from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView, TemplateView, DetailView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
import numpy

from dashboards.models import Aplicacion, Compania, Inspeccion, InspeccionVehiculo, Llanta, Rendimiento, Tendencia, TendenciaAplicacion, TendenciaCompania, TendenciaUbicacion, Ubicacion, Vehiculo

from utilidades.functions import functions
from dashboards.functions import functions as func

import json
from django.http import HttpResponse
from django.views.generic.base import View

import dashboards.functions.functions_create as func_create

from dashboards.functions.functions import DiffDays, CastDate
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func, OuterRef, Subquery, Sum
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest, TruncDate
# Create your views here.

class UtilidadesView(LoginRequiredMixin, TemplateView):
    # Vista de CatalogoDesechosView

    template_name = "utilidades/utilidades.html"
    
def subirBigData(request): 
    #func_create.crear_big_data_chida()
    return redirect("utilidades:utilidades")
    
def corregirInspeccionesVehiculo(request):
    compania = Compania.objects.get(compania='PruebaBI')
    inspecciones_vehiculos = InspeccionVehiculo.objects.all()
    for inspeccion in inspecciones_vehiculos:
        user = None
        inspeccion_llanta = Inspeccion.objects.filter(inspeccion_vehiculo=inspeccion)
        for ins in inspeccion_llanta:
            if ins.usuario != None:
                user = ins.usuario
        inspeccion.usuario = user

    InspeccionVehiculo.objects.bulk_update(inspecciones_vehiculos, ['usuario'])
        
    return redirect('utilidades:utilidades')

def guardar_estado_actual_llantas2(request):
    
    
    compania = Compania.objects.get(compania='PruebaBI')
    vehiculos = Vehiculo.objects.filter(compania=compania)
    llantas = Llanta.objects.filter(vehiculo__in = vehiculos).exclude(inventario='Nueva')
    
    km_actuales = llantas.exclude(km_actual = None).values_list("km_actual", flat=True)
    numero_elementos = km_actuales.count()
    km_actuales_list = list(km_actuales)
    pq_1 = functions.percentil(km_actuales_list, 1, numero_elementos)
    pq_3 = functions.percentil(km_actuales_list, 3, numero_elementos)
    print(pq_1)
    print(pq_3)
    km_filtrados = llantas.filter(km_actual__gte = pq_1, km_actual__lte = pq_3).exclude(km_actual = None)
    km_filtrados_list = list(km_filtrados.values_list("km_actual", flat=True))
    km_filtrados_list.sort()
    print(km_filtrados_list)
    mediana = numpy.median(km_filtrados_list, axis = None)
    print(mediana)
    std = numpy.std(km_filtrados_list, axis=None, dtype=numpy.float64)
    print(std)
    
    limite_inferior = mediana - (2*std)
    limite_superior = mediana + (2*std)
    
    print(limite_inferior)
    print(limite_superior)
    
    datos = []
    datos_data = []
    
    for llanta in llantas:
        mm_desgastados = functions.mm_desgastasdos(llanta)
        porcentaje_de_desgaste = functions.porcentaje_de_desgaste(llanta)
        km_x_mm = functions.km_x_mm(llanta)
        km_proyectado = functions.km_proyectado(llanta)
        cpk_proyectado = functions.cpk_proyectado(llanta)
        cpk_real = functions.cpk_real(llanta)


        try:
            prof_inical = llanta.producto.profundidad_inicial
        except:
            prof_inical = None
        try:    
            if(
                porcentaje_de_desgaste > .15
                and
                llanta.km_actual > limite_inferior
                and
                llanta.km_actual < limite_superior

                ):
                is_analizada = True
            else:
                is_analizada = False

        except:
            is_analizada = False
            
        punto_retiro = func.punto_de_retiro(llanta)
        minima = func.min_profundidad(llanta)

        datos.append({
                        'llanta': llanta,
                        'mm_desgastados': mm_desgastados, 
                        'porcentaje_de_desgaste': porcentaje_de_desgaste,
                        'profundidad_inicial': prof_inical,
                        'punto_retiro': punto_retiro,
                        'minima': minima,
                        'km_x_mm': km_x_mm,
                        'km_proyectado': km_proyectado,
                        'cpk_proyectado': cpk_proyectado,
                        'cpk_real': cpk_real,
                        'is_analizada': is_analizada
                        })
        datos_data.append(
            Rendimiento(
                year = date.today().year,
                mes = 7,
                llanta = llanta,
                mm_desgastados = mm_desgastados,
                porcentaje_de_desgaste = porcentaje_de_desgaste,
                km_x_mm = km_x_mm,
                km_proyectado = km_proyectado,
                is_analizada = is_analizada,
                cpk_proyectado = cpk_proyectado,
                cpk_real = cpk_real,
            ))
    objs = Rendimiento.objects.bulk_create(datos_data)
    
    return render(request, 'utilidades/datos.html',{
        'datos': datos,
        'km_actuales': km_actuales
    } )
    
    
def BorrarRendimientos(request):
    rendimiento = Rendimiento.objects.all()
    for r in rendimiento:
        r.delete()
    
        
    return redirect('utilidades:utilidades')



class DailyDataTendenciasCompanias(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        datos_data = []
        
        companias = Compania.objects.all()
        for compania in companias:
            ubicaciones = Ubicacion.objects.filter(compania = compania)
            num_ubicaciones = ubicaciones.count()
            periodo1_inflado = compania.periodo1_inflado
            periodo2_inflado = compania.periodo2_inflado
            
            periodo1_inspeccion = compania.periodo1_inspeccion
            periodo2_inspeccion = compania.periodo2_inspeccion
            
            vehiculos = Vehiculo.objects.filter(compania = compania)
            num_vehiculos = vehiculos.count()
            if num_vehiculos == 0:
                continue
            
            vehiculos_clase = vehiculos
            num_vehiculos_clase = vehiculos_clase.count()
            
            #? Variables:
            a_tiempo_pulpo:float
            correctas_pulpo:float
            inspecciones_a_tiempo:float
            health:float
            buena_presion:float
            
            #? a tiempo de pulpo
            vehiculos_con_pulpo = vehiculos_clase
            vehiculos_con_pulpo = vehiculos_con_pulpo.exclude(
                    fecha_de_inflado = None
                ).annotate(
                    dias_sin_inflar=DiffDays(
                        CastDate(Now())-CastDate(F('fecha_de_inflado')), 
                        output_field=IntegerField()
                        ),
                ).filter(
                    dias_sin_inflar__lte = periodo1_inflado
                ).count()
            
            a_tiempo_pulpo = ( ( vehiculos_con_pulpo * 100 ) / num_vehiculos_clase ) / 100
            
            #? Correctas pulpo
            vehiculos_correctas_pulpo = vehiculos_clase
            vehiculos_correctas_pulpo = vehiculos_correctas_pulpo.exclude(
                    observaciones_llanta__observacion__in=["Doble mala entrada"]
                ).exclude(
                    observaciones_llanta__observacion__in=["Mala entrada"]
                ).count()
            
            correctas_pulpo = ( ( vehiculos_correctas_pulpo * 100 ) / num_vehiculos_clase ) / 100
            #correctas_pulpo = vehiculos_correctas_pulpo
            
            
            #? Inspeccion a tiempo
            vehiculos_inspeccion = vehiculos_clase
            vehiculos_inspeccion = vehiculos_inspeccion.exclude(
                fecha_ultima_inspeccion = None
            ).annotate(
                dias_sin_inspeccion = DiffDays(
                    CastDate(Now()) - CastDate(F('fecha_ultima_inspeccion')), 
                    output_field=IntegerField()
                    ), 
            ).filter(
                dias_sin_inspeccion__lte = periodo1_inspeccion
            ).count()
            
            
            inspecciones_a_tiempo = ( ( vehiculos_inspeccion * 100 ) / num_vehiculos_clase ) / 100
            
            #? Health
            vehiculos_health = vehiculos_clase
            vehiculos_health = vehiculos_health.filter(
                observaciones_llanta__observacion = None
            ).count()
            
            health = ( ( vehiculos_health * 100 ) / num_vehiculos_clase ) / 100
            
            #? Buena presion
            vehiculos_buena_presion = vehiculos_clase
            vehiculos_buena_presion = vehiculos_buena_presion.exclude(
                observaciones_llanta__observacion__in=["Alta presion"]
            ).exclude(
                observaciones_llanta__observacion__in=["Baja presión"]
            ).count()
            
            buena_presion = ( ( vehiculos_buena_presion * 100 ) / num_vehiculos_clase ) / 100
            
            print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
            print(f'correctas_pulpo: {correctas_pulpo}')
            print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
            print(f'health: {health}')
            print(f'buena_presion: {buena_presion}')
            print(num_vehiculos_clase)
            print('--------')
            
            datos_data.append( TendenciaCompania(
                fecha = date.today(),
                compania = compania,
                correctas_pulpo = correctas_pulpo,
                inspecciones_a_tiempo = inspecciones_a_tiempo,
                health = health,
                buena_presion = buena_presion
            ) ) 
                
        objs = TendenciaCompania.objects.bulk_create(datos_data)
        
        dict_context = {
            'compania': 'compania',
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')




class DailyDataTendenciasUbicaciones(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        datos_data = []
        
        companias = Compania.objects.all()
        for compania in companias:
            ubicaciones = Ubicacion.objects.filter(compania = compania)
            num_ubicaciones = ubicaciones.count()
            periodo1_inflado = compania.periodo1_inflado
            periodo2_inflado = compania.periodo2_inflado
            
            periodo1_inspeccion = compania.periodo1_inspeccion
            periodo2_inspeccion = compania.periodo2_inspeccion
            if num_ubicaciones == 0:
                continue
            print(compania)
            print(num_ubicaciones)
            for ubicacion in ubicaciones:
                
                vehiculos = Vehiculo.objects.filter(compania = compania, ubicacion = ubicacion)
                num_vehiculos = vehiculos.count()
                if num_vehiculos == 0:
                    continue
                
                vehiculos_clase = vehiculos
                num_vehiculos_clase = vehiculos_clase.count()
                
                #? Variables:
                a_tiempo_pulpo:float
                correctas_pulpo:float
                inspecciones_a_tiempo:float
                health:float
                buena_presion:float
                
                #? a tiempo de pulpo
                vehiculos_con_pulpo = vehiculos_clase
                vehiculos_con_pulpo = vehiculos_con_pulpo.exclude(
                        fecha_de_inflado = None
                    ).annotate(
                        dias_sin_inflar=DiffDays(
                            CastDate(Now())-CastDate(F('fecha_de_inflado')), 
                            output_field=IntegerField()
                            ),
                    ).filter(
                        dias_sin_inflar__lte = periodo1_inflado
                    ).count()
                
                a_tiempo_pulpo = ( ( vehiculos_con_pulpo * 100 ) / num_vehiculos_clase ) / 100
                
                #? Correctas pulpo
                vehiculos_correctas_pulpo = vehiculos_clase
                vehiculos_correctas_pulpo = vehiculos_correctas_pulpo.exclude(
                        observaciones_llanta__observacion__in=["Doble mala entrada"]
                    ).exclude(
                        observaciones_llanta__observacion__in=["Mala entrada"]
                    ).count()
                
                correctas_pulpo = ( ( vehiculos_correctas_pulpo * 100 ) / num_vehiculos_clase ) / 100
                #correctas_pulpo = vehiculos_correctas_pulpo
                
                
                #? Inspeccion a tiempo
                vehiculos_inspeccion = vehiculos_clase
                vehiculos_inspeccion = vehiculos_inspeccion.exclude(
                    fecha_ultima_inspeccion = None
                ).annotate(
                    dias_sin_inspeccion = DiffDays(
                        CastDate(Now()) - CastDate(F('fecha_ultima_inspeccion')), 
                        output_field=IntegerField()
                        ), 
                ).filter(
                    dias_sin_inspeccion__lte = periodo1_inspeccion
                ).count()
                
                
                inspecciones_a_tiempo = ( ( vehiculos_inspeccion * 100 ) / num_vehiculos_clase ) / 100
                
                #? Health
                vehiculos_health = vehiculos_clase
                vehiculos_health = vehiculos_health.filter(
                    observaciones_llanta__observacion = None
                ).count()
                
                health = ( ( vehiculos_health * 100 ) / num_vehiculos_clase ) / 100
                
                #? Buena presion
                vehiculos_buena_presion = vehiculos_clase
                vehiculos_buena_presion = vehiculos_buena_presion.exclude(
                    observaciones_llanta__observacion__in=["Alta presion"]
                ).exclude(
                    observaciones_llanta__observacion__in=["Baja presión"]
                ).count()
                
                buena_presion = ( ( vehiculos_buena_presion * 100 ) / num_vehiculos_clase ) / 100
                
                print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
                print(f'correctas_pulpo: {correctas_pulpo}')
                print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
                print(f'health: {health}')
                print(f'buena_presion: {buena_presion}')
                print(num_vehiculos_clase)
                print('--------')
                
                datos_data.append( TendenciaUbicacion(
                    fecha = date.today(),
                    compania = compania,
                    ubicacion = ubicacion,
                    correctas_pulpo = correctas_pulpo,
                    inspecciones_a_tiempo = inspecciones_a_tiempo,
                    health = health,
                    buena_presion = buena_presion
                ) ) 
                
        objs = TendenciaUbicacion.objects.bulk_create(datos_data)
        
        dict_context = {
            'compania': 'compania',
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')






class DailyDataTendenciasAplicaciones(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        datos_data = []
        
        companias = Compania.objects.all()
        for compania in companias:
            ubicaciones = Ubicacion.objects.filter(compania = compania)
            num_ubicaciones = ubicaciones.count()
            periodo1_inflado = compania.periodo1_inflado
            periodo2_inflado = compania.periodo2_inflado
            
            periodo1_inspeccion = compania.periodo1_inspeccion
            periodo2_inspeccion = compania.periodo2_inspeccion
            if num_ubicaciones == 0:
                continue
            print(compania)
            print(num_ubicaciones)
            for ubicacion in ubicaciones:
                aplicaciones = Aplicacion.objects.filter(ubicacion = ubicacion)
                num_aplicaciones = aplicaciones.count()
                if num_aplicaciones == 0:
                    continue
                print(ubicacion)
                for aplicacion in aplicaciones:
                    vehiculos = Vehiculo.objects.filter(compania = compania, ubicacion = ubicacion, aplicacion = aplicacion)
                    num_vehiculos = vehiculos.count()
                    if num_vehiculos == 0:
                        continue
                    
                    vehiculos_clase = vehiculos
                    num_vehiculos_clase = vehiculos_clase.count()
                    
                    #? Variables:
                    a_tiempo_pulpo:float
                    correctas_pulpo:float
                    inspecciones_a_tiempo:float
                    health:float
                    buena_presion:float
                    
                    #? a tiempo de pulpo
                    vehiculos_con_pulpo = vehiculos_clase
                    vehiculos_con_pulpo = vehiculos_con_pulpo.exclude(
                            fecha_de_inflado = None
                        ).annotate(
                            dias_sin_inflar=DiffDays(
                                CastDate(Now())-CastDate(F('fecha_de_inflado')), 
                                output_field=IntegerField()
                                ),
                        ).filter(
                            dias_sin_inflar__lte = periodo1_inflado
                        ).count()
                    
                    a_tiempo_pulpo = ( ( vehiculos_con_pulpo * 100 ) / num_vehiculos_clase ) / 100
                    
                    #? Correctas pulpo
                    vehiculos_correctas_pulpo = vehiculos_clase
                    vehiculos_correctas_pulpo = vehiculos_correctas_pulpo.exclude(
                            observaciones_llanta__observacion__in=["Doble mala entrada"]
                        ).exclude(
                            observaciones_llanta__observacion__in=["Mala entrada"]
                        ).count()
                    
                    correctas_pulpo = ( ( vehiculos_correctas_pulpo * 100 ) / num_vehiculos_clase ) / 100
                    #correctas_pulpo = vehiculos_correctas_pulpo
                    
                    
                    #? Inspeccion a tiempo
                    vehiculos_inspeccion = vehiculos_clase
                    vehiculos_inspeccion = vehiculos_inspeccion.exclude(
                        fecha_ultima_inspeccion = None
                    ).annotate(
                        dias_sin_inspeccion = DiffDays(
                            CastDate(Now()) - CastDate(F('fecha_ultima_inspeccion')), 
                            output_field=IntegerField()
                            ), 
                    ).filter(
                        dias_sin_inspeccion__lte = periodo1_inspeccion
                    ).count()
                    
                    
                    inspecciones_a_tiempo = ( ( vehiculos_inspeccion * 100 ) / num_vehiculos_clase ) / 100
                    
                    #? Health
                    vehiculos_health = vehiculos_clase
                    vehiculos_health = vehiculos_health.filter(
                        observaciones_llanta__observacion = None
                    ).count()
                    
                    health = ( ( vehiculos_health * 100 ) / num_vehiculos_clase ) / 100
                    
                    #? Buena presion
                    vehiculos_buena_presion = vehiculos_clase
                    vehiculos_buena_presion = vehiculos_buena_presion.exclude(
                        observaciones_llanta__observacion__in=["Alta presion"]
                    ).exclude(
                        observaciones_llanta__observacion__in=["Baja presión"]
                    ).count()
                    
                    buena_presion = ( ( vehiculos_buena_presion * 100 ) / num_vehiculos_clase ) / 100
                    
                    print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
                    print(f'correctas_pulpo: {correctas_pulpo}')
                    print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
                    print(f'health: {health}')
                    print(f'buena_presion: {buena_presion}')
                    print(num_vehiculos_clase)
                    print('--------')
                    
                    datos_data.append( TendenciaAplicacion(
                        fecha = date.today(),
                        compania = compania,
                        ubicacion = ubicacion,
                        aplicacion = aplicacion,
                        correctas_pulpo = correctas_pulpo,
                        inspecciones_a_tiempo = inspecciones_a_tiempo,
                        health = health,
                        buena_presion = buena_presion
                    ) ) 
                
        objs = TendenciaAplicacion.objects.bulk_create(datos_data)
        
        dict_context = {
            'compania': 'compania',
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')



class DailyDataTendencias(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        datos_data = []
        
        companias = Compania.objects.all()
        for compania in companias:
            ubicaciones = Ubicacion.objects.filter(compania = compania)
            num_ubicaciones = ubicaciones.count()
            periodo1_inflado = compania.periodo1_inflado
            periodo2_inflado = compania.periodo2_inflado
            
            periodo1_inspeccion = compania.periodo1_inspeccion
            periodo2_inspeccion = compania.periodo2_inspeccion
            if num_ubicaciones == 0:
                continue
            print(compania)
            print(num_ubicaciones)
            for ubicacion in ubicaciones:
                aplicaciones = Aplicacion.objects.filter(ubicacion = ubicacion)
                num_aplicaciones = aplicaciones.count()
                if num_aplicaciones == 0:
                    continue
                print(ubicacion)
                for aplicacion in aplicaciones:
                    vehiculos = Vehiculo.objects.filter(compania = compania, ubicacion = ubicacion, aplicacion = aplicacion)
                    num_vehiculos = vehiculos.count()
                    if num_vehiculos == 0:
                        continue
                    clases = vehiculos.values('clase').distinct()
                    clases = functions.query_a_str(clases)
                    for clase in clases:
                        vehiculos_clase = vehiculos.filter(clase = clase)
                        num_vehiculos_clase = vehiculos_clase.count()
                        
                        #? Variables:
                        a_tiempo_pulpo:float
                        correctas_pulpo:float
                        inspecciones_a_tiempo:float
                        health:float
                        buena_presion:float
                        
                        #? a tiempo de pulpo
                        vehiculos_con_pulpo = vehiculos_clase
                        vehiculos_con_pulpo = vehiculos_con_pulpo.exclude(
                                fecha_de_inflado = None
                            ).annotate(
                                dias_sin_inflar=DiffDays(
                                    CastDate(Now())-CastDate(F('fecha_de_inflado')), 
                                    output_field=IntegerField()
                                    ),
                            ).filter(
                                dias_sin_inflar__lte = periodo1_inflado
                            ).count()
                        
                        a_tiempo_pulpo = ( ( vehiculos_con_pulpo * 100 ) / num_vehiculos_clase ) / 100
                        
                        #? Correctas pulpo
                        vehiculos_correctas_pulpo = vehiculos_clase
                        vehiculos_correctas_pulpo = vehiculos_correctas_pulpo.exclude(
                                observaciones_llanta__observacion__in=["Doble mala entrada"]
                            ).exclude(
                                observaciones_llanta__observacion__in=["Mala entrada"]
                            ).count()
                        
                        correctas_pulpo = ( ( vehiculos_correctas_pulpo * 100 ) / num_vehiculos_clase ) / 100
                        #correctas_pulpo = vehiculos_correctas_pulpo
                        
                        
                        #? Inspeccion a tiempo
                        vehiculos_inspeccion = vehiculos_clase
                        vehiculos_inspeccion = vehiculos_inspeccion.exclude(
                            fecha_ultima_inspeccion = None
                        ).annotate(
                            dias_sin_inspeccion = DiffDays(
                                CastDate(Now()) - CastDate(F('fecha_ultima_inspeccion')), 
                                output_field=IntegerField()
                                ), 
                        ).filter(
                            dias_sin_inspeccion__lte = periodo1_inspeccion
                        ).count()
                        
                        
                        inspecciones_a_tiempo = ( ( vehiculos_inspeccion * 100 ) / num_vehiculos_clase ) / 100
                        
                        #? Health
                        vehiculos_health = vehiculos_clase
                        vehiculos_health = vehiculos_health.filter(
                            observaciones_llanta__observacion = None
                        ).count()
                        
                        health = ( ( vehiculos_health * 100 ) / num_vehiculos_clase ) / 100
                        
                        #? Buena presion
                        vehiculos_buena_presion = vehiculos_clase
                        vehiculos_buena_presion = vehiculos_buena_presion.exclude(
                            observaciones_llanta__observacion__in=["Alta presion"]
                        ).exclude(
                            observaciones_llanta__observacion__in=["Baja presión"]
                        ).count()
                        
                        buena_presion = ( ( vehiculos_buena_presion * 100 ) / num_vehiculos_clase ) / 100
                        
                        print(clase)
                        print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
                        print(f'correctas_pulpo: {correctas_pulpo}')
                        print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
                        print(f'health: {health}')
                        print(f'buena_presion: {buena_presion}')
                        print(num_vehiculos_clase)
                        print('--------')
                        
                        datos_data.append( Tendencia(
                            fecha = date.today(),
                            compania = compania,
                            ubicacion = ubicacion,
                            aplicacion = aplicacion,
                            clase = clase,
                            correctas_pulpo = correctas_pulpo,
                            inspecciones_a_tiempo = inspecciones_a_tiempo,
                            health = health,
                            buena_presion = buena_presion
                        ) ) 
                
        objs = Tendencia.objects.bulk_create(datos_data)
        
        dict_context = {
            'compania': 'compania',
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    


class MonthDataRendimiento(View):
    def get(self, request , *args, **kwargs):
        datos_data = []
        
        #compania = Compania.objects.get(compania='PruebaBI')
        #vehiculos = Vehiculo.objects.filter(compania=compania)
        #llantas = Llanta.objects.filter(vehiculo__in = vehiculos).exclude(inventario='Nueva')
        companias = Compania.objects.all()
        
        for compania in companias:
            try:
                vehiculos = Vehiculo.objects.filter(compania=compania)
                llantas = Llanta.objects.filter(vehiculo__in = vehiculos).exclude(inventario='Nueva')
                
                km_actuales = llantas.exclude(km_actual = None).values_list("km_actual", flat=True)
                numero_elementos = km_actuales.count()
                km_actuales_list = list(km_actuales)
                pq_1 = functions.percentil(km_actuales_list, 1, numero_elementos)
                pq_3 = functions.percentil(km_actuales_list, 3, numero_elementos)
                print(pq_1)
                print(pq_3)
                km_filtrados = llantas.filter(km_actual__gte = pq_1, km_actual__lte = pq_3).exclude(km_actual = None)
                km_filtrados_list = list(km_filtrados.values_list("km_actual", flat=True))
                km_filtrados_list.sort()
                print(km_filtrados_list)
                mediana = numpy.median(km_filtrados_list, axis = None)
                print(mediana)
                std = numpy.std(km_filtrados_list, axis=None, dtype=numpy.float64)
                print(std)
                
                limite_inferior = mediana - (2*std)
                limite_superior = mediana + (2*std)
                
                print(limite_inferior)
                print(limite_superior)
                
                datos = []
                
                for llanta in llantas:
                    mm_desgastados = functions.mm_desgastasdos(llanta)
                    porcentaje_de_desgaste = functions.porcentaje_de_desgaste(llanta)
                    km_x_mm = functions.km_x_mm(llanta)
                    km_proyectado = functions.km_proyectado(llanta)
                    cpk_proyectado = functions.cpk_proyectado(llanta)
                    cpk_real = functions.cpk_real(llanta)


                    try:
                        prof_inical = llanta.producto.profundidad_inicial
                    except:
                        prof_inical = None
                    try:    
                        if(
                            porcentaje_de_desgaste > .15
                            and
                            llanta.km_actual > limite_inferior
                            and
                            llanta.km_actual < limite_superior

                            ):
                            is_analizada = True
                        else:
                            is_analizada = False

                    except:
                        is_analizada = False
                        
                    punto_retiro = func.punto_de_retiro(llanta)
                    minima = func.min_profundidad(llanta)
                    
                    mes = date.today().month

                    datos.append({
                                    'llanta': llanta,
                                    'mm_desgastados': mm_desgastados, 
                                    'porcentaje_de_desgaste': porcentaje_de_desgaste,
                                    'profundidad_inicial': prof_inical,
                                    'punto_retiro': punto_retiro,
                                    'minima': minima,
                                    'km_x_mm': km_x_mm,
                                    'km_proyectado': km_proyectado,
                                    'cpk_proyectado': cpk_proyectado,
                                    'cpk_real': cpk_real,
                                    'is_analizada': is_analizada
                                    })
                    datos_data.append(
                        Rendimiento(
                            mes = mes,
                            llanta = llanta,
                            mm_desgastados = mm_desgastados,
                            porcentaje_de_desgaste = porcentaje_de_desgaste,
                            km_x_mm = km_x_mm,
                            km_proyectado = km_proyectado,
                            is_analizada = is_analizada,
                            cpk_proyectado = cpk_proyectado,
                            cpk_real = cpk_real,
                        ))
            except:
                pass
        objs = Rendimiento.objects.bulk_create(datos_data)
        
        dict_context = {
            'compania': 'compania',
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
    
    

def guardar_estado_actual_llantas(request):
    
    
    compania = Compania.objects.get(compania='PruebaBI')
    vehiculos = Vehiculo.objects.filter(compania=compania)
    llantas = Llanta.objects.filter(vehiculo__in = vehiculos).exclude(inventario='Nueva')
    
    vehiculos1 = vehiculos
    vehiculos2 = vehiculos.values()
    
    vehiculos1 = vehiculos1.annotate(
        hola = Value('hola')
    ).values()
    
    print(vehiculos1.first())
    print(vehiculos2.first())
    return render(request, 'utilidades/datos.html',{
        
    } )
    
    

class CorregirPrimeraInspeccion(View):
    def get(self, request , *args, **kwargs):
        datos_data = []
        
        llantas = Llanta.objects.exclude(ultima_inspeccion = None)
        num = 0
        for llanta in llantas:
            inspecciones = Inspeccion.objects.filter(llanta_id = llanta.id, vida = llanta.vida).order_by('id')
            primera = inspecciones.first()
            llanta.primera_inspeccion = primera
            llanta.save()
        print(num)
        llantas = list(llantas.values('pk'))
        dict_context = {
            'compania': llantas,
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')