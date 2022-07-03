# Django
from operator import mod
from pyexpat import model
from re import L
from xmlrpc.client import Boolean
from django.contrib.auth.models import User
from django.db import models

# Utilities
from datetime import date, datetime, timedelta

class Compania(models.Model):
    # Modelo de la Compañía

    compania = models.CharField(max_length=200, null=True)

    periodo1_inflado = models.IntegerField(default=30)
    periodo2_inflado = models.IntegerField(default=60)
    objetivo = models.IntegerField(default=10)
    periodo1_inspeccion = models.IntegerField(default=30)
    periodo2_inspeccion = models.IntegerField(default=60)
    opciones_unidades_presion = (("psi", "psi"),
                    ("bar", "bar"),
                    ("mPa", "mPa"),
                )
    opciones_unidades_distancia = (("km", "km"),
                    ("mi", "mi"),
                )
    opciones_unidades_profundidad = (("mm", "mm"),
                    ("32''", "32''"),
                )
    punto_retiro_eje_direccion = models.FloatField(default=3)
    punto_retiro_eje_traccion = models.FloatField(default=3)
    punto_retiro_eje_arrastre = models.FloatField(default=3)
    punto_retiro_eje_loco = models.FloatField(default=3)
    punto_retiro_eje_retractil = models.FloatField(default=3)
    mm_de_desgaste_irregular = models.FloatField(default=3)
    mm_de_diferencia_entre_duales = models.FloatField(default=3)
    mm_parametro_sospechoso = models.FloatField(default=5)
    unidades_presion = models.CharField(max_length=200, choices=opciones_unidades_presion, default="psi")
    unidades_distancia = models.CharField(max_length=200, choices=opciones_unidades_distancia, default="km")
    unidades_profundidad = models.CharField(max_length=200, choices=opciones_unidades_profundidad, default="mm")
    valor_casco_nuevo = models.FloatField(blank=True, null=True)
    valor_casco_1r = models.FloatField(blank=True, null=True)
    valor_casco_2r = models.FloatField(blank=True, null=True)
    valor_casco_3r = models.FloatField(blank=True, null=True)
    valor_casco_4r = models.FloatField(blank=True, null=True)
    valor_casco_5r = models.FloatField(blank=True, null=True)

    def __str__(self):
        # Retorna el nombre de la compañía
        return f"{self.compania}"
    def natural_key(self):
        return f"{self.compania}"

class Ubicacion(models.Model):
    # Modelo de la Ubicación
    # Modelo de la SUCURSAL o FLOTA

    nombre = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    rendimiento_de_nueva = models.IntegerField(default=80)
    rendimiento_de_primera = models.IntegerField(default=70)
    rendimiento_de_segunda = models.IntegerField(default=40)
    rendimiento_de_tercera = models.IntegerField(default=5)
    rendimiento_de_cuarta = models.IntegerField(default=0)
    precio_nueva = models.FloatField(default=4000)
    precio_renovada = models.FloatField(default=2000)
    precio_nueva_direccion = models.FloatField(default=5500)

    def __str__(self):
        # Retorna el nombre de la ubicación
        return f"{self.nombre}"
    class Meta:
        verbose_name_plural = "Ubicaciones"
        
