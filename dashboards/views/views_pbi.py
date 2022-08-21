from datetime import date
from email.policy import default
import json
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.models import User, Group
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.db.models import FloatField, F, Q, Case, When, Value, IntegerField, CharField, ExpressionWrapper, Func, OuterRef, Subquery, Sum
from django.db.models.functions import Cast, ExtractMonth, ExtractDay, Now, Round, Substr, ExtractYear, Least, Greatest, TruncDate
import numpy

from dashboards.functions import functions
from dashboards.functions.functions import DiffDays, CastDate, min_profundidad, porcentaje, reemplazo_actual
from dashboards.models import Bitacora_Desecho, Observacion, OrdenDesecho, Perfil, Presupuesto, ServicioVehiculo, Tendencia, TendenciaAplicacion, TendenciaCompania, TendenciaUbicacion, Vehiculo, Compania, Ubicacion, Aplicacion, Taller, Llanta, Producto, Desecho, Rendimiento, InspeccionVehiculo, Inspeccion, Bitacora, Bitacora_Pro, ServicioLlanta

from utilidades.functions import functions as utilidades
class CompaniaData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        compania = Compania.objects.filter(compania = compania
                ).annotate(
                objetivo_porcentaje =  (Cast('objetivo', output_field=FloatField()) / 100.0)
                )
        print('************')
        print(compania)
        #Serializar data
        compania = list(compania.values("compania", "periodo1_inflado", "periodo2_inflado", "objetivo_porcentaje", "periodo1_inspeccion", "periodo2_inspeccion", "punto_retiro_eje_direccion", "punto_retiro_eje_traccion", "punto_retiro_eje_arrastre", "punto_retiro_eje_loco", "punto_retiro_eje_retractil", "mm_de_desgaste_irregular", "mm_de_diferencia_entre_duales", "mm_parametro_sospechoso", "unidades_presion", "unidades_distancia", "unidades_profundidad", "valor_casco_nuevo", "valor_casco_1r", "valor_casco_2r", "valor_casco_3r", "valor_casco_4r", "valor_casco_5r"))
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
        sucursales = list(sucursales.values("nombre", "email", "compania__compania", "rendimiento_de_nueva", "rendimiento_de_primera", "rendimiento_de_segunda", "rendimiento_de_tercera", "rendimiento_de_cuarta", "precio_nueva", "precio_renovada", "precio_nueva_direccion"))
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
        aplicaciones = Aplicacion.objects.filter(compania=compania).annotate(sucursal_nombre=F("ubicacion__nombre")).values("nombre", "compania__compania", "sucursal_nombre", "parametro_desgaste_direccion", "parametro_desgaste_traccion", "parametro_desgaste_arrastre", "parametro_desgaste_loco", "parametro_desgaste_retractil")
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
        talleres = list(talleres.values(
                                        "nombre", 
                                        "compania__compania", 
                                        "codigo"
                                        )
                        )
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
        perfil = Perfil.objects.get(user = user)
        #ubicacion = list(perfil.values_list("ubicacion__nombre", flat=True))
        #aplicacion = list(perfil.values_list("aplicacion", flat=True))
        #taller = list(perfil.values_list("taller", flat=True))
        #companias = list(perfil.values_list("companias", flat=True))
        #ubicaciones = list(perfil.values_list("ubicaciones", flat=True))
        #aplicaciones = list(perfil.values_list("aplicaciones", flat=True))
        #talleres = list(perfil.values_list("talleres", flat=True))
                
        dict_context = {
            'perfil': perfil.user.username,
            'compania': perfil.compania.compania,
            'idioma': perfil.idioma,
            "fecha_de_creacion": perfil.fecha_de_creacion,
            "fecha_de_modificacion": perfil.fecha_de_modificacion,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')


class ProductosData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        productos = Producto.objects.filter(compania=compania)
        #Serializar data
        productos = list(productos.values(
            "id",
            "producto",
            "compania__compania",
            "marca",
            "dibujo",
            "rango",
            "dimension",
            "profundidad_inicial",
            "aplicacion",
            "vida",
            "precio",
            "km_esperado",
        ))
        
        dict_context = {
            'productos': productos,
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
        vehiculos = Vehiculo.objects.filter(compania=compania).select_related("compania"
            ).annotate(
                dias_sin_inspeccion=DiffDays(CastDate(Now())-CastDate(F('fecha_ultima_inspeccion')), output_field=IntegerField()), 
                dias_sin_inflar=DiffDays(CastDate(Now())-CastDate(F('fecha_de_inflado')), output_field=IntegerField()),
                vencido=Case(
                    When(dias_sin_inspeccion__gt=F("compania__periodo1_inspeccion"), then=True),
                    When(fecha_ultima_inspeccion=None, then=True),
                    default=False
                    )
            ).annotate(
                lista_observaciones=ArrayAgg(Observacion.objects.filter(id=OuterRef("observaciones_llanta")).values("observacion"))
            ).annotate(
                estatus_pulpo=Case(
                    When(dias_sin_inflar=None, then=Value("Nunca")), 
                    When(lista_observaciones__icontains="Doble mala entrada", then=Value("Doble")), 
                    When(lista_observaciones__icontains="Mala entrada", then=Value("Mala")), 
                    default=Value("Correcta")
                    ),
                vencido_de_inflado= Case(
                    When(dias_sin_inflar=None, then=Value(True)),
                    When(dias_sin_inflar__gt=F('compania__periodo1_inflado'), then=Value(True)),
                    default=False)
            )
        #Serializar data

        vehiculos = list(vehiculos.values(
            "numero_economico",
             "modelo",
             "marca",
             "compania__compania",
             "ubicacion__nombre",
             "aplicacion__nombre",
             "numero_de_llantas",
             "clase",
             "configuracion",
             "fecha_de_inflado",
             "tiempo_de_inflado",
             "presion_de_entrada",
             "presion_de_salida",
             "presion_establecida_1",
             "presion_establecida_2",
             "presion_establecida_3",
             "presion_establecida_4",
             "presion_establecida_5",
             "presion_establecida_6",
             "presion_establecida_7",
             "km",
             "km_diario_maximo",
             "ultima_bitacora_pro_id",
             "estatus_activo",
             "tirecheck",
             "nuevo",
             "fecha_de_creacion",
             "dias_sin_inflar",
             "dias_sin_inspeccion",
             "fecha_ultima_inspeccion",
             "dias_alinear",
             "fecha_ultima_alineacion",
             "estatus_pulpo",
             "vencido_de_inflado"))        
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
        llantas = Llanta.objects.filter(compania=compania
        ).annotate(
            health=Case(When(observaciones__color__in=["Rojo", "Amarillo"], then=False), default=True),
        
            punto_de_retiro = Case(
                When(nombre_de_eje="Dirección", then=F("vehiculo__compania__punto_retiro_eje_direccion")),
                When(nombre_de_eje="Tracción", then=F("vehiculo__compania__punto_retiro_eje_traccion")),
                When(nombre_de_eje="Arrastre", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),
                When(nombre_de_eje="Loco", then=F("vehiculo__compania__punto_retiro_eje_loco")),
                When(nombre_de_eje="Retractil", then=F("vehiculo__compania__punto_retiro_eje_retractil"))
                ),
            p1=Case(
                When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), 
                When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), 
                When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), 
                When(Q(profundidad_izquierda=None), then=Value(4)), 
                When(Q(profundidad_central=None), then=Value(5)), 
                When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField()),
            min_profundidad=
                Case(
                    When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")),
                    When(p1=1, then=F("profundidad_izquierda")), 
                    When(p1=2, then=F("profundidad_central")), 
                    When(p1=3, then=F("profundidad_derecha")), 
                    When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), 
                    When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), 
                    When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), 
                    output_field=FloatField()),
        
            ubicacion_llanta = F('vehiculo__ubicacion__nombre'),
            aplicacion_llanta = F('vehiculo__aplicacion__nombre'),
        
            presion_establecida = Case(
                 When(eje=1, then=F('vehiculo__presion_establecida_1')),
                 When(eje=2, then=F('vehiculo__presion_establecida_2')),
                 When(eje=3, then=F('vehiculo__presion_establecida_3')),
                 When(eje=4, then=F('vehiculo__presion_establecida_4')),
                 When(eje=5, then=F('vehiculo__presion_establecida_5')),
                 When(eje=6, then=F('vehiculo__presion_establecida_6')),
                 When(eje=7, then=F('vehiculo__presion_establecida_7')),
            ),
            
            objetivo =  (Cast('compania__objetivo', output_field=FloatField()) / 100.0),
            
            max_presion = F('presion_establecida') + ( F('presion_establecida') * F('objetivo') ),
            min_presion = F('presion_establecida') - ( F('presion_establecida') * F('objetivo') ),
            status_presion = Case(
                When(presion_actual__lt=F('min_presion'), then=Value('baja')),
                When(presion_actual__gt=F('max_presion'), then=Value('alta')),
                default=Value('buena')
            ),
            status_profundidad = Case(
                When( min_profundidad__lte = F('punto_de_retiro'), then = Value('baja') ),
                default = Value('buena')
            ),
            primera = Case(
                When(primera_inspeccion = None, then=0),
                default=1
            ),
            ultima = Case(
                When(ultima_inspeccion = None, then=0),
                default=2
            ),
            operacion_des = F('primera') + F('ultima'),
            primera_profundidad = Least(
                "primera_inspeccion__profundidad_izquierda", 
                "primera_inspeccion__profundidad_central", 
                "primera_inspeccion__profundidad_derecha"
                ),
            ultima_profundidad = Least(
                "ultima_inspeccion__profundidad_izquierda", 
                "ultima_inspeccion__profundidad_central", 
                "ultima_inspeccion__profundidad_derecha"
                ),
            desgaste_diario = Case(
                When(operacion_des = 3, then=F('primera_profundidad') - F('ultima_profundidad')),
                When(operacion_des = 2, then=Value(0.0)),
                default=None
            ),
            reemplazo = Case(
                When( observaciones__observacion__in=["En punto de retiro", "Baja profundidad"], then=Value('REEMPLAZO') ),
                default=Value('SIN REEMPLAZO')
            )
            
        ).distinct()
        #Serializar data
        llantas = list(llantas.values(
                            "status_presion",
                            "numero_economico",
                            "compania__compania",
                            "vehiculo__numero_economico",
                            "taller__nombre",
                            "renovador__nombre",
                            "vida",
                            "tipo_de_eje",
                            "eje",
                            "posicion",
                            "nombre_de_eje",
                            "presion_de_entrada",
                            "presion_de_salida",
                            "presion_actual",
                            "fecha_de_inflado",
                            "ultima_inspeccion_id",
                            "profundidad_izquierda",
                            "profundidad_central",
                            "profundidad_derecha",
                            "km_actual",
                            "km_montado",
                            "producto__producto",
                            "inventario",
                            "fecha_de_entrada_inventario",
                            "rechazo_id",
                            "tirecheck",
                            "fecha_de_balanceado",
                            "health",
                            "min_profundidad",
                            "ubicacion_llanta",
                            "aplicacion_llanta",
                            "status_profundidad",
                            "desgaste_diario",
                            "reemplazo"
                            ))
        
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
        productos = list(productos.values(
                                        "producto", 
                                        "compania__compania", 
                                        "marca",
                                        "dibujo",
                                        "rango",
                                        "dimension",
                                        "profundidad_inicial",
                                        "aplicacion",
                                        "vida",
                                        "precio",
                                        "km_esperado"
                                           )
                         )
        
        dict_context = {
            'productos': productos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class DesechoDataHistorico(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        desechos = OrdenDesecho.objects.filter(llanta__compania=compania).annotate(
            punto_de_retiro = Case(
                When(llanta__nombre_de_eje="Dirección", then=F("llanta__vehiculo__compania__punto_retiro_eje_direccion")),
                When(llanta__nombre_de_eje="Tracción", then=F("llanta__vehiculo__compania__punto_retiro_eje_traccion")),
                When(llanta__nombre_de_eje="Arrastre", then=F("llanta__vehiculo__compania__punto_retiro_eje_arrastre")),
                When(llanta__nombre_de_eje="Loco", then=F("llanta__vehiculo__compania__punto_retiro_eje_loco")),
                When(llanta__nombre_de_eje="Retractil", then=F("llanta__vehiculo__compania__punto_retiro_eje_retractil"))
                ),
            mm_desechados = Case(
                When(min_profundidad__lte = F('punto_de_retiro'), then=(0.0)),
                When(min_profundidad__gte = F('punto_de_retiro'), then=(F('min_profundidad') - F('punto_de_retiro'))),
                default=None
                ),
            porcentaje_util_desechado = F('mm_desechados') / (F('llanta__producto__profundidad_inicial') - F('punto_de_retiro')),
            valor_casco = Case(
                When(llanta__vida="Nueva", then=F("llanta__vehiculo__compania__valor_casco_nuevo")),
                When(llanta__vida="1R", then=F("llanta__vehiculo__compania__valor_casco_1r")),
                When(llanta__vida="2R", then=F("llanta__vehiculo__compania__valor_casco_2r")),
                When(llanta__vida="3R", then=F("llanta__vehiculo__compania__valor_casco_3r")),
                When(llanta__vida="4R", then=F("llanta__vehiculo__compania__valor_casco_4r")),
                When(llanta__vida="5R", then=F("llanta__vehiculo__compania__valor_casco_5r"))
            ),
            valor_banda_rodamiento = Case(
                When(llanta__vida="Nueva", then=F("llanta__producto__precio") - F('valor_casco')),
                When(llanta__vida="1R", then=F("llanta__producto__precio")),
                When(llanta__vida="2R", then=F("llanta__producto__precio")),
                When(llanta__vida="3R", then=F("llanta__producto__precio")),
                When(llanta__vida="4R", then=F("llanta__producto__precio")),
                When(llanta__vida="5R", then=F("llanta__producto__precio")),
                default=None
            ),
            profundidad_desecho = F('min_profundidad'),
            operacion = F('porcentaje_util_desechado') * F('valor_banda_rodamiento'),
            perdida_total = Case(
                When(desecho__razon = 'Venta', then= F('operacion') - F('valor_casco') ),
                When(desecho__razon = 'Cobrada', then= (F('operacion') + F('valor_casco')) * -1 ),
                When(desecho__razon = 'Fin de vida', then= 0.0),
                default = F('operacion') + F('valor_casco')
            )
        )
        #Serializar data
        desechos = list(desechos.values(
            "usuario__user__username",
            
            "compania__compania",
            "desecho__zona_de_llanta",
            "desecho__condicion",
            "desecho__razon",
            "fecha",
            "llanta__numero_economico",
            "llanta__producto__producto",
            "porcentaje_util_desechado",
            "punto_de_retiro",
            "mm_desechados",
            "valor_casco",
            "llanta__vida",
            "valor_banda_rodamiento",
            "llanta__producto__precio",
            "llanta__producto__profundidad_inicial",
            
            "punto_de_retiro",
            "llanta__vehiculo__numero_economico",
            "llanta__vehiculo__clase",
            "llanta__vehiculo__aplicacion__nombre",
            "llanta__nombre_de_eje",
            "llanta__km_actual",
            
            "profundidad_desecho",
            "perdida_total",
            #"min_profundidad",
            #"llanta",
            #"llanta__nombre_de_eje",
            #"punto_de_retiro",
            #"folio",
        ))
        
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
        rendimientos = Rendimiento.objects.filter(llanta__compania=compania).annotate(
            punto_de_retiro = Case(
                When(llanta__nombre_de_eje="Dirección", then=F("llanta__vehiculo__compania__punto_retiro_eje_direccion")),
                When(llanta__nombre_de_eje="Tracción", then=F("llanta__vehiculo__compania__punto_retiro_eje_traccion")),
                When(llanta__nombre_de_eje="Arrastre", then=F("llanta__vehiculo__compania__punto_retiro_eje_arrastre")),
                When(llanta__nombre_de_eje="Loco", then=F("llanta__vehiculo__compania__punto_retiro_eje_loco")),
                When(llanta__nombre_de_eje="Retractil", then=F("llanta__vehiculo__compania__punto_retiro_eje_retractil"))
                ),
            min_profundidad=Least("llanta__profundidad_izquierda", "llanta__profundidad_central", "llanta__profundidad_derecha"),
            
        ).annotate(
            numero_economico = F('llanta__numero_economico'),
            inventario = F('llanta__inventario'),
            nombre_de_eje = F('llanta__nombre_de_eje'),
            vehiculo__estatus_activo = F('llanta__vehiculo__estatus_activo'),
            vehiculo__modelo = F('llanta__vehiculo__modelo'),
            vehiculo__clase = F('llanta__vehiculo__clase'),
            
            producto__producto = F('llanta__producto__producto'),
            producto__profundidad_inicial = F('llanta__producto__profundidad_inicial'),
            
            km_actual = F('llanta__km_actual'),
            vehiculo__compania__compania = F('llanta__vehiculo__compania__compania'),
            vehiculo__ubicacion__nombre = F('llanta__vehiculo__ubicacion__nombre'),
            vehiculo__aplicacion__nombre = F('llanta__vehiculo__aplicacion__nombre'),
            vehiculo__numero_economico = F('llanta__vehiculo__numero_economico'),
            fecha_de_entrada_inventario = F('llanta__fecha_de_entrada_inventario'),
            vida = F('llanta__vida'),
            taller__nombre = F('llanta__taller__nombre'),
            
            km_montado = F('llanta__km_montado')
            
        ).annotate(
            year_ = F('year'),
            mes_ = F('mes'),
            numero_economico_ = F('numero_economico'),
            mm_desgastados_ = F('mm_desgastados'),
            porcentaje_de_desgaste_ = F('porcentaje_de_desgaste'),
            km_x_mm_ = F('km_x_mm'),
            km_proyectado_ = F('km_proyectado'),
            is_analizada_ = F('is_analizada'),
            cpk_proyectado_ = F('cpk_proyectado'),
            cpk_real_ = F('cpk_real'),
                 
            inventario_ = F('inventario'),
            nombre_de_eje_ = F('nombre_de_eje'),
            vehiculo__estatus_activo_ = F('vehiculo__estatus_activo'),
            vehiculo__modelo_ = F('vehiculo__modelo'),
            vehiculo__clase_ = F('vehiculo__clase'),
                 
            producto__producto_ = F('producto__producto'),
            producto__profundidad_inicial_ = F('producto__profundidad_inicial'),
            min_profundidad_ = F('min_profundidad'),
            punto_de_retiro_ = F('punto_de_retiro'),
            km_actual_ = F('km_actual'),
            vehiculo__compania__compania_ = F('vehiculo__compania__compania'),
            vehiculo__ubicacion__nombre_ = F('vehiculo__ubicacion__nombre'),
            vehiculo__aplicacion__nombre_ = F('vehiculo__aplicacion__nombre'),
            vehiculo__numero_economico_ = F('vehiculo__numero_economico'),
            fecha_de_entrada_inventario_ = F('fecha_de_entrada_inventario'),
            vida_ = F('vida'),
            taller__nombre_ = F('taller__nombre'),
        )
        #Serializar data
        """Mes, Numero economico de la llanta, inventario, nombre del eje, estatus_activo_vehiculo, modelo_vehiculo, clase_vehiculo,
            mm_desgastado, profundidad_inicial, profundidad_actual, punto_retiro_eje, porcentaje_de_desgaste, km_actual_llanta, 
            km_x_mm, km_proyectado / km_teorico_proyectado, analizada, cpk_proyectado, cpk_real, producto_nombre, compania_vehiculo,
            sucursal_vehiculo, aplicacion_vehiculo, ultimo_vehiculo, posicion, fecha_de_entrada_inventario, vida, taller
            """
        rendimientos = list(rendimientos.values(
            "year_",
            "mes_",
            "numero_economico_",
            "mm_desgastados_",
            "porcentaje_de_desgaste_",
            "km_x_mm_",
            "km_proyectado_",
            "is_analizada_",
            "cpk_proyectado_",
            "cpk_real_",
            
            "inventario_",
            "nombre_de_eje_",
            "vehiculo__estatus_activo_",
            "vehiculo__modelo_",
            "vehiculo__clase_",
            
            "producto__producto_",
            "producto__profundidad_inicial_",
            "min_profundidad_",
            "punto_de_retiro_",
            "km_actual_",
            "vehiculo__compania__compania_",
            "vehiculo__ubicacion__nombre_",
            "vehiculo__aplicacion__nombre_",
            "vehiculo__numero_economico_",
            "fecha_de_entrada_inventario_",
            "vida_",
            "taller__nombre_",
            
            
        ))

        dict_context = {
            'rendimientos': rendimientos,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')


class RendimientoActualData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        mes = date.today().month
        llantas = Llanta.objects.filter(compania=compania)
        
        km_actuales = llantas.exclude(km_actual = None).values_list("km_actual", flat=True)
        numero_elementos = km_actuales.count()
        km_actuales_list = list(km_actuales)
        pq_1 = utilidades.percentil(km_actuales_list, 1, numero_elementos)
        pq_3 = utilidades.percentil(km_actuales_list, 3, numero_elementos)
        
        km_filtrados = llantas.filter(km_actual__gte = pq_1, km_actual__lte = pq_3).exclude(km_actual = None)
        km_filtrados_list = list(km_filtrados.values_list("km_actual", flat=True))
        km_filtrados_list.sort()
        
        mediana = numpy.median(km_filtrados_list, axis = None)
        std = numpy.std(km_filtrados_list, axis=None, dtype=numpy.float64)
    
        limite_inferior = mediana - (2*std)
        limite_superior = mediana + (2*std)
        
        
        rendimientos = llantas.annotate(
            punto_de_retiro = Case(
                When(nombre_de_eje="Dirección", then=F("vehiculo__compania__punto_retiro_eje_direccion")),
                When(nombre_de_eje="Tracción", then=F("vehiculo__compania__punto_retiro_eje_traccion")),
                When(nombre_de_eje="Arrastre", then=F("vehiculo__compania__punto_retiro_eje_arrastre")),
                When(nombre_de_eje="Loco", then=F("vehiculo__compania__punto_retiro_eje_loco")),
                When(nombre_de_eje="Retractil", then=F("vehiculo__compania__punto_retiro_eje_retractil"))
                ),
            min_profundidad=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha"),
            mes = Value(mes),
            mm_desgastados = Case(
                When(producto = None, then=None),
                When(producto__profundidad_inicial = None, then=None),
                When(min_profundidad = None, then=None),
                default=F('producto__profundidad_inicial') - F('min_profundidad')
                
            ),
            operacion_porcentaje_de_desgaste = Case(
                When(producto = None, then=None),
                When(producto__profundidad_inicial = None, then=None),
                When(min_profundidad = None, then=None),
                When(punto_de_retiro = None, then=None),
                default = ( F('producto__profundidad_inicial') - F('min_profundidad') ) / ( F('producto__profundidad_inicial') - F('punto_de_retiro') )
            ),
            porcentaje_de_desgaste = Case(
                When(operacion_porcentaje_de_desgaste = None, then=None),
                When(operacion_porcentaje_de_desgaste__lt = 0.0, then=0.0 ),
                default = F('operacion_porcentaje_de_desgaste')
            ),
            km_x_mm = Case(
                When(mm_desgastados = None, then = None),
                When(mm_desgastados = 0.0, then = None),
                When(mm_desgastados = 0.0, then = None),
                When(producto = None, then = None),
                When(producto__profundidad_inicial = None, then=None),
                When(km_actual = None, then = None),
                When(km_montado = None, then = F('km_actual') / F('mm_desgastados') ),
                default = F('km_actual') / ( F('producto__profundidad_inicial') - F('punto_de_retiro') )
            ),
            km_proyectado = Case(
                When(min_profundidad = None, then = None),
                When(producto = None, then = None),
                When(producto__profundidad_inicial = None, then=None),
                When(km_x_mm = None, then=None),
                When(min_profundidad__lt = F('punto_de_retiro'), then=Cast('km_actual', output_field=FloatField()) ),
                default = ( F('producto__profundidad_inicial') - F('punto_de_retiro') ) * F('km_x_mm')
            ),
            limite_inferior = Case(
                When(km_actual__gt = limite_inferior, then = 1.0),
                default = 0.0
            ),
            limite_superior = Case(
                When(km_actual__lt = limite_superior, then = 1.0),
                default = 0.0
            ),
            operacion_analizada = (
                F('limite_inferior') + F('limite_superior')
            ),
            is_analizada = Case(
                When(porcentaje_de_desgaste__lte = .15, then = False),
                When(operacion_analizada = 2.0, then = True),
                default = False
            ),
            cpk_proyectado = Case(
                When(km_proyectado = None, then = None),
                When(km_proyectado = 0, then = None),
                When(producto = None, then=None),
                default = F('producto__precio') / F('km_proyectado')
            ),
            cpk_real = Case(
                When(producto__precio = None, then = None),
                When(km_actual = None, then = None),
                When(km_actual = 0, then = None),
                default = F('producto__precio') / F('km_actual')
            )
            ).annotate(
            year_ = Value(date.today().year),
            mes_ = F('mes'),
            numero_economico_ = F('numero_economico'),
            mm_desgastados_ = F('mm_desgastados'),
            porcentaje_de_desgaste_ = F('porcentaje_de_desgaste'),
            km_x_mm_ = F('km_x_mm'),
            km_proyectado_ = F('km_proyectado'),
            is_analizada_ = F('is_analizada'),
            cpk_proyectado_ = F('cpk_proyectado'),
            cpk_real_ = F('cpk_real'),
                 
            inventario_ = F('inventario'),
            nombre_de_eje_ = F('nombre_de_eje'),
            vehiculo__estatus_activo_ = F('vehiculo__estatus_activo'),
            vehiculo__modelo_ = F('vehiculo__modelo'),
            vehiculo__clase_ = F('vehiculo__clase'),
                 
            producto__producto_ = F('producto__producto'),
            producto__profundidad_inicial_ = F('producto__profundidad_inicial'),
            min_profundidad_ = F('min_profundidad'),
            punto_de_retiro_ = F('punto_de_retiro'),
            km_actual_ = F('km_actual'),
            vehiculo__compania__compania_ = F('vehiculo__compania__compania'),
            vehiculo__ubicacion__nombre_ = F('vehiculo__ubicacion__nombre'),
            vehiculo__aplicacion__nombre_ = F('vehiculo__aplicacion__nombre'),
            vehiculo__numero_economico_ = F('vehiculo__numero_economico'),
            fecha_de_entrada_inventario_ = F('fecha_de_entrada_inventario'),
            vida_ = F('vida'),
            taller__nombre_ = F('taller__nombre'),
        )
            
            
        
        #Serializar data
        """Mes, Numero economico de la llanta, inventario, nombre del eje, estatus_activo_vehiculo, modelo_vehiculo, clase_vehiculo,
            mm_desgastado, profundidad_inicial, profundidad_actual, punto_retiro_eje, porcentaje_de_desgaste, km_actual_llanta, 
            km_x_mm, km_proyectado / km_teorico_proyectado, analizada, cpk_proyectado, cpk_real, producto_nombre, compania_vehiculo,
            sucursal_vehiculo, aplicacion_vehiculo, ultimo_vehiculo, posicion, fecha_de_entrada_inventario, vida, taller
            """
        rendimientos = list(rendimientos.values(
            "year_",
            "mes_",
            "numero_economico_",
            "mm_desgastados_",
            "porcentaje_de_desgaste_",
            "km_x_mm_",
            "km_proyectado_",
            "is_analizada_",
            "cpk_proyectado_",
            "cpk_real_",
            
            "inventario_",
            "nombre_de_eje_",
            "vehiculo__estatus_activo_",
            "vehiculo__modelo_",
            "vehiculo__clase_",
            
            "producto__producto_",
            "producto__profundidad_inicial_",
            "min_profundidad_",
            "punto_de_retiro_",
            "km_actual_",
            "vehiculo__compania__compania_",
            "vehiculo__ubicacion__nombre_",
            "vehiculo__aplicacion__nombre_",
            "vehiculo__numero_economico_",
            "fecha_de_entrada_inventario_",
            "vida_",
            "taller__nombre_",
            
            
        ))
        
        
        
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
        inspecciones_vehiculo = list(inspecciones_vehiculo.values(
            "usuario__user__username",
            "vehiculo__numero_economico",
            "km",
            "fecha"
        ))
        
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
        inspecciones_llanta = Inspeccion.objects.filter(llanta__compania=compania).annotate(
            p1=Case(
                When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), 
                When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), 
                When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), 
                When(Q(profundidad_izquierda=None), then=Value(4)), 
                When(Q(profundidad_central=None), then=Value(5)), 
                When(Q(profundidad_derecha=None), then=Value(6)), 
                default=0, output_field=IntegerField()
                ),
            min_profundidad=Case(
                    When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")),
                    When(p1=1, then=F("profundidad_izquierda")), 
                    When(p1=2, then=F("profundidad_central")), 
                    When(p1=3, then=F("profundidad_derecha")), 
                    When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), 
                    When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), 
                    When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), 
                    output_field=FloatField()
                ),
            objetivo = Cast(F('llanta__compania__objetivo'), output_field=FloatField()) / 100,
            max_presion = F('presion_establecida') +  ( F('presion_establecida') * F('objetivo') ) ,
            min_presion = F('presion_establecida') -  ( F('presion_establecida') * F('objetivo') ) ,
            baja_presion = Case(
                When(presion__lt = F('min_presion'), then=True),
                default=False
            ),
            alta_presion = Case(
                When(presion__gt = F('max_presion'), then=True),
                default=False
            ),
            punto_de_retiro = Case(
                When(llanta__nombre_de_eje="Dirección", then=F("llanta__vehiculo__compania__punto_retiro_eje_direccion")),
                When(llanta__nombre_de_eje="Tracción", then=F("llanta__vehiculo__compania__punto_retiro_eje_traccion")),
                When(llanta__nombre_de_eje="Arrastre", then=F("llanta__vehiculo__compania__punto_retiro_eje_arrastre")),
                When(llanta__nombre_de_eje="Loco", then=F("llanta__vehiculo__compania__punto_retiro_eje_loco")),
                When(llanta__nombre_de_eje="Retractil", then=F("llanta__vehiculo__compania__punto_retiro_eje_retractil"))
                ),
            baja_profundidad = Case(
                When(min_profundidad__lte = F('punto_de_retiro'), then=True),
                default=False
            )
        )
        #Serializar data
        inspecciones_llanta = list(inspecciones_llanta.values(
            "tipo_de_evento",
            "inspeccion_vehiculo_id",
            "llanta__numero_economico",
            "posicion",
            "tipo_de_eje",
            "eje",
            "usuario__user__username",
            "vehiculo__numero_economico",
            "fecha_hora",
            "vida",
            "km_vehiculo",
            "presion",
            "presion_establecida",
            "profundidad_izquierda",
            "profundidad_central",
            "profundidad_derecha",
            "edicion_manual",
            'min_profundidad',
            'baja_presion',
            'alta_presion',
            'baja_profundidad',
        ))
        
        dict_context = {
            'inspecciones_llanta': inspecciones_llanta,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ObservacionesHistoriconData(View): #Historico
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        inspecciones = Inspeccion.objects.filter(llanta__compania=compania).annotate(health=Case(When(observaciones__color__in=["Rojo"], then=False), default=True)).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
        #Serializar data
        inspecciones = list(inspecciones.annotate(fecha=TruncDate("fecha_hora")
                                                  ).values(
                                                        "llanta__numero_economico",
                                                        "observaciones__observacion",
                                                        "fecha",
                                                        "llanta__vehiculo__numero_economico",
                                                        "llanta__compania__compania",
                                                        "llanta__vehiculo__ubicacion__nombre",
                                                        "llanta__vehiculo__aplicacion__nombre",
                                                        "llanta__nombre_de_eje"
                                                        ).exclude(observaciones__observacion = None
                                                        ).exclude(observaciones__observacion = 'Mala entrada'
                                                        ).exclude(observaciones__observacion = 'Doble mala entrada')
                                                    )

        dict_context = {
            'inspecciones': inspecciones,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class ObservacionesActualesData(View): # Actual
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        llantas = Llanta.objects.filter(compania=compania).annotate(health=Case(When(observaciones__color__in=["Rojo"], then=False), default=True)).annotate(p1=Case(When(Q(profundidad_central=None) & Q(profundidad_derecha=None), then=Value(1)), When(Q(profundidad_izquierda=None) & Q(profundidad_derecha=None), then=Value(2)), When(Q(profundidad_izquierda=None) & Q(profundidad_central=None), then=Value(3)), When(Q(profundidad_izquierda=None), then=Value(4)), When(Q(profundidad_central=None), then=Value(5)), When(Q(profundidad_derecha=None), then=Value(6)), default=0, output_field=IntegerField())).annotate(min_profundidad=Case(When(p1=0, then=Least("profundidad_izquierda", "profundidad_central", "profundidad_derecha")), When(p1=1, then=F("profundidad_izquierda")), When(p1=2, then=F("profundidad_central")), When(p1=3, then=F("profundidad_derecha")), When(p1=4, then=Least("profundidad_central", "profundidad_derecha")), When(p1=5, then=Least("profundidad_izquierda", "profundidad_derecha")), When(p1=6, then=Least("profundidad_izquierda", "profundidad_central")), output_field=FloatField()))
        #Serializar data
        llantas = list(llantas.annotate(sucursal=F("vehiculo__ubicacion__nombre")
                                        ).values(
                                        "numero_economico",
                                        "observaciones__observacion",
                                        "compania__compania",
                                        "sucursal",
                                        "vehiculo__aplicacion__nombre",
                                        "nombre_de_eje",
                                        "vehiculo__numero_economico",
                                        ).exclude(observaciones__observacion = None
                                        ).exclude(observaciones__observacion = 'Mala entrada'
                                        ).exclude(observaciones__observacion = 'Doble mala entrada')
                                            )
        
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
        bitacoras = list(bitacoras.values("id", "vehiculo__numero_economico", "compania__compania", "fecha_de_inflado__date", "tiempo_de_inflado", "presion_de_entrada_1", "presion_de_salida_1", "presion_de_entrada_2", "presion_de_salida_2", "presion_de_entrada_3", "presion_de_salida_3", "presion_de_entrada_4", "presion_de_salida_4", "presion_de_entrada_5", "presion_de_salida_5", "presion_de_entrada_6", "presion_de_salida_6", "presion_de_entrada_7", "presion_de_salida_7", "presion_de_entrada_8", "presion_de_salida_8", "presion_de_entrada_9", "presion_de_salida_9", "presion_de_entrada_10", "presion_de_salida_10", "presion_de_entrada_11", "presion_de_salida_11", "presion_de_entrada_12", "presion_de_salida_12", "estatus_pulpo"))

        whens = [When(id=k, then=Value(str(v))) for k, v in entradas_correctas.items()]
        bitacoras_pro = list(bitacoras_pro.annotate(estatus_pulpo=Case(*whens, output_field=CharField())).values("id", "vehiculo__numero_economico", "compania__compania", "fecha_de_inflado__date", "tiempo_de_inflado", "presion_de_entrada_1", "presion_de_salida_1", "presion_de_entrada_2", "presion_de_salida_2", "presion_de_entrada_3", "presion_de_salida_3", "presion_de_entrada_4", "presion_de_salida_4", "presion_de_entrada_5", "presion_de_salida_5", "presion_de_entrada_6", "presion_de_salida_6", "presion_de_entrada_7", "presion_de_salida_7", "presion_de_entrada_8", "presion_de_salida_8", "presion_de_entrada_9", "presion_de_salida_9", "presion_de_entrada_10", "presion_de_salida_10", "presion_de_entrada_11", "presion_de_salida_11", "presion_de_entrada_12", "presion_de_salida_12", "estatus_pulpo"))
       
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
        servicios_llantas = ServicioLlanta.objects.filter(llanta__compania=compania).values(
            "id",
            "serviciovehiculo_id",
            "serviciovehiculo__fecha_inicio",
            "llanta__numero_economico",
            "nombre_de_eje",
            "tipo_de_eje",
            "eje",
            "producto__producto",
            "inflado",
            "balanceado",
            "reparado",
            "valvula_reparada",
            "costado_reparado",
            "rotar",
            "rotar_mismo",
            "rotar_otro",
            "desmontaje",
            "llanta_cambio__numero_economico",
            "inventario_de_desmontaje",
            "taller_de_desmontaje__nombre",
            "razon_de_desmontaje",
            "km_desmontaje"
        )
        #Serializar data
        servicios_llantas = list(servicios_llantas)
        
        dict_context = {
            'servicios_llantas': servicios_llantas,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')

class AccionVehiculoData(View): 
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        servicios_vehiculo = ServicioVehiculo.objects.filter(vehiculo__compania=compania).values(
            "id",
            "folio",
            "vehiculo__numero_economico",
            "usuario__username",
            "fecha_inicio",
            "horario_inicio",
            "fecha_final",
            "horario_final",
            "ubicacion__nombre",
            "aplicacion__nombre",
            "alineacion",
            "estado",
        )
        #Serializar data
        servicios_vehiculo = list(servicios_vehiculo)
        
        dict_context = {
            'servicios_vehiculo': servicios_vehiculo,
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

class PresupuestosData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        presupuesto = Presupuesto.objects.filter(compania=compania)
        #Serializar data
        presupuesto = list(presupuesto.values("mes_ano", "compania__compania", "ubicacion__nombre", "presupuesto", "gasto_real", "km_recorridos"))
        
        dict_context = {
            'presupuesto': presupuesto,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
class TendenciaData(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        tendencias = Tendencia.objects.filter(compania=compania)
        #Serializar data
        tendencias = list(tendencias.values(
            "fecha",
            "compania__compania",
            "ubicacion__nombre",
            "aplicacion__nombre",
            "clase",
            "correctas_pulpo",
            "correctas_inspeccion",
            "inspecciones_a_tiempo",
            "health",
            "buena_presion",
        ))
        
        dict_context = {
            'tendencias': tendencias,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')


class TendenciaDataAplicacion(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        tendencias = TendenciaAplicacion.objects.filter(compania=compania)
        #Serializar data
        tendencias = list(tendencias.values(
            "fecha",
            "compania__compania",
            "ubicacion__nombre",
            "aplicacion__nombre",
            "correctas_pulpo",
            "correctas_inspeccion",
            "inspecciones_a_tiempo",
            "health",
            "buena_presion",
        ))
        
        dict_context = {
            'tendencias': tendencias,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    
    
class TendenciaDataUbicacion(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        tendencias = TendenciaUbicacion.objects.filter(compania=compania)
        #Serializar data
        tendencias = list(tendencias.values(
            "fecha",
            "compania__compania",
            "ubicacion__nombre",
            "correctas_pulpo",
            "correctas_inspeccion",
            "inspecciones_a_tiempo",
            "health",
            "buena_presion",
        ))
        
        dict_context = {
            'tendencias': tendencias,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')
    

class TendenciaDataCompania(View):
    def get(self, request , *args, **kwargs):
        #Queryparams
        usuario = kwargs['usuario']
        user = User.objects.get(username = usuario)
        perfil = Perfil.objects.get(user = user)
        compania = perfil.compania
        tendencias = TendenciaCompania.objects.filter(compania=compania)
        #Serializar data
        tendencias = list(tendencias.values(
            "fecha",
            "compania__compania",
            "correctas_pulpo",
            "correctas_inspeccion",
            "inspecciones_a_tiempo",
            "health",
            "buena_presion",
        ))
        
        dict_context = {
            'tendencias': tendencias,
        }

        json_context = json.dumps(dict_context, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')