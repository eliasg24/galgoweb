# Django
from django.urls import path, include
from aetoappapi import views
from django.contrib import admin
from rest_framework.authtoken import views as rest



# Views

urlpatterns = [
    
    #-----------------------A-----------------------
    path(
        route="api/user/",
        view=views.UserList.as_view(),
        name="userList"
    ),   
    
    #-----------------------B-----------------------
       
    #-----------------------C-----------------------
    
    path(
       route="app/companiasperfildata/",
       view=views.CompaniasPerfilData.as_view(),
       name="companiasperfildata"
    ),   

    #-----------------------D-----------------------

    #-----------------------E-----------------------
    
    #-----------------------F-----------------------
    
    #-----------------------G-----------------------
    path(
       route="app/generate_token/",
       view=rest.obtain_auth_token,
       name="generate_token"
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
       route="app/userdata/",
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


#path(
#   route="utilidades/DailyDataTendencias",
#   view=views.DailyDataTendencias.as_view(),
#   name="DailyDataTendencias"
#    ),   