class Taller(models.Model):
    # Modelo del Taller

    nombre = models.CharField(max_length=200, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        # Retorna el nombre del taller
        return f"{self.nombre}"
    class Meta:
        verbose_name_plural = "Talleres"

class Aplicacion(models.Model):
    # Modelo de la Aplicación

    nombre = models.CharField(max_length=200, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, blank=True, null=True)
    parametro_desgaste_direccion = models.FloatField(default=3)
    parametro_desgaste_traccion = models.FloatField(default=4)
    parametro_desgaste_arrastre = models.FloatField(default=3)
    parametro_desgaste_loco = models.FloatField(default=3)
    parametro_desgaste_retractil = models.FloatField(default=3)
    def __str__(self):
        # Retorna el nombre de la aplicación
        return f"{self.nombre}"
    class Meta:
        verbose_name_plural = "Aplicaciones"


class Perfil(models.Model):
    # Modelo del Perfil de Usuario

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, blank=True, null=True)
    ubicacion = models.ManyToManyField("Ubicacion", blank=True, null=True)
    aplicacion = models.ManyToManyField("Aplicacion", blank=True, null=True)
    taller = models.ManyToManyField("Taller", blank=True, null=True)
    opciones_idioma = (("Español", "Español"), ("Inglés", "Inglés"))
    idioma = models.CharField(max_length=200, choices=opciones_idioma, default="Español")

    fecha_de_creacion = models.DateTimeField(auto_now_add=True)
    fecha_de_modificacion = models.DateTimeField(auto_now=True)
    companias = models.ManyToManyField("Compania", null=True, blank=True, related_name="companias")
    ubicaciones = models.ManyToManyField("Ubicacion", blank=True, null=True, related_name="ubicaciones")
    aplicaciones = models.ManyToManyField("Aplicacion", blank=True, null=True, related_name="aplicaciones")
    talleres = models.ManyToManyField("Taller", blank=True, null=True, related_name="talleres")
    def __str__(self):
        # Retorna el username
        return self.user.username
    class Meta:
        verbose_name_plural = "Perfiles"

