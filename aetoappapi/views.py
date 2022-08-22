from urllib import response
from django.shortcuts import render, redirect
from rest_framework import generics
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from yaml import serialize
from aetoappapi.serializers import AplicacionDataSerializer, CompaniasPerfilSerializer, ContextPerfilSerializer, TalleresDataSerializer, UbicacionDataSerializer, UserDataSerializer, UserSerializer
from galgoapi.functions import functions as galgofunc
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


from dashboards import models
from rest_framework import mixins
from rest_framework.generics import GenericAPIView

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
        app = models.Ubicacion.objects.filter(compania_id = id, id__in = ubicaciones_perfil)
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
        
        aplicacion = models.Aplicacion.objects.filter(ubicacion__id__in=id, id__in=aplicaciones_perfil).order_by('ubicacion__id')
        
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
        
        talleres = models.Taller.objects.filter(compania__id__in=id, id__in=teller_perfil).order_by('compania__id')
        
        print(talleres)
        self.queryset = talleres 
        return self.list(request, *args, **kwargs)
    
#? Metodo para modificar el contyexto de perfil

class ContextoPerfil(mixins.UpdateModelMixin, GenericAPIView):
    
    #serializer_class = ContextPerfilSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
   
    def get(self, request, *args, **kwargs):   
        user = request.user
        perfil = models.Perfil.objects.get(user=user)
        serializer = self.get_serializer(perfil)
        return Response(status = status.HTTP_200_OK)
    
    
    """
    def put(self, request, *args, **kwargs):

        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):

        return self.partial_update(request, *args, **kwargs)

    
    """



#! TEST
class UserList(generics.ListCreateAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    permission_classes = [IsAuthenticated]
    
    authentication_classes = [TokenAuthentication]
    
    #def get(self, request, *args, **kwargs):
    #    
    #    persona = User.objects.all()
    #    self.queryset = persona
    #    print(request.user)
    #    
    #    return self.list(request, *args, **kwargs)

"""    
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        print(request.body)
        print(request.data)
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
"""


#class Logout(APIView):
#    @method_decorator(csrf_protect)
#    @method_decorator(never_cache)
#    def get(self,request, format = None):
#        request.user.auth_token.delete()
#        logout(request)
#        return Response(status = status.HTTP_200_OK)
#
#