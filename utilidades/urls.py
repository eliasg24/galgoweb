# Django
from django.urls import path
from django.views.generic.base import View
from utilidades import views

# Views

urlpatterns = [
    
    #-----------------------A-----------------------
    
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
    #-----------------------D-----------------------
    
    path(
        route="utilidades/DailyDataTendencias",
        view=views.DailyDataTendencias.as_view(),
        name="DailyDataTendencias"
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
    
    #-----------------------N-----------------------
     
    #-----------------------Ñ-----------------------
    
    #-----------------------O-----------------------

    #-----------------------P-----------------------

    #-----------------------Q-----------------------

    #-----------------------R-----------------------

    #-----------------------S-----------------------

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