class Vehiculo(models.Model):
    # Modelo del Vehiculo

    numero_economico = models.CharField(max_length=100)
    modelo = models.CharField(max_length=200, null=True, blank=True)
    marca = models.CharField(max_length=200, null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, blank=True, null=True)
    aplicacion = models.ForeignKey(Aplicacion, on_delete=models.CASCADE, blank=True, null=True)
    numero_de_llantas = models.PositiveIntegerField(default=8)
    opciones_clase = (("ARRASTRE", "Arrastre"),
                    ("TRUCK - BOX", "Truck - Box"),
                    ("VAN", "Van"),
                    ("TRAILER - FLAT BED", "Trailer - Flat Bed"),
                    ("CÁMARA FRIGORÍFICA", "Cámara Frigorífica"),
                    ("COACH", "Coach"),
                    ("TRAILER - DUMP", "Trailer - Dump"),
                    ("RAMPLA PLANA", "Rampla Plana"),
                    ("TRAILER - DUMP", "Trailer - Dump"),
                    ("GONDOLA", "Gondola"),
                    ("TRACTOR - SLEEPER", "Tractor - Sleeper"),
                    ("TRUCK - DUMP", "Truck - Dump"),
                    ("TRAILER", "Trailer"),
                    ("AUTOBUS", "Autobus"),
                    ("AUTOMOVIL", "Automovil"),
                    ("AUTOTANQUE ALIMENTICIO", "Autotanque Alimenticio"),
                    ("AUTOTANQUE COMBUSTIBLE", "Autotanque Combustible"),
                    ("AUTOTANQUE QUIMICOS", "Autotanque Químicos"),
                    ("CAJA REFRIGERADO 48", "Caja Refrigerado 48"),
                    ("CAJA SECA", "Caja Seca"),
                    ("CAJA SECA 40", "Caja Seca 40"),
                    ("CAJA SECA 48", "Caja Seca 48"),
                    ("CAJA SECA 53", "Caja Seca 53"),
                    ("CAJA SECA 53 (3 EJES)", "Caja Seca 53 (3 Ejes)"),
                    ("CAMIÓN", "Camión"),
                    ("CAMIÓN - CAMAROTE", "Camión - Camarote"),
                    ("CAMIONETA", "Camioneta"),
                    ("CAMIONETA LIGERA", "Camioneta ligera"),
                    ("CORTINA", "Cortina"),
                    ("CORTINA 38", "Cortina 38"),
                    ("DOLLY", "Dolly"),
                    ("MOTOCICLETA", "Motocicleta"),
                    ("PICK-UP", "Pick-Up"),
                    ("PLATAFORMA 35", "Plataforma 35"),
                    ("PLATAFORMA 40", "Plataforma 40"),
                    ("PLATAFORMA 53", "Plataforma 53"),
                    ("PLATAFORMA 53 (3 EJES)", "Plataforma 53 (3 Ejes)"),
                    ("PORTACONTENEDOR", "Portacontenedor"),
                    ("RABON", "Rabon"),
                    ("REMOLQUE", "Remolque"),
                    ("REMOLQUE - CAJA SECA", "Remolque - Caja Seca"),
                    ("THERMOKING THORTON CAJA 25", "Thermoking Thorton Caja 25"),
                    ("TOLVA", "Tolva"),
                    ("TORTHON", "Torthon"),
                    ("TORTHON REFRIGERADO", "Torthon Refrigerado"),
                    ("TORTHON SECO", "Torthon Seco"),
                    ("TRACTOR", "Tractor"),
                    ("TRACTOCAMION", "Tractocamion"),
                    ("UTILITARIO TALLER", "Utilitario Taller"),
                    ("UTILITARIO ADMINISTRATIVO", "Utilitario Administrativo"),
                    ("YARD TRUCK", "Yard Truck")
                )
    clase = models.CharField(max_length=200, choices=opciones_clase, null=True, blank=True)
    opciones_configuracion = (("S1.D1", "S1.D1"),
                            ("S2.D2", "S2.D2"),
                            ("S2.D2.D2", "S2.D2.D2"),
                            ("S2.D2.D2.T4.T4", "S2.D2.D2.T4.T4"),
                            ("S2.D2.SP1", "S2.D2.SP1"),
                            ("S2.C4.D4", "S2.C4.D4"),
                            ("S2.D4", "S2.D4"),
                            ("S2.D4.SP1", "S2.D4.SP1"),
                            ("S2.D4.C4.SP1", "S2.D4.C4.SP1"),
                            ("S2.D4.D4", "S2.D4.D4"),
                            ("S2.D4.D4.D4", "S2.D4.D4.D4"),
                            ("S2.D4.D4.L2", "S2.D4.D4.L2"),
                            ("S2.D4.D4.SP1", "S2.D4.D4.SP1"),
                            ("S2.D4.D4.T4.T4", "S2.D4.D4.T4.T4"),
                            ("S2.D4.L4", "S2.D4.L4"),
                            ("S2.S2.D4", "S2.S2.D4"),
                            ("S2.L2.D4", "S2.L2.D4"),
                            ("S2.L2.D4.D4", "S2.L2.D4.D4"),
                            ("S2.L2.D4.D4.D2", "S2.L2.D4.D4.D2"),
                            ("S2.L2.D4.D4.L2", "S2.L2.D4.D4.L2"),
                            ("S2.L2.D4.D4.L4", "S2.L2.D4.D4.L4"),
                            ("S2.L2.L2.D4.D4", "S2.L2.L2.D4.D4"),
                            ("S2.L2.L2.D4.D4.L2", "S2.L2.L2.D4.D4.L2"),
                            ("S2.L2.L2.L2.D4.D4", "S2.L2.L2.L2.D4.D4"),
                            ("S2.L2.L2.L2.L2.D4.D4", "S2.L2.L2.L2.L2.D4.D4"),
                            ("S2.L4.D4", "S2.L4.D4"),
                            ("S2.L4.D4.D4", "S2.L4.D4.D4"),
                            ("T4.T4", "T4.T4"),
                            ("T4.T4.T4", "T4.T4.T4"),
                            ("T4.T4.SP1", "T4.T4.SP1"),
                            ("T4.T4.SP2", "T4.T4.SP2"),
                            ("T4.T4.T4.SP2", "T4.T4.T4.SP2")
                )
    configuracion = models.CharField(max_length=200, choices=opciones_configuracion, null=True, blank=True)
    fecha_de_inflado = models.DateField(null=True, blank=True)
    tiempo_de_inflado = models.FloatField(blank=True, null=True)
    presion_de_entrada = models.IntegerField(blank=True, null=True)
    presion_de_salida = models.IntegerField(blank=True, null=True)
    presion_establecida_1 = models.IntegerField(blank=True, null=True)
    presion_establecida_2 = models.IntegerField(blank=True, null=True)
    presion_establecida_3 = models.IntegerField(blank=True, null=True)
    presion_establecida_4 = models.IntegerField(blank=True, null=True)
    presion_establecida_5 = models.IntegerField(blank=True, null=True)
    presion_establecida_6 = models.IntegerField(blank=True, null=True)
    presion_establecida_7 = models.IntegerField(blank=True, null=True)
    km = models.IntegerField(blank=True, null=True)
    km_diario_maximo = models.IntegerField(blank=True, null=True, default=1000)
    ultima_bitacora_pro = models.ForeignKey("Bitacora_Pro", null=True, blank=True, on_delete=models.CASCADE, related_name="bitacoras_pro")
    observaciones = models.ManyToManyField("Observacion", null=True, blank=True, limit_choices_to={'nivel': "Vehiculo"})
    observaciones_llanta = models.ManyToManyField("Observacion", null=True, blank=True, limit_choices_to={'nivel': "Llanta"}, related_name='observaciones_llanta')
    estatus_activo = models.BooleanField(default=True)
    tirecheck = models.BooleanField(default=False)
    nuevo = models.BooleanField(default=False)
    fecha_de_creacion = models.DateField(auto_now_add=True)
    
    dias_inspeccion = models.IntegerField(blank=True, null=True, default=0)
    fecha_ultima_inspeccion = models.DateField(null=True, blank=True)
    
    dias_alinear = models.IntegerField(blank=True, null=True, default=0)
    fecha_ultima_alineacion = models.DateField(null=True, blank=True)

    def __str__(self):
        # Retorna el número económico
        return f"{self.numero_economico}"

class InspeccionVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    km = models.IntegerField(blank=True, null=True)
    observaciones = models.ManyToManyField("Observacion", null=True, blank=True, limit_choices_to={'nivel': "Vehiculo"})
    fecha = models.DateTimeField(null=True, blank=True, editable=True)
    
class Inspeccion(models.Model):
    # Modelo de la Inspección
    opciones_evento = (("Inspección", "Inspección"),
                       ("Inspección Galgo", "Inspección Galgo")
                )
    tipo_de_evento = models.CharField(max_length=1000, choices=opciones_evento)
    inspeccion_vehiculo = models.ForeignKey(InspeccionVehiculo, on_delete=models.CASCADE, null=True, blank=True)
    llanta = models.ForeignKey("Llanta", on_delete=models.CASCADE, related_name="related_llanta")
    posicion = models.CharField(max_length=4, null=True, blank=True)
    tipo_de_eje = models.CharField(max_length=4, null=True, blank=True)
    eje = models.IntegerField(blank=True, null=True)
    usuario = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True, blank=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now=True, null=True, blank=True)
    opciones_vida = (("Nueva", "Nueva"),
                            ("1R", "1R"),
                            ("2R", "2R"),
                            ("3R", "3R"),
                            ("4R", "4R"),
                            ("5R", "5R"),
                )
    vida = models.CharField(max_length=200, choices=opciones_vida, null=True, blank=True, default="Nueva")
    km_vehiculo = models.IntegerField(null=True, blank=True)
    presion = models.IntegerField(null=True, blank=True)
    presion_establecida = models.IntegerField(blank=True, null=True, default=100)
    profundidad_izquierda = models.FloatField(blank=True, null=True)
    profundidad_central = models.FloatField(blank=True, null=True)
    profundidad_derecha = models.FloatField(blank=True, null=True)
    observaciones = models.ManyToManyField("Observacion", null=True, blank=True, limit_choices_to={'nivel': "Llanta"})
    edicion_manual = models.BooleanField(default=False)
    evento = models.CharField(max_length=1000)

    def __str__(self):
        # Retorna el número económico
        return f"{self.llanta}  |  {self.fecha_hora.strftime('%d-%m-%Y %H:%M:%S')}"
    class Meta:
        verbose_name_plural = "Inspecciones"

class Producto(models.Model):
    # Modelo de productos

    producto = models.CharField(max_length=100, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True)
    marca = models.CharField(max_length=100, null=True, blank=True)
    dibujo = models.CharField(max_length=100, null=True, blank=True)
    rango = models.CharField(max_length=100, null=True, blank=True)
    dimension = models.CharField(max_length=100, null=True, blank=True)
    profundidad_inicial = models.FloatField(null=True)

    opciones_aplicacion = (("Dirección", "Dirección"),
                        ("Tracción", "Tracción"),
                        ("Arrastre", "Arrastre"),
                        ("Mixta", "Mixta"),
                        ("Regional", "Regional"),
                        ("Urbano", "Urbano")
                      )
    aplicacion = models.CharField(max_length=100, choices= opciones_aplicacion, null=True, blank=True)

    opciones_vida = (("Nueva", "Nueva"),
                        ("Renovada", "Renovada"),
                        ("Vitacasco", "Vitacasco"),

                    )
    vida = models.CharField(max_length=100, choices=opciones_vida, null=True)
    precio = models.FloatField(null=True)
    km_esperado = models.IntegerField(null=True, blank=True)

    def __str__(self):
    # Retorna el producto
       return f"{self.producto}"

