from rest_framework import serializers
from django.contrib.auth.models import User

from dashboards.models import Aplicacion, Compania, Perfil, Ubicacion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
        )

#esta es el de la user/compañia
class CompaniasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compania
        fields = (
            'id',
            'compania'
            )
        
#? user

class UserDataSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source="user.id")
    username = serializers.CharField(read_only=True, source="user.username")
    
    class Meta:
        model = Perfil
        fields = (
            'id',
            'username',
            
        )
        
        
class CompaniasPerfilSerializer(serializers.ModelSerializer):
    companias = CompaniasSerializer(read_only=True, many=True)
    class Meta:
        model = Perfil
        fields = ( 
            'companias',
        )
        

class UbicacionDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ubicacion
        fields = (
            'id',
            'nombre',
        )