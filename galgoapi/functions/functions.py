def str_to_list_int(cadena:str):
    lista = cadena.split(',')
    lista = list(map(lambda x: int(x), lista))
    return lista