class Llanta(models.Model):
    # Modelo de la Llanta

    numero_economico = models.CharField(max_length=200, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, blank=True, null=True)
    aplicacion = models.ForeignKey(Aplicacion, on_delete=models.CASCADE, blank=True, null=True)
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, blank=True, null=True)
    renovador = models.ForeignKey('Renovador', on_delete=models.CASCADE, null=True, blank=True)
    opciones_vida = (("Nueva", "Nueva"),
                            ("1R", "1R"),
                            ("2R", "2R"),
                            ("3R", "3R"),
                            ("4R", "4R"),
                            ("5R", "5R"),
                )
    vida = models.CharField(max_length=200, choices=opciones_vida, null=True, blank=True, default="Nueva")
    tipo_de_eje = models.CharField(max_length=4, null=True, blank=True)
    eje = models.IntegerField(blank=True, null=True)
    posicion = models.CharField(max_length=4, null=True, blank=True)
    opciones_de_eje = (("Dirección", "Dirección"),
                        ("Tracción", "Tracción"),
                        ("Arrastre", "Arrastre"),
                        ("Loco", "Loco"),
                        ("Retractil", "Retractil")
                )
    nombre_de_eje = models.CharField(max_length=200, choices=opciones_de_eje, null=True, blank=True)
    presion_de_entrada = models.IntegerField(blank=True, null=True)
    presion_de_salida = models.IntegerField(blank=True, null=True)
    presion_actual = models.IntegerField(blank=True, null=True)
    fecha_de_inflado = models.DateField(null=True, blank=True)
    ultima_inspeccion = models.ForeignKey(Inspeccion, null=True, blank=True, on_delete=models.SET_NULL, related_name="inspecciones")
    profundidad_izquierda = models.FloatField(blank=True, null=True)
    profundidad_central = models.FloatField(blank=True, null=True)
    profundidad_derecha = models.FloatField(blank=True, null=True)
    km_actual = models.IntegerField(blank=True, null=True)
    km_montado = models.IntegerField(blank=True, null=True)

    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.CASCADE)
    opciones_de_inventario = (("Nueva", "Nueva"),
                        ("Antes de Renovar", "Antes de Renovar"),
                        ("Antes de Desechar", "Antes de Desechar"),
                        ("Renovada", "Renovada"),
                        ("Con renovador", "Con renovador"),
                        ("Desecho final", "Desecho final"),
                        ("Servicio", "Servicio"),
                        ("Rodante", "Rodante"),
                        ("Archivado", "Archivado")
                )
    inventario = models.CharField(max_length=200, choices=opciones_de_inventario, null=True, blank=True, default="Rodante")
    fecha_de_entrada_inventario = models.DateField(null=True, blank=True)
    rechazo = models.ForeignKey("Rechazo", on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.ManyToManyField("Observacion", null=True, blank=True, limit_choices_to={'nivel': "Llanta"})
    tirecheck = models.BooleanField(default=False)
    fecha_de_balanceado = models.DateField(null=True, blank=True)

    def __str__(self):
        # Retorna el número económico
        return f"{self.numero_economico}"

class Bitacora(models.Model):
    # Modelo de la Bitácora

    numero_economico = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    fecha_de_inflado = models.DateField(null=True, blank=True)
    tiempo_de_inflado = models.FloatField(blank=True, null=True, default=2)
    presion_de_entrada = models.IntegerField(blank=True, null=True, default=100)
    presion_de_salida = models.IntegerField(blank=True, null=True, default=100)

    def __str__(self):
        # Retorna el número económico
        return f"{self.numero_economico}"

class Bitacora_Pro(models.Model):
    # Modelo de la Bitácora del Pulpo Pro

    numero_economico = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    fecha_de_inflado = models.DateField(null=True, blank=True)
    tiempo_de_inflado = models.FloatField(blank=True, null=True)
    presion_de_entrada_1 = models.IntegerField(blank=True, null=True)
    presion_de_salida_1 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_2 = models.IntegerField(blank=True, null=True)
    presion_de_salida_2 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_3 = models.IntegerField(blank=True, null=True)
    presion_de_salida_3 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_4 = models.IntegerField(blank=True, null=True)
    presion_de_salida_4 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_5 = models.IntegerField(blank=True, null=True)
    presion_de_salida_5 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_6 = models.IntegerField(blank=True, null=True)
    presion_de_salida_6 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_7 = models.IntegerField(blank=True, null=True)
    presion_de_salida_7 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_8 = models.IntegerField(blank=True, null=True)
    presion_de_salida_8 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_9 = models.IntegerField(blank=True, null=True)
    presion_de_salida_9 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_10 = models.IntegerField(blank=True, null=True)
    presion_de_salida_10 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_11 = models.IntegerField(blank=True, null=True)
    presion_de_salida_11 = models.IntegerField(blank=True, null=True)
    presion_de_entrada_12 = models.IntegerField(blank=True, null=True)
    presion_de_salida_12 = models.IntegerField(blank=True, null=True)

    def __str__(self):
        # Retorna el número económico
        return f"{self.numero_economico}"
    class Meta:
        verbose_name_plural = "Bitacoras Pro"

class Excel(models.Model):
    # Modelo del Excel
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    file = models.FileField(upload_to="files/", null=False)

class FTP(models.Model):
    file = models.CharField(max_length=200)

"""class Pulpo(models.Model):
    # Modelo del Pulpo
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    aplicaciones = models.ForeignKey(Aplicacion, on_delete=models.CASCADE)
    bitacoras = models.ForeignKey(Bitacora, on_delete=models.CASCADE)
    doble_entrada = models.JSONField(null=True, blank=True)
    cantidad_doble_entrada = models.JSONField(null=True, blank=True)
    cantidad_inflado = models.IntegerField(blank=True, null=True)
    cantidad_inflado_1 = models.IntegerField(blank=True, null=True)
    cantidad_inflado_2 = models.IntegerField(blank=True, null=True)
    cantidad_entrada = models.IntegerField(blank=True, null=True)
    cantidad_entrada_barras_mes1 = models.IntegerField(blank=True, null=True)
    cantidad_entrada_barras_mes2 = models.IntegerField(blank=True, null=True)
    cantidad_entrada_mes1 = models.IntegerField(blank=True, null=True)
    cantidad_entrada_mes2 = models.IntegerField(blank=True, null=True)
    cantidad_entrada_mes3 = models.IntegerField(blank=True, null=True)
    cantidad_entrada_mes4 = models.IntegerField(blank=True, null=True)
    cantidad_total = models.IntegerField(blank=True, null=True)
    clases_mas_frecuentes_infladas = models.JSONField(null=True, blank=True)
    flotas = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    hoy = models.DateField(null=True, blank=True)"""

class Tendencias(models.Model):
    # Modelo de la Tendencia CPK
    mes = models.DateField()
    llanta = models.ForeignKey(Llanta, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    aplicacion = models.ForeignKey(Aplicacion, on_delete=models.SET_NULL, null=True)
    posicion = models.CharField(max_length=200)
    opciones_de_eje = (("Dirección", "Dirección"),
                        ("Tracción", "Tracción"),
                        ("Arrastre", "Arrastre"),
                        ("Loco", "Loco"),
                        ("Retractil", "Retractil")
                )
    nombre_de_eje = models.CharField(max_length=200, choices=opciones_de_eje, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    km = models.IntegerField()
    km_proyectado = models.IntegerField()
    cpk = models.FloatField()
    min_profundidad = models.FloatField()
    opciones_de_color = (("Amarillo", "Amarillo"),
                ("Rojo", "Rojo"),
                ("NA", "NA")
        )
    color = models.CharField(max_length=200, choices=opciones_de_color)
    buena_presion = models.BooleanField()
    opciones_vida = (("Nueva", "Nueva"),
                            ("1R", "1R"),
                            ("2R", "2R"),
                            ("3R", "3R"),
                            ("4R", "4R"),
                            ("5R", "5R"),
                )
    vida = models.CharField(max_length=200, choices=opciones_vida, null=True, blank=True)
    calificacion = models.IntegerField()
    salud = models.BooleanField()

class Renovador(models.Model):
    # Modelo del Renovador
    nombre = models.CharField(max_length=200)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True)
    ciudad = models.CharField(max_length=200)
    marca = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Renovadores"

class Desecho(models.Model):
    # Modelo del Desecho
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True)
    zona_de_llanta = models.CharField(max_length=200)
    condicion = models.CharField(max_length=200)
    razon = models.CharField(max_length=200)

class Bitacora_Desecho(models.Model):
    # Modelo de la Bitácora del Desecho
    desecho = models.ForeignKey(Desecho, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField()
    llanta = models.ForeignKey(Llanta, on_delete=models.CASCADE, null=True, blank=True)
    porcentaje_util_desechado = models.FloatField()
    mm_desechados = models.FloatField()
    valor_casco = models.FloatField()
    valor_banda_rodamiento = models.FloatField()
    profundidad_de_desecho = models.FloatField()
    perdida_total = models.FloatField()
    foto = models.URLField()

    class Meta:
        verbose_name_plural = "Bitacoras Desecho"

class Observacion(models.Model):
    # Modelo de la Observación
    icono = models.CharField(max_length=200, null=True, blank=True)
    observacion = models.CharField(max_length=200)
    opciones_de_color = (("Amarillo", "Amarillo"),
                ("Rojo", "Rojo"),
                ("NA", "NA")
        )
    color = models.CharField(max_length=200, choices=opciones_de_color)
    opciones_de_nivel = (("Llanta", "Llanta"),
                ("Vehiculo", "Vehiculo"),
        )
    nivel = models.CharField(max_length=200, choices=opciones_de_nivel)
    automatico = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Observaciones"

    def __str__(self):
        # Retorna la Observación
        return f"{self.observacion} | {self.color} | {self.nivel}"

class Rechazo(models.Model):
    # Modelo del Rechazo
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    razon = models.CharField(max_length=200)


class HistoricoLlanta(models.Model):
    num_eco = models.ForeignKey(Llanta, on_delete=models.CASCADE)
    casco_nuevo	= models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="casco_nuevo", null=True)
    km_recorrido_nuevo = models.IntegerField(null=True)
    renovado_1 = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="renovado_1", null=True)
    km_recorrido_1 = models.IntegerField(null=True)
    renovado_2	= models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="renovado_2", null=True)
    km_recorrido_2 = models.IntegerField(null=True)
    renovado_3 = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="renovado_3", null=True)
    km_recorrido_3 = models.IntegerField(null=True)
    renovado_4 = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="renovado_4", null=True)
    km_recorrido_4 = models.IntegerField(null=True)
    renovado_5	= models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="renovado_5", null=True)
    km_recorrido_5 = models.IntegerField(null=True)
    km_total = models.IntegerField(null=True)

