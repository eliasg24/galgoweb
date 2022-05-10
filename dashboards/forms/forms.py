# Django
from django import forms

# Models
from dashboards.models import Inspeccion, Vehiculo, Excel, Llanta, Producto, Renovador, Desecho, Compania, Observacion, Rechazo, Ubicacion, Taller, User, Perfil, Aplicacion
from django.contrib.auth.models import Group


class LlantaForm(forms.ModelForm):
    # Model form del Llanta
    class Meta:
        # Configuración del Form
        model = Llanta
        fields = ("numero_economico",)

class VehiculoForm(forms.ModelForm):
    # Model form del Vehiculo
    class Meta:
        # Configuración del Form
        model = Vehiculo
        fields = ("numero_economico",)

class ProductoForm(forms.ModelForm):
    # Model form del Producto
    class Meta:
        # Configuración del Form
        model = Producto
        fields = ['producto', 'compania', 'marca', 'dibujo', 'rango', 'dimension', 'profundidad_inicial', 'aplicacion', 'vida', 'precio', 'km_esperado']

class RenovadorForm(forms.ModelForm):
    # Model form del Renovador
    class Meta:
        # Configuración del Form
        model = Renovador
        fields = ["nombre", 'ciudad', 'marca']

class DesechoForm(forms.ModelForm):
    # Model form del Desecho
    llanta = forms.ModelChoiceField(queryset=Llanta.objects.all(), to_field_name = 'numero_economico')
    class Meta:
        # Configuración del Form
        model = Desecho
        fields = ['llanta', 'zona_de_llanta', 'condicion', 'razon']

class DesechoEditForm(forms.ModelForm):
    # Model form del Desecho
    llanta = forms.ModelChoiceField(queryset=Llanta.objects.all(), to_field_name = 'numero_economico')
    class Meta:
        # Configuración del Form
        model = Desecho
        fields = ['id', 'llanta', 'zona_de_llanta', 'condicion', 'razon']


class ObservacionForm(forms.ModelForm):
    # Model form de la Observación
    llanta = forms.ModelChoiceField(queryset=Llanta.objects.all(), to_field_name = 'numero_economico')
    class Meta:
        # Configuración del Form
        model = Observacion
        fields = ['llanta', 'observacion', 'color']

class ObservacionEditForm(forms.ModelForm):
    # Model form de la Observación
    llanta = forms.ModelChoiceField(queryset=Llanta.objects.all(), to_field_name = 'numero_economico')
    class Meta:
        # Configuración del Form
        model = Observacion
        fields = ['id', 'llanta', 'observacion', 'color']

class RechazoForm(forms.ModelForm):
    # Model form del Rechazo
    llanta = forms.ModelChoiceField(queryset=Llanta.objects.all(), to_field_name = 'numero_economico')
    class Meta:
        # Configuración del Form
        model = Rechazo
        fields = ['llanta', 'razon']

class RechazoEditForm(forms.ModelForm):
    # Model form del Rechazo
    llanta = forms.ModelChoiceField(queryset=Llanta.objects.all(), to_field_name = 'numero_economico')
    class Meta:
        # Configuración del Form
        model = Rechazo
        fields = ['id', 'llanta', 'razon']

class SucursalForm(forms.ModelForm):
    # Model form de la Sucursal
    compania = forms.ModelChoiceField(queryset=Compania.objects.all(), to_field_name = 'compania')
    class Meta:
        # Configuración del Form
        model = Ubicacion
        fields = ["nombre", "compania", "rendimiento_de_nueva", "rendimiento_de_primera", "rendimiento_de_segunda", "rendimiento_de_tercera", "rendimiento_de_cuarta", "precio_nueva", "precio_renovada", "precio_nueva_direccion"]

class TallerForm(forms.ModelForm):
    # Model form del Taller
    compania = forms.ModelChoiceField(queryset=Compania.objects.all(), to_field_name = 'compania')
    class Meta:
        # Configuración del Form
        model = Taller
        fields = ["nombre", "compania"]

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    # Here we add the extra form fields that we will use to create another model object
    compania = forms.CharField(required=False)
    ubicacion = forms.CharField(required=False)
    aplicacion = forms.CharField(required=False)
    groups = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password',]

class AplicacionForm(forms.ModelForm):
    # Model form de la Aplicación
    compania = forms.ModelChoiceField(queryset=Compania.objects.all(), to_field_name = 'compania')
    ubicacion = forms.ModelChoiceField(queryset=Ubicacion.objects.all(), to_field_name = 'nombre')
    class Meta:
        # Configuración del Form
        model = Aplicacion
        fields = ["nombre", "compania", "ubicacion"]

class CompaniaForm(forms.ModelForm):
    # Model form de la Compania
    class Meta:
        # Configuración del Form
        model = Compania
        fields = ["periodo1_inflado", "periodo2_inflado", "objetivo", "periodo1_inspeccion", "periodo2_inspeccion", "punto_retiro_eje_direccion", "punto_retiro_eje_traccion", "punto_retiro_eje_arrastre", "mm_de_desgaste_irregular", "mm_de_diferencia_entre_duales"]

class UsuarioEditForm(forms.ModelForm):
    # Model form del User
    idioma = forms.CharField(required=False)
    groups = forms.CharField(required=False)

    class Meta:
        # Configuración del Form
        model = User
        fields = ["email", "username"]

class ExcelForm(forms.ModelForm):
    # Model form del Excel
    class Meta:
        # Configuración del Form
        model = Excel
        fields = ("file",)

class EdicionManual(forms.ModelForm):
    class Meta:
        model = Llanta
        fields = ("numero_economico", "producto", "vida", "km_montado", )

class InspeccionForm(forms.ModelForm):
    class Meta:
        model = Inspeccion
        fields = ('llanta', 'km_vehiculo', 'presion', 'observaciones')