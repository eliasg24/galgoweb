from rest_framework import serializers
from django.contrib.auth.models import User

from dashboards.models import Aplicacion, Compania, Llanta, Perfil, Taller, Ubicacion, Vehiculo

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
        
        
class llantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Llanta
        fields=(
            'numero_economico',
            'vehiculo',
            'posicion',
        )
#? Ordenamiento de llantas por vehiculo acomiodado
class OrdenamientoPorvehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields=(
            'id',
            'numero_economico',    
            'modelo',
            'marca',
            'compania',
            'ubicacion',
            'aplicacion',
            'numero_de_llantas',
            'configuracion',
            'km',
            'observaciones',
            'observaciones_llanta',
            'estatus_activo',
            'nuevo',
            'fecha_de_creacion',
            'dias_inspeccion',
            'fecha_ultima_inspeccion',
            'fecha_ultima_alineacion',  
        
        )
        
#? Ordenamiento de llantas por vehiculo acomiodado
class OrdenamientoPorllantaSerializer(serializers.ModelSerializer):
    Vehiculovehiculo = serializers.CharField(read_only=True, source="vehiculo.numero_economico")
    
    class Meta:
        model = Llanta
        fields=(
            'Vehiculovehiculo',
            'numero_economico',
            'compania',
            'vehiculo',
            'ubicacion',
            'aplicacion',
            'taller',
            'vida',
            'tipo_de_eje',
            'eje',
            'posicion',
            'km_actual',
            'presion_actual',
            'profundidad_izquierda',
            'profundidad_central',
            'profundidad_derecha',
            'km_actual',
            'km_montado',
            'producto',
            'observaciones',
        )
        
        
        
        
    #LLANTA_numero_economico = serializers.IntegerField(read_only=True, source="llanta.numero_economico")
    #LLANTA_compania = serializers.IntegerField(read_only=True, source="llanta.compania")
    #LLANTA_vehiculo = serializers.IntegerField(read_only=True, source="llanta.vehiculo")
    #LLANTA_ubicacion = serializers.IntegerField(read_only=True, source="llanta.ubicacion")
    #LLANTA_aplicacion = serializers.IntegerField(read_only=True, source="llanta.aplicacion")
    #LLANTA_taller = serializers.IntegerField(read_only=True, source="llanta.taller")
    #LLANTA_renovador = serializers.IntegerField(read_only=True, source="llanta.renovador")
    #LLANTA_vida = serializers.IntegerField(read_only=True, source="llanta.vida")
    #LLANTA_tipo_de_eje = serializers.IntegerField(read_only=True, source="llanta.tipo_de_eje")
    #LLANTA_eje = serializers.IntegerField(read_only=True, source="llanta. eje")
    #LLANTA_posicion = serializers.IntegerField(read_only=True, source="llanta.posicion")
    #LLANTA_km_actual = serializers.IntegerField(read_only=True, source="llanta.km_actual")
            #vehiculo
            #' compania',
            #'aplicacion',
            #'numero_de_llantas',
            #'configuracion',
            #'km',
            #'observaciones',
            #'observaciones_llanta',
            #'estatus_activo',
            #'nuevo',
            #'fecha_de_creacion',
            #'dias_inspeccion',
            #'fecha_ultima_inspeccion',
            #'fecha_ultima_alineacion',  
            #
            #'ubicacion',
            
            #'LLANTA_numero_economico',
            #'LLANTA_compania',
            #'LLANTA_vehiculo',
            #'LLANTA_ubicacion',
            #'LLANTA_aplicacion',
            #'LLANTA_taller',
            #'LLANTA_renovador',
            #'LLANTA_vida',
            #'LLANTA_tipo_de_eje',
            #'LLANTA_eje',
            #'LLANTA_posicion',
            #'LLANTA_km_actual',
             