class Servicio(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True)
    fecha_programada = models.DateField()
    horario_programada = models.TimeField()
    fecha_real = models.DateField(null=True, blank=True)
    horario_real = models.TimeField(null=True, blank=True)


class ServicioVehiculo(models.Model):
    folio = models.CharField(max_length=200)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    horario_inicio = models.TimeField(null=True, blank=True)
    fecha_final = models.DateField(null=True, blank=True)
    horario_final = models.TimeField(null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, blank=True, null=True)
    aplicacion = models.ForeignKey(Aplicacion, on_delete=models.CASCADE, blank=True, null=True)
    configuracion = models.CharField(max_length=5000)
    alineacion = models.BooleanField(default=False)

class ServicioLlanta(models.Model):
    serviciovehiculo = models.ForeignKey(ServicioVehiculo, null=True, on_delete=models.SET_NULL)
    llanta = models.ForeignKey(Llanta, null=True, on_delete=models.SET_NULL)
    inflado = models.BooleanField(default=False)
    balanceado = models.BooleanField(default=False)
    reparado = models.BooleanField(default=False)
    valvula_reparada = models.BooleanField(default=False)
    costado_reparado = models.BooleanField(default=False)
    rotar = models.BooleanField(default=False)
    rotar_mismo = models.BooleanField(default=False)
    rotar_otro = models.BooleanField(default=False)
    desmontaje = models.BooleanField(default=False)
    llanta_cambio = models.ForeignKey(Llanta, null=True, on_delete=models.SET_NULL, related_name='NuevaLlanta')
    opciones_de_inventario = (("Nueva", "Nueva"),
                        ("Antes de Renovar", "Antes de Renovar"),
                        ("Antes de Desechar", "Antes de Desechar"),
                        ("Renovada", "Renovada"),
                        ("Con renovador", "Con renovador"),
                        ("Desecho final", "Desecho final"),
                        ("Servicio", "Servicio"),
                        ("Rodante", "Rodante"),
                        ("Archivado", "Archivado")
                )
    inventario_de_desmontaje = models.CharField(max_length=200, choices=opciones_de_inventario, null=True, blank=True)
    taller_de_desmontaje = models.ForeignKey(Taller, on_delete=models.SET_NULL, blank=True, null=True)
    razon_de_desmontaje = models.CharField(max_length=200, null=True, blank=True)
    
            
