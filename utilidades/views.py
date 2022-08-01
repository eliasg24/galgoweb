from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView, TemplateView, DetailView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboards.models import Compania, Inspeccion, InspeccionVehiculo, Llanta, Vehiculo

from utilidades.functions import functions
from dashboards.functions import functions as func

# Create your views here.

class UtilidadesView(LoginRequiredMixin, TemplateView):
    # Vista de CatalogoDesechosView

    template_name = "utilidades/utilidades.html"
    
    
def corregirInspeccionesVehiculo(request):
    compania = Compania.objects.get(compania='PruebaBI')
    inspecciones_vehiculos = InspeccionVehiculo.objects.all()
    for inspeccion in inspecciones_vehiculos:
        user = None
        inspeccion_llanta = Inspeccion.objects.filter(inspeccion_vehiculo=inspeccion)
        for ins in inspeccion_llanta:
            if ins.usuario != None:
                user = ins.usuario
        inspeccion.usuario = user
            
        
    InspeccionVehiculo.objects.bulk_update(inspecciones_vehiculos, ['usuario'])
        
    return redirect('utilidades:utilidades')

def guardar_estado_actual_llantas(request):
    compania = Compania.objects.get(compania='PruebaBI')
    vehiculos = Vehiculo.objects.filter(compania=compania)
    llantas = Llanta.objects.filter(vehiculo__in = vehiculos).exclude(inventario='Nueva')
    print(llantas.count())
    print()
    datos = []
    for llanta in llantas:
        mm_desgastados = functions.mm_desgastasdos(llanta)
        porcentaje_de_desgaste = functions.porcentaje_de_desgaste(llanta)
        km_x_mm = functions.km_x_mm(llanta)
        km_proyectado_sobre_km_teórico_proyectado = ''
        cpk_proyectado = ''
        cpk_real = ''
        try:
            prof_inical = llanta.producto.profundidad_inicial
        except:
            prof_inical = None
            
            
        punto_retiro = func.punto_de_retiro(llanta)
        minima = func.min_profundidad(llanta)

        datos.append({
                        'llanta': llanta,
                        'mm_desgastados': mm_desgastados, 
                        'porcentaje_de_desgaste': porcentaje_de_desgaste,
                        'profundidad_inicial': prof_inical,
                        'punto_retiro': punto_retiro,
                        'minima': minima,
                        'km_x_mm': km_x_mm
                        })
    return render(request, 'utilidades/datos.html',{
        'datos': datos
    } )
    