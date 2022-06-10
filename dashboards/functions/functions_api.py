#Funciones

import json
from django.http import HttpResponse, QueryDict

from dashboards.models import Llanta, Perfil, Taller


def asignarTaller(usuario):
    perfil = Perfil.objects.get(user = usuario)
    llantas = Llanta.objects.filter(compania = perfil.compania)
    taller = Taller.objects.get(pk=1)
    for i in llantas:
        i.taller = taller
    Llanta.objects.bulk_update(llantas, ['taller'])
    

def aplicaciones_list(aplicaciones: QueryDict, ubicaciones_select: list):
    """Obtiene las aplicaciones disponibles y las ubicaciones y las empareja
    Args:
        aplicaciones (QueryDict): Aplicaciones
        ubicaciones_select (list): Ubicaciones

    Returns:
        ap_list (list): Regresa una lista con las aplicaciones ordenada por ubicacion
    """
    ap_list = []
    for ub in ubicaciones_select:
        ubicacion = ub
        aplicaciones_list = []
        for aplicacion in aplicaciones:
            if aplicacion.ubicacion.nombre == ub:
                aplicaciones_list.append({'aplicacion': aplicacion.nombre})
        ap_list.append({
            'ubicacion': ub,
            'aplicaciones': aplicaciones_list
            })
    return ap_list


def companias_list(companias:list):
    """Funcion que recibe una lista de compañias y las devielve en un diccionario

    Args:
        companias (list): Lista de compañias

    Returns:
        companias_list (list): Lista de diccionarios de compañias
    """
    companias_list = []
    for compania in companias:
        companias_list.append({'compania': compania})
    return companias_list



def inventario_none(inventario:str):
    """Devuelve un error si el valor es none

    Args:
        inventario (str): Cadena del inventario

    Returns:
        HttpResponse: Json con el error
    """
    if inventario == None:
        json_context = json.dumps({'status': 'Inventario no especificado'}, indent=None, sort_keys=False, default=str)
        return HttpResponse(json_context, content_type='application/json')


def list_select(lista_select:str):
    """Obtiene la cadena de las ubicaciones o aplicaciones seleccionadas y devuelve una lista

    Args:
        lista_select (str): Cadena de lista

    Returns:
        lista (list): Lista de lista
    """
    lista = []
    if lista_select != None:
        lista = lista_select.split(',')
    return lista


def taller_list(talleres:QueryDict):
    """Funcion que recibe un QueryDict de talleres y las devielve en un diccionario

    Args:
        ubicaciones (QueryDict): Conjunto de talleres

    Returns:
        ubicaciones_list (list): Lista de diccionarios de talleres
    """
    taller_list = []
    for taller in talleres:
            taller_list.append({'taller': taller}) 
    return taller_list


def ubicaciones_list(ubicaciones:QueryDict):
    """Funcion que recibe un QueryDict de ubicacioness y las devielve en un diccionario

    Args:
        ubicaciones (QueryDict): Conjunto de ubicaciones

    Returns:
        ubicaciones_list (list): Lista de diccionarios de ubicaciones
    """
    ubicaciones_list = []
    for ubicacion in ubicaciones:
            ubicaciones_list.append({'ubicacion': ubicacion}) 
    return ubicaciones_list
