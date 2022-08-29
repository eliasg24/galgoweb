from sklearn import inspection
from aetoappapi.serializers import AplicacionDataSerializer, CompaniasPerfilSerializer, ContextPerfilSerializer, InspeccionVehiculoSerializers, InspeccionesSerializers, OrdenamientoPorllantaSerializer,  OrdenamientoPorvehiculoSerializer, TalleresDataSerializer, UbicacionDataSerializer, UserDataSerializer, UserSerializer, llantaSerializer
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from galgoapi.functions import functions as galgofunc
from django.utils.decorators import method_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.urls import reverse_lazy
from rest_framework import generics
from rest_framework import status
from rest_framework import mixins
from dashboards import models
from urllib import response
from yaml import serialize

#? view para la imformacion del user
class UserData(generics.GenericAPIView):
    #queryset = User.objects.all()
    serializer_class = UserDataSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):   
        user = request.user
        print(user)
        perfil = models.Perfil.objects.get(user=user)
        #self.queryset = perfil
        serializer = self.get_serializer(perfil)
        return Response(serializer.data) 
    
#? view para la informacion de 
class CompaniasPerfilData(generics.ListCreateAPIView):
    #queryset = User.objects.all()
    serializer_class = CompaniasPerfilSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):   
        user = request.user
        print(user)
        perfil = models.Perfil.objects.filter(user=user)
        self.queryset = perfil
        return self.list(request, *args, **kwargs)

#? view para la informacion de las ubicaciones de  user
class UbicacionData(generics.ListCreateAPIView):
    #queryset = User.objects.all()
    serializer_class = UbicacionDataSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):   
        user = request.user
        perfil = models.Perfil.objects.get(user=user)
        try:
            id = int(request.GET.get('id', None))
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        ubicaciones_perfil = perfil.ubicaciones.all()
        print(ubicaciones_perfil)     
        app = models.Ubicacion.objects.filter(
            compania_id = id, id__in = ubicaciones_perfil
            )
        self.queryset = app
        return self.list(request, *args, **kwargs)
    
#? view para la informacion de las aplicacion
class AplicacionPerfilData(generics.ListCreateAPIView):
    #queryset = User.objects.all()
    serializer_class = AplicacionDataSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication] 
    def get(self, request, *args, **kwargs):   
        user = request.user
        perfil = models.Perfil.objects.get(user=user)     
        try:
            id = request.GET.get('id', None)
            id = galgofunc.str_to_list_int(id)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)        
        aplicacion = models.Aplicacion.objects.filter(ubicacion__id__in=id)
        aplicaciones_perfil = perfil.aplicaciones.all()      
        aplicacion = models.Aplicacion.objects.filter(
            ubicacion__id__in=id, id__in=aplicaciones_perfil
            ).order_by('ubicacion__id')        
        self.queryset = aplicacion
        return self.list(request, *args, **kwargs)
    
#? view para la informacion de las talleres
class TalleresPerfilData(generics.ListCreateAPIView):
    #queryset = User.objects.all()
    serializer_class = TalleresDataSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):   
        user = request.user
        perfil = models.Perfil.objects.get(user=user)
        try:
            id = request.GET.get('id', None)
            id = galgofunc.str_to_list_int(id)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        talleres = models.Taller.objects.filter(compania__id__in=id)
        teller_perfil = perfil.talleres.all()
        talleres = models.Taller.objects.filter(
            compania__id__in=id, id__in=teller_perfil
            ).order_by('compania__id')
        print(talleres)
        self.queryset = talleres 
        return self.list(request, *args, **kwargs)
    
