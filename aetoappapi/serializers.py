from rest_framework import serializers

from dashboards.models import Aplicacion, Compania, Inspeccion, InspeccionVehiculo, Llanta, Perfil, Taller, Ubicacion, Vehiculo

from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func

from django.contrib.auth.models import User
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest, TruncDate



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
        
#? Filtrado de llantas rodante de esta manera
#! se puede serializar los annotat
class FilteredLlantasListSerializer(serializers.ListSerializer):
    
    def to_representation(self, data):
        data = data.filter(inventario = 'Rodante').annotate(
            objetivo =  (Cast('vehiculo__compania__objetivo', output_field=FloatField()) / 100.0),
            presion_establecida = Case(
                When(eje = 1, then=F('vehiculo__presion_establecida_1')),
                When(eje = 2, then=F('vehiculo__presion_establecida_2')),
                When(eje = 3, then=F('vehiculo__presion_establecida_3')),
                When(eje = 4, then=F('vehiculo__presion_establecida_4')),
                When(eje = 5, then=F('vehiculo__presion_establecida_5')),
                When(eje = 6, then=F('vehiculo__presion_establecida_6')),
                When(eje = 7, then=F('vehiculo__presion_establecida_7')),
                ),
            max_presion = F('presion_establecida') + ( F('presion_establecida') * F('objetivo') ),
            min_presion = F('presion_establecida') - ( F('presion_establecida') * F('objetivo') ),
            color_midle = Case(
                When(observaciones__color__in=["Rojo"], then=Value('bad')),
                When(observaciones__color__in=["Amarillo"], then=Value('yellow')),
                default=Value('good')
            ),
            ejemplo = Value('hola')
        )
        return super(FilteredLlantasListSerializer, self).to_representation(data) 
    
#? serealizador para implementar las llantas en vehiculos
class llantaSerializer(serializers.ModelSerializer):
    ejemplo = serializers.CharField()
    objetivo = serializers.FloatField()
    presion_establecida = serializers.FloatField()
    max_presion = serializers.FloatField()
    min_presion = serializers.FloatField()
    dimension = serializers.CharField(read_only=True, source="producto.dimension")
    color_midle = serializers.CharField()
    class Meta:
        model = Llanta
        #! con esta libreria elejes el serializador que prefieres
        list_serializer_class = FilteredLlantasListSerializer
        fields=(
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
            'inventario',
            'ejemplo',
            'presion_establecida',
            'objetivo',
            "max_presion",
            "min_presion",
            "dimension",
            "color_midle"
        )
        
#? Ordenamiento de llantas por vehiculo acomiodado
class OrdenamientoPorvehiculoSerializer(serializers.ModelSerializer):
    llanta_set = llantaSerializer(many=True, read_only=True)
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
            'llanta_set',   
        )  
   
#? Ordenamiento de llantas 
class OrdenamientoPorllantaSerializer(serializers.ModelSerializer):
    #Vehiculovehiculo = serializers.CharField(read_only=True, source="vehiculo.numero_economico")
    class Meta:
        model = Llanta
        fields=(
            #'Vehiculovehiculo',
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
        
#? Inpecciones por vehiculos
class InspeccionVehiculoSerializers(serializers.ModelSerializer):
    class Meta:
        model = InspeccionVehiculo
        fields=(
            'opciones_evento',
            'tipo_de_evento',
            'usuario',
            'vehiculo',
            'km',
            'observaciones',
            'fecha',
        )
        
        
class InspeccionesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Inspeccion
        fields=(
            'opciones_evento',
            'tipo_de_evento',
            'inspeccion_vehiculo',
            'llanta',
            'posicion',
            'tipo_de_eje',
            'eje',
            'usuario',
            'vehiculo',
            'vida',
            'km_vehiculo',
            'presion',
            'presion_establecida',
            'profundidad_izquierda',
            'profundidad_central',
            'profundidad_derecha',
            'observaciones',
            'edicion_manual',
            'evento',
            'imagen',
        )
        



"""  
{
  "results": [
    {
      "vehiculo": 115,
      "km": 454,
      "usuario": 19,
      "tipo_de_evento": "Inspección",
      
      "observaciones": [
        ],
      "llantas": [
          {
            "llanta":54489,
            "presion": 90,
            "profundidad_izquierda": 10.0,
            "profundidad_central": 10.0,
            "profundidad_derecha": 10.0,
            "imagen": "null"
          },
          
          {
            "llanta":54489,
            "presion": 90,
            "profundidad_izquierda": 10.0,
            "profundidad_central": 10.0,
            "profundidad_derecha": 10.0,
            "imagen": "null"
          }
        
        ]
    }
    
    ]
}
"""