class TareasServicio(models.Model):
    folio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    
    opciones_tarea = (("Prueba", "Prueba"),
            )
    tarea = models.CharField(max_length=200, choices=opciones_tarea)
    vehiculo_1 = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="vehiculo_1")
    posicion_llanta_1 = models.CharField(max_length=200)
    llanta_1 = models.ForeignKey(Llanta, on_delete=models.CASCADE, related_name="llanta_1")
    vehiculo_2 = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="vehiculo_2")
    posicion_llanta_2 = models.CharField(max_length=200)
    llanta_2 = models.ForeignKey(Llanta, on_delete=models.CASCADE, related_name="llanta_2")
    
class Orden(models.Model):
    opcion_status = (
        ("PreOrden", "PreOrden"),
        ("Orden", "Orden"),
        ("AntesRenovar", "AntesRenovar"),
        ("ConRenovador", "ConRenovador"),
        ("CambioTaller", "CambioTaller"),
        ("CambioStock", "CambioStock"),
            )
    status= models.CharField(max_length=200, choices=opcion_status)
    folio= models.CharField(max_length=200)
    datos = models.CharField(max_length=100000)
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, blank=True, null=True)
    renovador = models.ForeignKey(Renovador, on_delete=models.CASCADE, blank=True, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    imagen = models.ImageField(upload_to='desecho', null=True)

    class Meta:
        verbose_name_plural = "Ordenes"
        


class OrdenDesecho(models.Model):
    usuario = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True, blank=True)
    folio= models.CharField(max_length=200)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True)
    llanta = models.ForeignKey(Llanta, on_delete=models.CASCADE)
    fecha = models.DateField(null=True, blank=True)
    min_profundidad = models.IntegerField(blank=True, null=True)
    desecho = models.ForeignKey(Desecho, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='desecho', null=True)

    class Meta:
        verbose_name_plural = "OrdenesDesechos"

     
