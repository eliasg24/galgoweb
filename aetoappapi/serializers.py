from rest_framework import serializers
from django.contrib.auth.models import User

from dashboards.models import Aplicacion, Compania, Perfil, Taller, Ubicacion

#? serializador   del Aeto token
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
        )

#? esta es el el suplemento para sacar la compañia en llave foranea de compañia
class CompaniasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compania
        fields = (
            'id',
            'compania'
            )
        
        
#? serializador para la ubicacion del user
class UbicacionDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ubicacion
        fields = (
            'id',
            'nombre',
        )
    
        

#? serializador para usuario

class UserDataSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source="user.id")
    username = serializers.CharField(read_only=True, source="user.username")
    companias = CompaniasSerializer(read_only=True, many=True)
        
    class Meta:
        model = Perfil
        fields = (
            'id',
            'username',
            'companias',
            
        )
        
#? serializador para compañia     
class CompaniasPerfilSerializer(serializers.ModelSerializer):
    companias = CompaniasSerializer(read_only=True, many=True)
    class Meta:
        model = Perfil
        fields = ( 
            'companias',
        )
        

#? serializador para la aplicacion de user 
class AplicacionDataSerializer(serializers.ModelSerializer):
    id_ubicacion = serializers.IntegerField(read_only=True, source="ubicacion.id")
    nombre_ubicaion = serializers.CharField(read_only=True, source="ubicacion.nombre")
    class Meta:
        model = Aplicacion
        fields = (
            'id',
            'nombre',
            'id_ubicacion',
            'nombre_ubicaion',
        )
        
#? serializador para los talleres
class TalleresDataSerializer(serializers.ModelSerializer):
    id_compania = serializers.IntegerField(read_only=True, source="compania.id")
    nombre_compania = serializers.CharField(read_only=True, source="compania.nombre")
    
    class Meta:
        model = Taller
        fields = (
            'id',
            'nombre',
            'id_compania',
            'nombre_compania',
        )
        
#? serializador para la modificacion del contexto
class ContextPerfilSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Perfil
        fields =(
            'id',
            'compania',
            'ubicacion',
            'aplicacion',
            'taller'
        )