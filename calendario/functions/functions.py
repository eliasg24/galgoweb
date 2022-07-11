from datetime import date
from dashboards.models import Llanta, ServicioLlanta, ServicioVehiculo, Taller
from dashboards.functions import functions as func


def servicio_vehiculo_guardado(servicio, preguardado_vehiculo):
    vehiculo = servicio.vehiculo
    vehiculo_acomodado = func.vehiculo_con_ejes_acomodados(vehiculo.id)
    vehiculo_acomodado = func.fecha_str_vehiculo(vehiculo_acomodado)
    servicio.estado = 'cerrado'
    servicio.configuracion = func.eje_a_str(vehiculo_acomodado)
    #? Se guardan los servicios
    for vehicule in preguardado_vehiculo:
        if 'alinearVehiculo' in vehicule:
            servicio.alineacion = True
            
    servicio.save()
    return servicio


def servicio_llanta_desmomtaje(servicio, preguardado_llantas_raw):
    preguardado_llantas = []
    for dato in preguardado_llantas_raw:
        if dato:
            preguardado_llantas.append(dato)
    for data in preguardado_llantas:
        if data['tipoServicio'] == 'desmontaje':
            #? Se llama la llanta actual
            llanta = Llanta.objects.get(pk=data['llanta'])
            
            #? Se llama la llanta a montar
            nuevaLlanta = data['llanta_nueva']
            llanta_nueva = Llanta.objects.get(pk = nuevaLlanta)
            
            #? Se obtienen los datos del desmontaje
            razon = data['razon']
            almacen_desmontaje = data['taller_desmontaje']
            taller_desmontaje = Taller.objects.get(id = int(data['taller_desmontaje']))
            
           
            ServicioLlanta.objects.create(
                serviciovehiculo = servicio,
                llanta = llanta,
                desmontaje = True,
                llanta_cambio = llanta_nueva,
                inventario_de_desmontaje = almacen_desmontaje,
                taller_de_desmontaje = taller_desmontaje,
                razon_de_desmontaje = razon
            )
            

def servicio_llanta_servicio(llantas_desmontadas, servicio, preguardado_llantas_raw):
        llantas_rotadas = []
        preguardado_llantas = []
        for dato in preguardado_llantas_raw:
            if dato:
                preguardado_llantas.append(dato)
        for data in preguardado_llantas:
            if data['tipoServicio'] == 'sr':
                #?Se llama la llanta
                llanta = Llanta.objects.get(pk=data['llanta'])
                #? Se verifican que servicios se realizaron
                inflar = True if data['inflar'] == 'True' else False
                balancear = True if data['balancear'] == 'True' else False
                reparar = True if data['reparar'] == 'True' else False
                valvula = True if data['valvula'] == 'True' else False
                costado = True if data['costado'] == 'True' else False
                rotar = data['rotar'] if data['rotar'] != 'False' else False
                rotar_bool = True if rotar == 'mismo' or rotar == 'otro' else False
                rotar_mismo = False
                rotar_otro = False
                llanta_rotar = None
                #? Rotar en el mismo vehiculo
                if rotar == 'mismo':
                    id_llanta_rotar = int(data['llanta_rotar'])
                    llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)
                    
                    if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                        llanta_rotar = None
                        continue
                    
                    rotar_mismo = True
                    
                    llantas_rotadas.append(llanta)
                    llantas_rotadas.append(llanta_rotar)
                    
                #? Rotar en diferente vehiculo
                if rotar == 'otro':
                    id_llanta_rotar = int(data['llanta_rotar'])
                    llanta_rotar = Llanta.objects.get(id = id_llanta_rotar)
                    
                    if llanta_rotar in llantas_rotadas or llanta_rotar in llantas_desmontadas:
                        llanta_rotar = None
                        continue
                    
                    rotar_otro = True
                    
                    llantas_rotadas.append(llanta)
                    llantas_rotadas.append(llanta_rotar)
                    
                ServicioLlanta.objects.create(
                    serviciovehiculo = servicio,
                    llanta = llanta,
                    inflado = inflar,
                    balanceado = balancear,
                    reparado = reparar,
                    valvula_reparada = valvula,
                    costado_reparado = costado,
                    rotar = rotar_bool,
                    rotar_mismo = rotar_mismo,
                    rotar_otro = rotar_otro,
                    llanta_cambio = llanta_rotar
                )