class LlantasSeleccionadas(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    opciones_de_inventario = (("Nueva", "Nueva"),
                        ("Antes de Renovar", "Antes de Renovar"),
                        ("Antes de Desechar", "Antes de Desechar"),
                        ("Renovada", "Renovada"),
                        ("Con renovador", "Con renovador"),
                        ("Desecho final", "Desecho final"),
                        ("Servicio", "Servicio"),
                        ("Rodante", "Rodante"),
                        ("Archivado", "Archivado")
                )
    inventario = models.CharField(max_length=200, choices=opciones_de_inventario, null=True, blank=True)
    llantas = models.ManyToManyField(Llanta, null=True, blank=True)

    class Meta:
        verbose_name_plural = "LlantasSeleccionadas"

class Rendimiento(models.Model):
    # Modelo de la Bitácora del Desecho
    mes = models.ForeignKey(Desecho, on_delete=models.CASCADE, null=True, blank=True)
    llanta = models.ForeignKey(Llanta, on_delete=models.CASCADE, null=True, blank=True)
    mm_desgastados = models.FloatField()
    porcentaje_de_desgaste = models.FloatField()
    km_x_mm = models.FloatField()
    km_proyectado = models.FloatField()
    analizada = models.FloatField()
    cpk_proyectado = models.FloatField()
    cpk_real = models.FloatField()
