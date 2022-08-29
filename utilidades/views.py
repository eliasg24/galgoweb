from datetime import date
from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView, TemplateView, DetailView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
import numpy

from dashboards.models import Aplicacion, Bitacora, Bitacora_Pro, Compania, Inspeccion, InspeccionVehiculo, Llanta, Observacion, Rendimiento, ServicioLlanta, Tendencia, TendenciaAplicacion, TendenciaCompania, TendenciaUbicacion, Ubicacion, Vehiculo

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
            
            """
            print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
            print(f'correctas_pulpo: {correctas_pulpo}')
            print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
            print(f'health: {health}')
            print(f'buena_presion: {buena_presion}')
            print(num_vehiculos_clase)
            print('--------')
            """
            
            datos_data.append( TendenciaCompania(
                fecha = date.today(),
                compania = compania,
                correctas_pulpo = correctas_pulpo,
                inspecciones_a_tiempo = inspecciones_a_tiempo,
                pulpos_a_tiempo = a_tiempo_pulpo,
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
                
                """
                print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
                print(f'correctas_pulpo: {correctas_pulpo}')
                print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
                print(f'health: {health}')
                print(f'buena_presion: {buena_presion}')
                print(num_vehiculos_clase)
                print('--------')
                """
                
                datos_data.append( TendenciaUbicacion(
                    fecha = date.today(),
                    compania = compania,
                    ubicacion = ubicacion,
                    correctas_pulpo = correctas_pulpo,
                    inspecciones_a_tiempo = inspecciones_a_tiempo,
                    pulpos_a_tiempo = a_tiempo_pulpo,
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
                    
                    """
                    print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
                    print(f'correctas_pulpo: {correctas_pulpo}')
                    print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
                    print(f'health: {health}')
                    print(f'buena_presion: {buena_presion}')
                    print(num_vehiculos_clase)
                    print('--------')
                    """
                    
                    datos_data.append( TendenciaAplicacion(
                        fecha = date.today(),
                        compania = compania,
                        ubicacion = ubicacion,
                        aplicacion = aplicacion,
                        correctas_pulpo = correctas_pulpo,
                        inspecciones_a_tiempo = inspecciones_a_tiempo,
                        pulpos_a_tiempo = a_tiempo_pulpo,
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
                        
                        """
                        print(clase)
                        print(f'a_tiempo_pulpo: {a_tiempo_pulpo}')
                        print(f'correctas_pulpo: {correctas_pulpo}')
                        print(f'inspeccion_a_timepo: {inspecciones_a_tiempo}')
                        print(f'health: {health}')
                        print(f'buena_presion: {buena_presion}')
                        print(num_vehiculos_clase)
                        print('--------')
                        """
                        
                        datos_data.append( Tendencia(
                            fecha = date.today(),
                            compania = compania,
                            ubicacion = ubicacion,
                            aplicacion = aplicacion,
                            clase = clase,
                            correctas_pulpo = correctas_pulpo,
                            inspecciones_a_tiempo = inspecciones_a_tiempo,
                            pulpos_a_tiempo = a_tiempo_pulpo,
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
                    year = date.today().year

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
                            year = year,
                            mes = mes,
                            llanta = llanta,
                            mm_desgastados = mm_desgastados,
                            porcentaje_de_desgaste = porcentaje_de_desgaste,
                            km_x_mm = km_x_mm,
                            km_proyectado = km_proyectado,
                            is_analizada = is_analizada,
                            cpk_proyectado = cpk_proyectado,
                            cpk_real = cpk_real,
                            km = llanta.km_actual,
                            producto = llanta.producto,
                            vida = llanta.vida,
                            posicion = llanta.posicion,
                            tipo_de_eje = llanta.tipo_de_eje
                            
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
    
    
class AgregarProductoAcciones(View):
    def get(self, request , *args, **kwargs):
        
        servicios = ServicioLlanta.objects.all()
        for servicio in servicios:
            servicio.tipo_de_eje = servicio.llanta.tipo_de_eje
            servicio.eje = servicio.llanta.eje
            servicio.producto = servicio.llanta.producto
            servicio.nombre_de_eje = servicio.llanta.nombre_de_eje
            servicio.save()
            
        
        dict_context = {
            'compania': 'servicios',
        }
        
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ArreglarBitacoras(View):
    def get(self, request , *args, **kwargs):
        vehiculos_sin_configuracion = []
        vehiculos = Vehiculo.objects.filter().exclude(fecha_de_inflado = None)
        print(vehiculos)
        for vehiculo in vehiculos:
            bitacoras = Bitacora.objects.filter(vehiculo = vehiculo).order_by('id')
            bitacoras_pro = Bitacora_Pro.objects.filter(vehiculo = vehiculo).order_by('id')
            print(bitacoras)
            print(bitacoras_pro)
            if bitacoras.count() == 0 and bitacoras_pro.count() == 0:
                continue
            
            presiones_establecidas = [
                vehiculo.presion_establecida_1,
                vehiculo.presion_establecida_2,
                vehiculo.presion_establecida_3,
                vehiculo.presion_establecida_4,
                vehiculo.presion_establecida_5,
                vehiculo.presion_establecida_6,
                vehiculo.presion_establecida_7,
            ]
                        
            stado1 = 'Buena'
            for bitacora in bitacoras_pro:
                stados_ = []
                stado_act = 'Buena'
                a = 0
                b = 0
                llantas = [
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
                
                objetivo = vehiculo.compania.objetivo / 100
                
                if vehiculo.configuracion == None:
                    if vehiculo not in vehiculos_sin_configuracion:
                        vehiculos_sin_configuracion.append(vehiculo)
                    continue
                configuracion = (bitacora.vehiculo.configuracion).split('.')
                loop = 0              
                for eje in configuracion:
                    if eje == 'SP1':
                        continue
                    else:
                        numero_llantas = int(eje[1])
                        if loop == 0:
                            b += numero_llantas
                        else:
                            a = b
                            b += numero_llantas
                        print(a, b)
                        l = llantas[a:b]
                        for elemento in l:
                            presion_est = presiones_establecidas[loop]
                            min_ = presion_est - (presion_est * objetivo)
                            max_ = presion_est + (presion_est * objetivo)
                            #print('min: ', min_, '|', 'max: ', max_)
                            #print(elemento, 'elemento')
                            #print( )
                            
                            
                            if elemento < min_ or elemento > max_:
                                stado_act = 'Mala'
                              
                            #print(stado1, 'pro')
                            stados_.append(stado1)
                    
                            
                                
                    loop += 1       
                    
                print(stado_act)
                if stado_act == 'Mala' and stado1 == 'Doble':
                    stado1 = 'Doble'
                elif stado_act == 'Mala' and stado1 == 'Mala':
                    stado1 = 'Doble'
                elif stado_act == 'Mala' and stado1 == 'Buena':
                    stado1 = 'Mala'
                else:
                    stado1 = 'Buena'
                    
                    
                    
                bitacora.estado = stado1
                bitacora.save()
                print('--')
                print()
            print()       
        print(vehiculos_sin_configuracion)      
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')
    
    
class VaciarBitacoras(View):
    def get(self, request , *args, **kwargs):
        vehiculos_sin_configuracion = []
        vehiculos = Vehiculo.objects.exclude(fecha_de_inflado = None)
        for vehiculo in vehiculos:
            bitacoras = Bitacora.objects.filter(vehiculo = vehiculo).order_by('id')
            bitacoras_pro = Bitacora_Pro.objects.filter(vehiculo = vehiculo).order_by('id')
            if bitacoras.count() == 0 and bitacoras_pro.count() == 0:
                continue
            
            
            
            for bitacora in bitacoras:
                stado1 = 'Buena'
                bitacora.estado = stado1
                bitacora.save()

            
            for bitacora in bitacoras_pro:
                stado1 = 'Buena'
                bitacora.estado = stado1
                bitacora.save()   
         
        print(vehiculos_sin_configuracion)      
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')
class Arreglar_Obs(View):
    def get(self, request , *args, **kwargs):
        vehiculos_sin_configuracion = []
        vehiculos = Vehiculo.objects.exclude(ultima_bitacora_pro = None)
        
        mala_entrada = Observacion.objects.get(observacion = 'Mala entrada')
        doble_mala_entrada = Observacion.objects.get(observacion = 'Doble mala entrada')
        for vehiculo in vehiculos:
            vehiculo.observaciones_llanta.remove(mala_entrada, doble_mala_entrada)
                        
            if vehiculo.ultima_bitacora_pro.estado == 'Mala':
                vehiculo.observaciones_llanta.add(mala_entrada)
                
            elif vehiculo.ultima_bitacora_pro.estado == 'Doble':
                vehiculo.observaciones_llanta.add(doble_mala_entrada)
            else:
                pass

                
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')
    
    
class AgregarPosiciones(View):
    def get(self, request , *args, **kwargs):
        
        bitacoras = Bitacora_Pro.objects.all()
        for bitacora in bitacoras:
            ubicacion = bitacora.vehiculo.ubicacion
            aplicacion = bitacora.vehiculo.aplicacion
            bitacora.ubicacion = ubicacion
            bitacora.aplicacion = aplicacion
            
            if bitacora.llanta_1 != None:
                bitacora.posicion_1 = bitacora.llanta_1.posicion
            if bitacora.llanta_2 != None:
                bitacora.posicion_2 = bitacora.llanta_2.posicion
            if bitacora.llanta_3 != None:
                bitacora.posicion_3 = bitacora.llanta_3.posicion
            if bitacora.llanta_4 != None:
                bitacora.posicion_4 = bitacora.llanta_4.posicion
            if bitacora.llanta_5 != None:
                bitacora.posicion_5 = bitacora.llanta_5.posicion
            if bitacora.llanta_6 != None:
                bitacora.posicion_6 = bitacora.llanta_6.posicion
            if bitacora.llanta_7 != None:
                bitacora.posicion_7 = bitacora.llanta_7.posicion
            if bitacora.llanta_8 != None:
                bitacora.posicion_8 = bitacora.llanta_8.posicion
            if bitacora.llanta_9 != None:
                bitacora.posicion_9 = bitacora.llanta_9.posicion
            if bitacora.llanta_10 != None:
                bitacora.posicion_10= bitacora.llanta_10.posicion
            if bitacora.llanta_11 != None:
                bitacora.posicion_11= bitacora.llanta_11.posicion
            if bitacora.llanta_12 != None:
                bitacora.posicion_12= bitacora.llanta_12.posicion
            bitacora.save()

            
            
                
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')
    
    
class AgregarLlantas_bitacoras(View):
    def get(self, request , *args, **kwargs):
        
        bitacoras = Bitacora_Pro.objects.all()
        for bitacora in bitacoras:
            vehiculo = bitacora.vehiculo
            bitacora.llantas.clear()
            print(vehiculo)
            llantas = Llanta.objects.filter(vehiculo=vehiculo, inventario='Rodante')
            print(llantas)
            num_ejes = vehiculo.configuracion.split('.')
            ejes_no_ordenados = []
            ejes = []
            eje = 1
            for num in num_ejes:
                if num != "SP1":
                    list_temp = []
                    for llanta in llantas:
                        if llanta.eje == eje:
                            list_temp.append([llanta])
                    eje += 1
                    ejes_no_ordenados.append(list_temp)
            
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
                
                elif len(eje) == 4:
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
                else:
                    pass
            print(ejes)
            numero = 1
            for eje in ejes:
                    for ej in eje:
                        for llant in ej:
                            llanta = llant
                            print(llanta)
                            if numero == 1:
                                bitacora.llanta_1 = llanta
                                bitacora.presion_establecida_1 = func.presion_establecida(llanta)
                            elif numero == 2:
                                bitacora.llanta_2 = llanta
                                bitacora.presion_establecida_2 = func.presion_establecida(llanta)
                            elif numero == 3:
                                bitacora.llanta_3 = llanta
                                bitacora.presion_establecida_3 = func.presion_establecida(llanta)
                            elif numero == 4:
                                bitacora.llanta_4 = llanta
                                bitacora.presion_establecida_4 = func.presion_establecida(llanta)
                            elif numero == 5:
                                bitacora.llanta_5 = llanta
                                bitacora.presion_establecida_5 = func.presion_establecida(llanta)
                            elif numero == 6:
                                bitacora.llanta_6 = llanta
                                bitacora.presion_establecida_6 = func.presion_establecida(llanta)
                            elif numero == 7:
                                bitacora.llanta_7 = llanta
                                bitacora.presion_establecida_7 = func.presion_establecida(llanta)
                            elif numero == 8:
                                bitacora.llanta_8 = llanta
                                bitacora.presion_establecida_8 = func.presion_establecida(llanta)
                            elif numero == 9:
                                bitacora.llanta_9 = llanta
                                bitacora.presion_establecida_9 = func.presion_establecida(llanta)
                            elif numero == 10:
                                bitacora.llanta_10 = llanta
                                bitacora.presion_establecida_10 = func.presion_establecida(llanta)
                            elif numero == 11:
                                bitacora.llanta_11 = llanta
                                bitacora.presion_establecida_11 = func.presion_establecida(llanta)
                            elif numero == 12:
                                bitacora.llanta_12 = llanta
                                bitacora.presion_establecida_12 = func.presion_establecida(llanta)
                                
                            bitacora.llantas.add(llanta)
                            bitacora.save()
                            numero += 1

            
            
                
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')
    
    
class ArreglarLlantasBitacoras(View):
    def get(self, request , *args, **kwargs):
        vehiculos_sin_configuracion = []
        vehiculos = Vehiculo.objects.exclude(ultima_bitacora_pro = None)
        
        for vehiculo in vehiculos:
            bitacoras_pro = Bitacora_Pro.objects.filter(vehiculo = vehiculo).order_by('id')
            llantas = {}
            objetivo = vehiculo.compania.objetivo / 100
            for bitacora in bitacoras_pro:
                llantas_=[
                    bitacora.llanta_1,
                    bitacora.llanta_2,
                    bitacora.llanta_3,
                    bitacora.llanta_4,
                    bitacora.llanta_5,
                    bitacora.llanta_6,
                    bitacora.llanta_7,
                    bitacora.llanta_8,
                    bitacora.llanta_9,
                    bitacora.llanta_10,
                    bitacora.llanta_11,
                    bitacora.llanta_12,
                ]
                for llanta in llantas_:
                    if llanta != None:
                        llantas[llanta.id] = 'Buena' 
            for bitacora in bitacoras_pro:
                print(bitacora.id)
                loop = 0
                llantas_=[
                    bitacora.llanta_1,
                    bitacora.llanta_2,
                    bitacora.llanta_3,
                    bitacora.llanta_4,
                    bitacora.llanta_5,
                    bitacora.llanta_6,
                    bitacora.llanta_7,
                    bitacora.llanta_8,
                    bitacora.llanta_9,
                    bitacora.llanta_10,
                    bitacora.llanta_11,
                    bitacora.llanta_12,
                ]
                p_establecidas=[
                    bitacora.presion_establecida_1,
                    bitacora.presion_establecida_2,
                    bitacora.presion_establecida_3,
                    bitacora.presion_establecida_4,
                    bitacora.presion_establecida_5,
                    bitacora.presion_establecida_6,
                    bitacora.presion_establecida_7,
                    bitacora.presion_establecida_8,
                    bitacora.presion_establecida_9,
                    bitacora.presion_establecida_10,
                    bitacora.presion_establecida_11,
                    bitacora.presion_establecida_12,
                ]
                p_entrada=[
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
                estado_llantas=[
                    bitacora.estado_llanta_1,
                    bitacora.estado_llanta_2,
                    bitacora.estado_llanta_3,
                    bitacora.estado_llanta_4,
                    bitacora.estado_llanta_5,
                    bitacora.estado_llanta_6,
                    bitacora.estado_llanta_7,
                    bitacora.estado_llanta_8,
                    bitacora.estado_llanta_9,
                    bitacora.estado_llanta_10,
                    bitacora.estado_llanta_11,
                    bitacora.estado_llanta_12,
                ]
                num = 0
                for llanta in llantas_:
                    if llanta != None:
                        min_ = p_establecidas[num] - (p_establecidas[num] * objetivo)
                        max_ = p_establecidas[num] + (p_establecidas[num] * objetivo)
                        print(llanta, min_, max_, p_entrada[num])
                        if llanta.id in llantas:
                            print(True)
                        if p_entrada[num] < min_ or p_entrada[num] > max_:
                            if llantas[llanta.id] == 'Doble' or llantas[llanta.id] == 'Mala':
                                llantas[llanta.id] = 'Doble'
                                if (num + 1) == 1:
                                    bitacora.estado_llanta_1 = 'Doble'
                                elif (num + 1) == 2:
                                    bitacora.estado_llanta_2 = 'Doble'
                                elif (num + 1) == 3:
                                    bitacora.estado_llanta_3 = 'Doble'
                                elif (num + 1) == 4:
                                    bitacora.estado_llanta_4 = 'Doble'
                                elif (num + 1) == 5:
                                    bitacora.estado_llanta_5 = 'Doble'
                                elif (num + 1) == 6:
                                    bitacora.estado_llanta_6 = 'Doble'
                                elif (num + 1) == 7:
                                    bitacora.estado_llanta_7 = 'Doble'
                                elif (num + 1) == 8:
                                    bitacora.estado_llanta_8 = 'Doble'
                                elif (num + 1) == 9:
                                    bitacora.estado_llanta_9 = 'Doble'
                                elif (num + 1) == 10:
                                    bitacora.estado_llanta_10 = 'Doble'
                                elif (num + 1) == 11:
                                    bitacora.estado_llanta_11 = 'Doble'
                                elif (num + 1) == 12:
                                    bitacora.estado_llanta_12 = 'Doble'
                                print('Doble')
                            else:
                                llantas[llanta.id] = 'Mala'
                                if (num + 1) == 1:
                                    bitacora.estado_llanta_1 = 'Mala'
                                elif (num + 1) == 2:
                                    bitacora.estado_llanta_2 = 'Mala'
                                elif (num + 1) == 3:
                                    bitacora.estado_llanta_3 = 'Mala'
                                elif (num + 1) == 4:
                                    bitacora.estado_llanta_4 = 'Mala'
                                elif (num + 1) == 5:
                                    bitacora.estado_llanta_5 = 'Mala'
                                elif (num + 1) == 6:
                                    bitacora.estado_llanta_6 = 'Mala'
                                elif (num + 1) == 7:
                                    bitacora.estado_llanta_7 = 'Mala'
                                elif (num + 1) == 8:
                                    bitacora.estado_llanta_8 = 'Mala'
                                elif (num + 1) == 9:
                                    bitacora.estado_llanta_9 = 'Mala'
                                elif (num + 1) == 10:
                                    bitacora.estado_llanta_10 = 'Mala'
                                elif (num + 1) == 11:
                                    bitacora.estado_llanta_11 = 'Mala'
                                elif (num + 1) == 12:
                                    bitacora.estado_llanta_12 = 'Mala'
                                print('Mala')
                                
                        else:
                            llantas[llanta.id] = 'Buena'
                            if (num + 1) == 1:
                                bitacora.estado_llanta_1 = 'Buena'
                            elif (num + 1) == 2:
                                bitacora.estado_llanta_2 = 'Buena'
                            elif (num + 1) == 3:
                                bitacora.estado_llanta_3 = 'Buena'
                            elif (num + 1) == 4:
                                bitacora.estado_llanta_4 = 'Buena'
                            elif (num + 1) == 5:
                                bitacora.estado_llanta_5 = 'Buena'
                            elif (num + 1) == 6:
                                bitacora.estado_llanta_6 = 'Buena'
                            elif (num + 1) == 7:
                                bitacora.estado_llanta_7 = 'Buena'
                            elif (num + 1) == 8:
                                bitacora.estado_llanta_8 = 'Buena'
                            elif (num + 1) == 9:
                                bitacora.estado_llanta_9 = 'Buena'
                            elif (num + 1) == 10:
                                bitacora.estado_llanta_10 = 'Buena'
                            elif (num + 1) == 11:
                                bitacora.estado_llanta_11 = 'Buena'
                            elif (num + 1) == 12:
                                bitacora.estado_llanta_12 = 'Buena'
                            print('Buena')
                            
                        num += 1

                bitacora.save()
                print(llantas)
                
                print()
                print()
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')
    
class CorregirRendimientos(View):
    def get(self, request , *args, **kwargs):
        rendimientos = Rendimiento.objects.all()
        for rendimiento in rendimientos:
            rendimiento.km = rendimiento.llanta.km_actual
            rendimiento.producto = rendimiento.llanta.producto
            rendimiento.vida = rendimiento.llanta.vida
            rendimiento.posicion = rendimiento.llanta.posicion
            rendimiento.tipo_de_eje = rendimiento.llanta.tipo_de_eje
            rendimiento.save()
        dict_context = {
                'compania': 'servicios',
            }
            
        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)
        
        return HttpResponse(json_context, content_type='application/json')