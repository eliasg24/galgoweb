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
        else:
            profundidad_inicial = llanta.producto.profundidad_inicial
            punto_retiro = functions.punto_de_retiro(llanta)
            km = llanta.km_actual / (profundidad_inicial - punto_retiro)
    except:
        km = None
    
    return km

def km_proyectado(llanta):
    try:
        min_profundidad = functions.min_profundidad(llanta)
        punto_retiro = functions.punto_de_retiro(llanta)
        if min_profundidad < punto_retiro:
            proyectado = llanta.km_actual
        else:
            profundidad_inicial = llanta.producto.profundidad_inicial
            km_por_mm = km_x_mm(llanta)
            proyectado = (profundidad_inicial - punto_retiro) * km_por_mm
    except:
        proyectado = None
    return proyectado

def cpk_proyectado(llanta):
    try:
        precio_llanta = llanta.producto.precio
        km_proyectado_actual = km_proyectado(llanta)
        cpk_p = precio_llanta / km_proyectado_actual
    except:
        cpk_p = None
    return cpk_p


def cpk_real(llanta):
    try:
        precio_llanta = llanta.producto.precio
        km_actual = llanta.km_actual
        cpk = precio_llanta / km_actual
    except:
        cpk = None
    return cpk

def percentil(numeros: list, num_q:int, numero_elementos=None):
    numeros.sort()
    if numero_elementos == None:
        total_num = len(numeros)
    else:
        total_num = numero_elementos
    if num_q == 1:
        indice = round((25/100) * total_num)
    elif num_q == 3:
        indice = round((75/100) * total_num)
    print(f'numeros {numeros}')
    print(f'num_q {num_q}')
    print(f'numero_elementos {numero_elementos}')
    print(f'indice {indice}')
    pq = numeros[(indice-1)]
    
    return pq
    
    
def query_a_str(query):
    lista = []
    for dato in query:
        lista.append(dato['clase'])
    return lista

