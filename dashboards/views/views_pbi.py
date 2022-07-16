import json
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.models import User, Group
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func, OuterRef, Subquery
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest

from dashboards.functions import functions
from dashboards.functions.functions import DiffDays, CastDate
from dashboards.models import Observacion, Perfil, Vehiculo, Compania, Ubicacion, Aplicacion, Taller, Llanta, Producto, Desecho, Rendimiento, InspeccionVehiculo, Inspeccion, Bitacora, Bitacora_Pro, ServicioLlanta

class CompaniaData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.companias.all()
        print(compania)
        #Serializar data
        compania = list(compania.values())
        print(compania)
        
        dict_context = {
            'compania': compania,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class SucursalData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        sucursales = Ubicacion.objects.filter(compania=compania)
        #Serializar data
        print(sucursales)
        sucursales = list(sucursales.values())
        print(sucursales)
        
        dict_context = {
            'sucursales': sucursales,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class AplicacionData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        aplicaciones = Aplicacion.objects.filter(compania=compania).annotate(sucursal=F("ubicacion")).values("id", "nombre", "compania", "sucursal", "parametro_desgaste_direccion", "parametro_desgaste_traccion", "parametro_desgaste_arrastre", "parametro_desgaste_loco", "parametro_desgaste_retractil")
        #Serializar data
        print(aplicaciones)
        aplicaciones = list(aplicaciones)
        print(aplicaciones)
        
        dict_context = {
            'aplicaciones': aplicaciones,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class TallerData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        talleres = Taller.objects.filter(compania=compania)
        #Serializar data
        print(talleres)
        talleres = list(talleres.values())
        print(talleres)
        
        dict_context = {
            'talleres': talleres,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class PerfilData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.filter(user = user)
        ubicacion = list(perfil.values_list("ubicacion", flat=True))
        aplicacion = list(perfil.values_list("aplicacion", flat=True))
        taller = list(perfil.values_list("taller", flat=True))
        companias = list(perfil.values_list("companias", flat=True))
        ubicaciones = list(perfil.values_list("ubicaciones", flat=True))
        aplicaciones = list(perfil.values_list("aplicaciones", flat=True))
        talleres = list(perfil.values_list("talleres", flat=True))
        #Serializar data
        perfil = list(perfil.annotate(ubicacion_id=Value(ubicacion, output_field=ArrayField(IntegerField())), aplicacion_id=Value(aplicacion, output_field=ArrayField(IntegerField())), taller_id=Value(taller, output_field=ArrayField(IntegerField())), companias_id=Value(companias, output_field=ArrayField(IntegerField())), ubicaciones_id=Value(ubicaciones, output_field=ArrayField(IntegerField())), aplicaciones_id=Value(aplicaciones, output_field=ArrayField(IntegerField())), talleres_id=Value(talleres, output_field=ArrayField(IntegerField()))).values("user", "user__username", "compania", "ubicacion_id", "aplicacion_id", "taller_id", "idioma", "fecha_de_creacion", "fecha_de_modificacion", "companias_id", "ubicaciones_id", "aplicaciones_id", "talleres_id"))
        print(perfil)
        
        dict_context = {
            'perfil': perfil,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class VehicleData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        vehiculos = Vehiculo.objects.filter(compania=compania).select_related("compania").annotate(dias_sin_inspeccion=DiffDays(CastDate(Now())-CastDate(F('fecha_ultima_inspeccion')), output_field=IntegerField()), dias_sin_inflar=DiffDays(CastDate(Now())-CastDate(F('fecha_de_inflado')), output_field=IntegerField()), vencido=Case(When(dias_sin_inspeccion__gt=F("compania__periodo2_inspeccion"), then=True), When(fecha_ultima_inspeccion=None, then=True), default=False)).annotate(lista_observaciones=ArrayAgg(Observacion.objects.filter(id=OuterRef("observaciones_llanta")).values("observacion"))).annotate(estatus_pulpo=Case(When(lista_observaciones__icontains="Doble mala entrada", then=Value("Doble")), When(lista_observaciones__icontains="Mala entrada", then=Value("Mala")), default=Value("Correcta")))
        #Serializar data

        vehiculos = list(vehiculos.values("id", "numero_economico", "modelo", "marca", "compania_id", "ubicacion_id", "aplicacion_id", "numero_de_llantas", "clase", "configuracion", "fecha_de_inflado", "tiempo_de_inflado", "presion_de_entrada", "presion_de_salida", "presion_establecida_1", "presion_establecida_2", "presion_establecida_3", "presion_establecida_4", "presion_establecida_5", "presion_establecida_6", "presion_establecida_7", "km", "km_diario_maximo", "ultima_bitacora_pro_id", "estatus_activo", "tirecheck", "nuevo", "fecha_de_creacion", "dias_sin_inflar", "dias_inspeccion", "dias_sin_inspeccion", "fecha_ultima_inspeccion", "dias_alinear", "fecha_ultima_alineacion", "estatus_pulpo"))
        
        dict_context = {
            'vehiculos': vehiculos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class LlantaData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania=compania).annotate(health=Case(When(observaciones__color__in=["Rojo"], then=False), default=True)).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
        #Serializar data
        llantas = list(llantas.values("id", "numero_economico", "compania_id", "vehiculo_id", "ubicacion_id", "aplicacion_id", "taller_id", "renovador_id", "vida", "tipo_de_eje", "eje", "posicion", "nombre_de_eje", "presion_de_entrada", "presion_de_salida", "presion_actual", "fecha_de_inflado", "ultima_inspeccion_id", "profundidad_izquierda", "profundidad_central", "profundidad_derecha", "km_actual", "km_montado", "producto_id", "inventario", "fecha_de_entrada_inventario", "rechazo_id", "tirecheck", "fecha_de_balanceado", "health", "min_profundidad"))
        
        dict_context = {
            'llantas': llantas,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ProductoData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        productos = Producto.objects.filter(compania=compania)
        #Serializar data
        productos = list(productos.values())
        
        dict_context = {
            'productos': productos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class DesechoData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        desechos = Desecho.objects.filter(compania=compania)
        #Serializar data
        desechos = list(desechos.values())
        
        dict_context = {
            'desechos': desechos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class RendimientoData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        rendimientos = Rendimiento.objects.filter(llanta__compania=compania)
        #Serializar data
        rendimientos = list(rendimientos.values())
        
        dict_context = {
            'rendimientos': rendimientos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class InspeccionesVehiculoData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        inspecciones_vehiculo = InspeccionVehiculo.objects.filter(vehiculo__compania=compania)
        #Serializar data
        inspecciones_vehiculo = list(inspecciones_vehiculo.values())
        
        dict_context = {
            'inspecciones_vehiculo': inspecciones_vehiculo,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class InspeccionesLlantaData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        inspecciones_llanta = Inspeccion.objects.filter(llanta__compania=compania)
        #Serializar data
        inspecciones_llanta = list(inspecciones_llanta.values())
        
        dict_context = {
            'inspecciones_llanta': inspecciones_llanta,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ObservacionesInspeccionData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        inspecciones = Inspeccion.objects.filter(llanta__compania=compania).annotate(health=Case(When(observaciones__color__in=["Rojo"], then=False), default=True)).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
        #Serializar data
        inspecciones = list(inspecciones.values("id", "llanta__numero_economico", "observaciones__observacion"))
        
        dict_context = {
            'inspecciones': inspecciones,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ObservacionesLlantaData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania=compania).annotate(health=Case(When(observaciones__color__in=["Rojo"], then=False), default=True)).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
        #Serializar data
        llantas = list(llantas.values("numero_economico", "observaciones__observacion"))
        
        dict_context = {
            'llantas': llantas,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ObservacionesVehiculoData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        vehiculos = Vehiculo.objects.filter(compania=compania).select_related("compania").annotate(dias_sin_inspeccion=DiffDays(CastDate(Now())-CastDate(F('fecha_ultima_inspeccion')), output_field=IntegerField()), dias_sin_inflar=DiffDays(CastDate(Now())-CastDate(F('fecha_de_inflado')), output_field=IntegerField()), vencido=Case(When(dias_sin_inspeccion__gt=F("compania__periodo2_inspeccion"), then=True), When(fecha_ultima_inspeccion=None, then=True), default=False), estatus_pulpo=Case(When(observaciones_llanta__observacion__in=["Doble mala entrada"], then=Value("Doble mala entrada")), When(observaciones_llanta__observacion__in=["Mala entrada"], then=Value("Mala entrada")), default=Value("Entrada Correcta")))
        #Serializar data
        vehiculos = list(vehiculos.values("numero_economico", "observaciones__observacion"))
        
        dict_context = {
            'vehiculos': vehiculos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class BitacorasData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        bitacoras = Bitacora.objects.filter(compania=compania)
        bitacoras_pro = Bitacora_Pro.objects.filter(compania=compania)

        entradas_correctas = functions.entrada_correcta_api(bitacoras, bitacoras_pro)

        #Serializar data

        whens = [When(id=k, then=Value(str(v))) for k, v in entradas_correctas.items()]
        bitacoras = bitacoras.annotate(presion_de_entrada_1=F("presion_de_entrada"), presion_de_salida_1=F("presion_de_salida"), presion_de_entrada_2=Value(None, output_field=IntegerField()), presion_de_salida_2=Value(None, output_field=IntegerField()), presion_de_entrada_3=Value(None, output_field=IntegerField()), presion_de_salida_3=Value(None, output_field=IntegerField()), presion_de_entrada_4=Value(None, output_field=IntegerField()), presion_de_salida_4=Value(None, output_field=IntegerField()), presion_de_entrada_5=Value(None, output_field=IntegerField()), presion_de_salida_5=Value(None, output_field=IntegerField()), presion_de_entrada_6=Value(None, output_field=IntegerField()), presion_de_salida_6=Value(None, output_field=IntegerField()), presion_de_entrada_7=Value(None, output_field=IntegerField()), presion_de_salida_7=Value(None, output_field=IntegerField()), presion_de_entrada_8=Value(None, output_field=IntegerField()), presion_de_salida_8=Value(None, output_field=IntegerField()), presion_de_entrada_9=Value(None, output_field=IntegerField()), presion_de_salida_9=Value(None, output_field=IntegerField()), presion_de_entrada_10=Value(None, output_field=IntegerField()), presion_de_salida_10=Value(None, output_field=IntegerField()), presion_de_entrada_11=Value(None, output_field=IntegerField()), presion_de_salida_11=Value(None, output_field=IntegerField()), presion_de_entrada_12=Value(None, output_field=IntegerField()), presion_de_salida_12=Value(None, output_field=IntegerField())).annotate(estatus_pulpo=Case(*whens, output_field=CharField()))
        bitacoras = list(bitacoras.values("id", "vehiculo__id", "compania__id", "fecha_de_inflado__date", "tiempo_de_inflado", "presion_de_entrada_1", "presion_de_salida_1", "presion_de_entrada_2", "presion_de_salida_2", "presion_de_entrada_3", "presion_de_salida_3", "presion_de_entrada_4", "presion_de_salida_4", "presion_de_entrada_5", "presion_de_salida_5", "presion_de_entrada_6", "presion_de_salida_6", "presion_de_entrada_7", "presion_de_salida_7", "presion_de_entrada_8", "presion_de_salida_8", "presion_de_entrada_9", "presion_de_salida_9", "presion_de_entrada_10", "presion_de_salida_10", "presion_de_entrada_11", "presion_de_salida_11", "presion_de_entrada_12", "presion_de_salida_12", "estatus_pulpo"))

        whens = [When(id=k, then=Value(str(v))) for k, v in entradas_correctas.items()]
        bitacoras_pro = list(bitacoras_pro.annotate(estatus_pulpo=Case(*whens, output_field=CharField())).values("id", "vehiculo__id", "compania__id", "fecha_de_inflado__date", "tiempo_de_inflado", "presion_de_entrada_1", "presion_de_salida_1", "presion_de_entrada_2", "presion_de_salida_2", "presion_de_entrada_3", "presion_de_salida_3", "presion_de_entrada_4", "presion_de_salida_4", "presion_de_entrada_5", "presion_de_salida_5", "presion_de_entrada_6", "presion_de_salida_6", "presion_de_entrada_7", "presion_de_salida_7", "presion_de_entrada_8", "presion_de_salida_8", "presion_de_entrada_9", "presion_de_salida_9", "presion_de_entrada_10", "presion_de_salida_10", "presion_de_entrada_11", "presion_de_salida_11", "presion_de_entrada_12", "presion_de_salida_12", "estatus_pulpo"))
       
        bitacoras.extend(bitacoras_pro)

        dict_context = {
            'bitacoras': bitacoras,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class AccionData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        servicios_llantas = ServicioLlanta.objects.filter(llanta__compania=compania).annotate(punto_de_retiro=Case(When(llanta__nombre_de_eje="Dirección", then=F("llanta__compania__punto_retiro_eje_direccion")),When(llanta__nombre_de_eje="Tracción", then=F("llanta__compania__punto_retiro_eje_traccion")),When(llanta__nombre_de_eje="Arrastre", then=F("llanta__compania__punto_retiro_eje_arrastre")),When(llanta__nombre_de_eje="Loco", then=F("llanta__compania__punto_retiro_eje_loco")),When(llanta__nombre_de_eje="Retractil", then=F("llanta__compania__punto_retiro_eje_retractil")))).values("id", "serviciovehiculo__folio", "llanta__numero_economico", "serviciovehiculo__fecha_real", "serviciovehiculo__vehiculo__numero_economico", "llanta__posicion", "llanta__nombre_de_eje", "punto_de_retiro", "serviciovehiculo__vehiculo__ubicacion__nombre", "serviciovehiculo__vehiculo__aplicacion__nombre", "serviciovehiculo__vehiculo__configuracion", "serviciovehiculo__usuario__username", "llanta_cambio__numero_economico", "inventario_de_desmontaje", "taller_de_desmontaje", "razon_de_desmontaje")
        #Serializar data
        servicios_llantas = list(servicios_llantas)
        
        dict_context = {
            'servicios_llantas': servicios_llantas,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ReemplazoData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        llantas = Llanta.objects.filter(vehiculo__compania=compania).filter(inventario="Rodante")
        inspecciones = Inspeccion.objects.filter(llanta__vehiculo__compania=compania)
        ubicacion = Ubicacion.objects.filter(compania=compania)[0]

        embudo_vida1 = functions.embudo_vidas(llantas)
        embudo_vida2 = functions.embudo_vidas_con_regresion(inspecciones, ubicacion, 30)
        embudo_vida3 = functions.embudo_vidas_con_regresion(inspecciones, ubicacion, 60)
        embudo_vida4 = functions.embudo_vidas_con_regresion(inspecciones, ubicacion, 90)

        periodo = {}
        for llanta in llantas:
            if llanta in embudo_vida1[0]:
                periodo[llanta.id] = "Hoy"
            elif llanta in embudo_vida2[0]:
                periodo[llanta.id] = "30 días"
            elif llanta in embudo_vida3[0]:
                periodo[llanta.id] = "60 días"
            elif llanta in embudo_vida4[0]:
                periodo[llanta.id] = "90 días"
            else:
                periodo[llanta.id] = "-"

        print(periodo)
            
        dict_context = {
            'llantas': list(llantas.annotate(periodo=periodo[F("id")]).values("numero_economico", "vehiculo__numero_economico", "compania", "posicion", "eje", "ubicacion__nombre", "aplicacion__nombre", "vehiculo__clase", "producto__precio", "producto__producto", "nombre_de_eje", "vida", "periodo"))
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')