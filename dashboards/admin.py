# Django
from django.apps import AppConfig
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

# Models
from django.contrib.auth.models import User
from django.db.models.fields.related import RelatedField
from dashboards.models import Aplicacion, Bitacora_Pro, Compania, Excel, FTP, HistoricoLlanta, InspeccionVehiculo, LlantasSeleccionadas, OrdenDesecho, ServicioLlanta, ServicioVehiculo, Tendencias, Ubicacion, Vehiculo, Perfil, Bitacora, Llanta, Inspeccion, Producto, Renovador, Desecho, Observacion, Rechazo, Taller, Orden, Bitacora_Desecho, Rendimiento

@admin.register(Bitacora)
class BitacorasAdmin(admin.ModelAdmin):
    # Admin de las Bitácoras
    list_display = ('vehiculo', 'presion_de_entrada', 'presion_de_salida', 'compania', 'fecha_de_inflado')
    search_fields= ('vehiculo__numero_economico',)
    list_filter = ('fecha_de_inflado', 'compania')
    def clase(self, obj):
        if obj.vehiculo:
            return obj.vehiculo.clase

@admin.register(Bitacora_Pro)
class BitacorasProAdmin(admin.ModelAdmin):
    # Admin de las Bitácoras
    list_display = ('vehiculo', 'presion_de_entrada_1', 'presion_de_salida_1', 'compania', 'fecha_de_inflado')
    search_fields= ('vehiculo__numero_economico',)
    list_filter = ('fecha_de_inflado', 'compania')
    verbose_name_plural = "Bitacoras Pro"

@admin.register(Bitacora_Desecho)
class BitacorasDesechoAdmin(admin.ModelAdmin):
    # Admin de las Bitácoras de Desecho
    list_display = ('llanta', 'desecho', )
    search_fields= ('llanta',)
    verbose_name_plural = "Bitacoras Desecho"

@admin.register(Ubicacion)
class UbicacionesAdmin(admin.ModelAdmin):
    # Admin de las Ubicaciones
    list_display = ('nombre', 'compania', 'rendimiento_de_nueva', 'rendimiento_de_primera', 'rendimiento_de_segunda', 'rendimiento_de_tercera', 'rendimiento_de_cuarta')
    search_fields= ('nombre',)
    list_filter = ('compania',)

@admin.register(Taller)
class TalleresAdmin(admin.ModelAdmin):
    # Admin de los Talleres
    list_display = ('nombre', 'compania')
    search_fields= ('nombre',)
    list_filter = ('compania',)


@admin.register(Aplicacion)
class AplicacionesAdmin(admin.ModelAdmin):
    # Admin de las Aplicaciones
    list_display = ('nombre', 'compania')
    search_fields= ('nombre',)
    list_filter = ('compania',)

@admin.register(Tendencias)
class TendenciasAdmin(admin.ModelAdmin):
    # Admin de las Tendencias CPK
    list_display = ('cpk', 'mes', 'vida', 'calificacion')


@admin.register(Vehiculo)
class VehiculosAdmin(admin.ModelAdmin):
    # Admin de los Vehículos
    list_display = ('numero_economico', 'tirecheck', "compania", "km", "presion_establecida_1", 'clase', 'ubicacion', 'aplicacion', 'configuracion', 'fecha_de_creacion')
    search_fields= ('numero_economico',)
    list_filter = ('compania', 'tirecheck', 'fecha_de_creacion', 'clase', "configuracion")

@admin.register(Llanta)
class LlantasAdmin(admin.ModelAdmin):
    # Admin de las Llantas
    list_display = ('numero_economico', "compania", "km_actual", "km_montado", "vehiculo", "producto", 'posicion', "profundidad_izquierda", "profundidad_central", "profundidad_derecha", 'tirecheck', "vehiculo", 'presion_de_entrada', 'presion_de_salida', 'fecha_de_inflado', 'ultima_inspeccion', 'nombre_de_eje', 'vida', 'tipo_de_eje', 'eje')
    search_fields= ('numero_economico',)
    list_filter = ('compania', "km_actual", "km_montado", "inventario", "vehiculo", 'tipo_de_eje')
    

