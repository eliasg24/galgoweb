# Django
from django.urls import path
from django.views.generic.base import View
from galgoapi import views

# Views

urlpatterns = [
    
    #-----------------------A-----------------------
    
    #-----------------------B-----------------------
     
    #-----------------------C-----------------------
    
    #-----------------------D-----------------------
    
    #-----------------------E-----------------------
    
    #-----------------------F-----------------------
    
    #-----------------------G-----------------------
    
    path(
        route="api/GalgoSucursales/",
        view=views.GalgoSucursales.as_view(),
        name="GalgoSucursales"
    ),
    
    path(
        route="api/GalgoAplicaciones/",
        view=views.GalgoAplicaciones.as_view(),
        name="GalgoAplicaciones"
    )
        
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
    
    #-----------------------V-----------------------

    #-----------------------W-----------------------

    #-----------------------X-----------------------

    #-----------------------Y-----------------------

    #-----------------------Z-----------------------
    
]