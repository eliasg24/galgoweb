from dashboards.functions import functions

def mm_desgastasdos(llanta):
    try:
        min_profundidad = functions.min_profundidad(llanta)
        profundidad_inicial = llanta.producto.profundidad_inicial
        
        if profundidad_inicial == None or min_profundidad == None:
            mm = None
        elif (profundidad_inicial - min_profundidad) < 0:
            mm = None
        elif (profundidad_inicial - min_profundidad) >= 0:
            mm = profundidad_inicial - min_profundidad
            
        else:
            mm = None
            
        return mm
    except:
        mm = None
        return mm
    
def porcentaje_de_desgaste(llanta):
    try:
        profundidad_actual = functions.min_profundidad(llanta)
        profundidad_inicial = llanta.producto.profundidad_inicial
        punto_retiro = functions.punto_de_retiro(llanta)
        operacion = (profundidad_inicial - profundidad_actual) / (profundidad_inicial - punto_retiro)
        if operacion < 0:
            desgaste = 0
        else:
            desgaste = operacion
    except:
        desgaste = None
        operacion = None
    return desgaste


def km_x_mm(llanta):
    try:
        if llanta.km_montado == None:
             km = llanta.km_actual / mm_desgastasdos(llanta)

             print(km)
             print(llanta.km_actual)
             print(mm_desgastasdos(llanta))
        else:
            profundidad_inicial = llanta.producto.profundidad_inicial
            punto_retiro = functions.punto_de_retiro(llanta)
            km = llanta.km_actual / (profundidad_inicial - punto_retiro)
            print(profundidad_inicial)
            print(punto_retiro)
            print(km)
    except:
        km = None
    
    return km