@admin.register(Inspeccion)
class InspeccionesAdmin(admin.ModelAdmin):
    # Admin de las Inspecciones
    list_display = ('id', 'llanta', "profundidad_izquierda", "profundidad_central", "profundidad_derecha", 'fecha_hora', "km_vehiculo")
    search_fields= ('llanta__numero_economico',)
    list_filter = ('llanta__compania', 'llanta')
    def get_view_count(self, obj):
        return obj.llanta.producto
    
@admin.register(InspeccionVehiculo)
class InspeccionVehiculoAdmin(admin.ModelAdmin):
    #Admin de observaciones
    list_display = ( 'id', 'vehiculo', 'fecha')

@admin.register(Excel)
class ExcelAdmin(admin.ModelAdmin):
    # Admin del Excel
    list_display = ('id', 'file')

@admin.register(FTP)
class FTPAdmin(admin.ModelAdmin):
    # Admin del FTP
    list_display = ('file',)

@admin.register(Compania)
class CompaniaAdmin(admin.ModelAdmin):
    # Admin del Perfil
    list_display = ('id', 'compania')
    search_fields= ('compania',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    # Admin del Perfil
    list_display = ('user', 'compania', 'fecha_de_creacion',)
    list_filter = ('fecha_de_creacion',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    #Admin de productos
    list_display = ('producto', 'marca', 'dibujo', 'rango', 'dimension', 'profundidad_inicial', 'vida', 'precio')
    search_fields = ('producto',)
    list_filter = ("compania", 'marca','aplicacion', 'vida',)

@admin.register(Renovador)
class RenovadorAdmin(admin.ModelAdmin):
    #Admin de renovadores
    list_display = ('nombre', 'ciudad', 'marca')
    search_fields = ('nombre',)
    list_filter = ('marca',)

@admin.register(Desecho)
class DesechoAdmin(admin.ModelAdmin):
    #Admin de desechos
    list_display = ('zona_de_llanta', 'condicion', 'razon')

@admin.register(Observacion)
class ObservacionAdmin(admin.ModelAdmin):
    #Admin de observaciones
    list_display = ( 'id', 'observacion', 'icono', 'color', "nivel", "automatico")
    
@admin.register(HistoricoLlanta)
class HistoricoLlantaAdmin(admin.ModelAdmin):
    #Admin de observaciones
    list_display = ( 'num_eco', 'km_recorrido_nuevo', 'km_recorrido_1', "km_recorrido_2", "km_recorrido_3", "km_recorrido_4", "km_recorrido_5")

@admin.register(Rechazo)
class RechazoAdmin(admin.ModelAdmin):
    #Admin de rechazos
    list_display = ('razon',)

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    #Admin de órdenes
    list_display = ('status', 'taller', 'datos')
    search_fields = ('datos',)
    list_filter = ('datos',)
    
@admin.register(OrdenDesecho)
class OrdenDesechoAdmin(admin.ModelAdmin):
    #Admin de órdenes
    list_display = ('folio', 'compania')
    
@admin.register(LlantasSeleccionadas)
class LlantasSeleccionadasAdmin(admin.ModelAdmin):
    # Admin del Perfil
    list_display = ('id', 'perfil', 'inventario')
    search_fields= ('id', 'perfil', 'inventario')


@admin.register(ServicioVehiculo)
class ServicioVehiculoAdmin(admin.ModelAdmin):
    # Admin del Perfil
    list_display = ('folio', 'vehiculo', 'usuario', 'alineacion')


@admin.register(ServicioLlanta)
class ServicioLlantaAdmin(admin.ModelAdmin):
    # Admin del Perfil
    list_display = ('serviciovehiculo', 'llanta', 'llanta', 'inflado', 'balanceado', 'reparado',
                    'valvula_reparada', 'rotar', 'rotar_mismo', 'rotar_otro', 'desmontaje')

@admin.register(Rendimiento)
class RendimientoAdmin(admin.ModelAdmin):
    # Admin del Perfil
    list_display = ('mes', 'llanta', 'analizada')

class ProfileInline(admin.StackedInline):
    # Alinear el admin del perfil con el de User de Django
    model = Perfil
    can_delete = False
    verbose_name_plural = "perfiles"

class UserAdmin(BaseUserAdmin):
    # Agregar el admin del perfil al admin del User de Django
    inlines = (ProfileInline,)
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Group'
    list_display = ("username", "group", "email", "is_staff", "is_active")

admin.site.unregister(User)
admin.site.register(User, UserAdmin)