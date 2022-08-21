# Django
from django.urls import path
from django.views.generic.base import View
from utilidades import views

# Views

urlpatterns = [
    
    #-----------------------A-----------------------
    
    path(
        route="utilidades/AgregarProductoAcciones",
        view=views.AgregarProductoAcciones.as_view(),
        name="AgregarProductoAcciones"
    ),    
    
    #-----------------------B-----------------------
    
    path(
        route="utilidades/BorrarRendimientos",
        view=views.BorrarRendimientos,
        name="BorrarRendimientos"
    ),    
    
    #-----------------------C-----------------------
    path(
        route="utilidades/corregirInspeccionesVehiculo",
        view=views.corregirInspeccionesVehiculo,
        name="corregirInspeccionesVehiculo"
    ),
    
    path(
        route="utilidades/CorregirPrimeraInspeccion",
        view=views.CorregirPrimeraInspeccion.as_view(),
        name="CorregirPrimeraInspeccion"
    ),
    
    #-----------------------D-----------------------
    
    path(
        route="utilidades/DailyDataTendencias",
        view=views.DailyDataTendencias.as_view(),
        name="DailyDataTendencias"
    ),
    path(
        route="utilidades/DailyDataTendenciasAplicaciones",
        view=views.DailyDataTendenciasAplicaciones.as_view(),
        name="DailyDataTendenciasAplicaciones"
    ),
    
    path(
        route="utilidades/DailyDataTendenciasUbicaciones",
        view=views.DailyDataTendenciasUbicaciones.as_view(),
        name="DailyDataTendenciasUbicaciones"
    ),
    
    
    path(
        route="utilidades/DailyDataTendenciasCompanias",
        view=views.DailyDataTendenciasCompanias.as_view(),
        name="DailyDataTendenciasCompanias"
    ),
    

    #-----------------------E-----------------------
    
    #-----------------------F-----------------------
    
    #-----------------------G-----------------------
    
    path(
        route="utilidades/guardar_estado_actual_llantas",
        view=views.guardar_estado_actual_llantas,
        name="guardar_estado_actual_llantas"
    ),    
    
    #-----------------------H-----------------------

    #-----------------------I-----------------------
    
    #-----------------------J-----------------------
    
    #-----------------------K-----------------------
    
    #-----------------------L-----------------------
    
    #-----------------------M-----------------------
    
    path(
        route="utilidades/MonthDataRendimiento",
        view=views.MonthDataRendimiento.as_view(),
        name="MonthDataRendimiento"
    ),
    
    #-----------------------N-----------------------
     
    #-----------------------Ñ-----------------------
    
    #-----------------------O-----------------------

    #-----------------------P-----------------------

    #-----------------------Q-----------------------

    #-----------------------R-----------------------

    #-----------------------S-----------------------

    path(
        route="utilidades/subirBigData",
        view=views.subirBigData,
        name="subirBigData"
    ),

    #-----------------------T-----------------------

    #-----------------------U-----------------------
    
    path(
        route="utilidades/home",
        view=views.UtilidadesView.as_view(),
        name="utilidades"
    ),

    #-----------------------V-----------------------

    #-----------------------W-----------------------

    #-----------------------X-----------------------

    #-----------------------Y-----------------------

    #-----------------------Z-----------------------
    
]