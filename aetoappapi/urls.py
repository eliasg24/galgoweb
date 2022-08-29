# Django
from rest_framework.authtoken import views as rest
from django.urls import path, include
from django.contrib import admin
from aetoappapi import views




# Views

urlpatterns = [
    
    #-----------------------A-----------------------
    path(
        route="app/aplicacion/",
        view=views.AplicacionPerfilData.as_view(),
        name="apiAplicacion"
    ),   
    
    
    #-----------------------B-----------------------
       
    #-----------------------C-----------------------
      path(
        route="app/ContextoPerfil/",
        view=views.ContextoPerfil.as_view(),
        name="app/ContextoPerfil/"
    ),   

    #-----------------------D-----------------------

    #-----------------------E-----------------------
    
    #-----------------------F-----------------------
    
    #-----------------------G-----------------------
   path(
        route="app/InspeccionVehiculo/",
        view=views.InspeccionVehiculo.as_view(),
        name="app/InspeccionVehiculo/"
    ),     
    
    #-----------------------H-----------------------

    #-----------------------I-----------------------
    
    path(
       route="app/login/",
       view=rest.obtain_auth_token,
       name="login"
        ),   
    #-----------------------J-----------------------
    
    #-----------------------K-----------------------
    
    #-----------------------L-----------------------

    #-----------------------M-----------------------
    
    #-----------------------N-----------------------
     
    #-----------------------Ñ-----------------------
    
    #-----------------------O-----------------------
     path(
       route="app/ordenaminto_vehiculo/",
       view=views.Ordenamientovehiculollantas.as_view(),
       name="ordenaminto_vehiculo" 
    ),  
      path(
       route="app/ordenamintoLlantas/",
       view=views.Ordenamientollantas.as_view(),
       name="ordenamintoLlantas"
       
    ),  

    #-----------------------P-----------------------

    #-----------------------Q-----------------------

    #-----------------------R-----------------------

    #-----------------------S-----------------------

    #-----------------------T-----------------------
    path(
       route="app/talleres/",
       view=views.TalleresPerfilData.as_view(),
       name="talleresData"
    ),   

    #-----------------------U-----------------------

    
    path(
       route="app/user_compania_data/",
       view=views.UserData.as_view(),
       name="userdata"
    ),   
    
    path(
       route="app/ubicacionesdata/",
       view=views.UbicacionData.as_view(),
       name="ubicacionesdata"
       
    ),  
    #-----------------------V-----------------------

    #-----------------------W-----------------------

    #-----------------------X-----------------------

    #-----------------------Y-----------------------

    #-----------------------Z-----------------------
    
]