#? Metodo para modificar el contyexto de perfil
class ContextoPerfil(mixins.UpdateModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication] 
    def put(self, request, *args, **kwargs):
        user = request.user
        perfil = models.Perfil.objects.get(user=user)
        #?Obtener parametros
        compania = request.data['compania']
        ubicaciones = request.data['ubicaciones']
        aplicaciones = request.data['aplicaciones']
        talleres = request.data['talleres']
        #?CONVERSION 
        try:
            compania = int(compania)
            ubicaciones = galgofunc.str_to_list_int(ubicaciones)
            aplicaciones = galgofunc.str_to_list_int(aplicaciones)
            talleres = galgofunc.str_to_list_int(talleres)      
        except:  
            return Response(status = status.HTTP_400_BAD_REQUEST)
        #?Consultas 
        compania = models.Compania.objects.get(id = compania)
        ubicaciones = models.Ubicacion.objects.filter(id__in = ubicaciones)
        aplicaciones = models.Aplicacion.objects.filter(id__in = aplicaciones)
        talleres = models.Taller.objects.filter(id__in = talleres)
        #? Limpiar datos
        perfil.ubicacion.clear()
        perfil.aplicacion.clear()
        perfil.taller.clear()
        #? guardar los datos

        perfil.compania = compania
        for ubicacion in ubicaciones:
            perfil.ubicacion.add(ubicacion)
        for aplicacion in aplicaciones:
            perfil.aplicacion.add(aplicacion)
        for  taller in  talleres:
            perfil.taller.add(taller)
        perfil.save()
        return Response({
            'companiaId': compania.id,
            'compania': compania.compania,
            'ubicaciones': ubicaciones.values('nombre'),
            'aplicaciones': aplicaciones.values('nombre'),
            'talleres': talleres.values('nombre')
        })

#? Metodo para ordenamiento de vehiculo y llantas
class Ordenamientovehiculollantas(mixins.ListModelMixin, GenericAPIView):
    serializer_class = OrdenamientoPorvehiculoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication] 
    def get_queryset(self):
        user = self.request.user
        perfil = models.Perfil.objects.get(user=user)
        compania = perfil.compania
        vehiculo = models.Vehiculo.objects.filter(compania = compania)
        return vehiculo
    def get(self, request, *args, **kwargs): 
        llantas = self.get_queryset()
        print(llantas[0].llanta_set.filter(inventario = 'Rodante'))
        return self.list(request, *args, **kwargs)
    
    
#? ordenamiento por llanta/vehiculo
class Ordenamientollantas(mixins.ListModelMixin, GenericAPIView):
    serializer_class = OrdenamientoPorllantaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication] 
    
    def get_queryset(self):
        user = self.request.user
        perfil = models.Perfil.objects.get(user=user)
        compania = perfil.compania
        llantas = models.Llanta.objects.filter(compania = compania)
        return llantas
    def get(self, request, *args, **kwargs):        
        return self.list(request, *args, **kwargs)

#? api para las inspecciones
class InspeccionVehiculo(mixins.ListModelMixin, GenericAPIView):
    
    serializer_class = InspeccionesSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication] 
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        perfil = models.Perfil.objects.get(user=user)
        compania = perfil.compania
        vehiculo = models.Vehiculo.objects.filter(compania = compania)
        
        #? Obtencion de los parametros
        datos = request.data['results']
        #print(datos)
        for dato in datos:
            #? Convercion de los datos vehiculo
            vehiculo = int(dato['vehiculo'])
            km = int(dato['km'])
            tipo_de_evento = dato['tipo_de_evento']
            
            #? consulta
            vehiculo = models.Vehiculo.objects.get(id = vehiculo)
            vehiculo.km = km
            
            observaciones = dato['observaciones']
            
            for observacion in observaciones:
                observacion = observacion["observacion"]
                observacion = models.Observacion.objects.get(observacion = observacion)
            
        
            llantas = dato['llantas']
            for llanta in llantas:
                llanta_id = int(llanta["llanta"])
                
                presion = int(llanta["presion"])
                profundidad_izquierda = float(llanta["profundidad_izquierda"])
                profundidad_central = float(llanta["profundidad_central"])
                profundidad_derecha = float(llanta["profundidad_derecha"])
                imagen = llanta["imagen"]
                observaciones_llantas = llanta["observaciones_llantas"]
                for observacion_llanta in observaciones_llantas:
                    observacion_llanta = observacion_llanta["observacion_llanta"]
                    print(observacion_llanta)
                    
        return Response({'hola':'hols'})
    
    
    
                                        
    


    
    
    
    

    
    
    