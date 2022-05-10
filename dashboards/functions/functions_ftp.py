# Django
from django.core.files import File
from django.contrib.auth.models import User

# Utilities
import csv
from dashboards.functions import functions, functions_create
from dashboards.models import Desecho, Llanta, Perfil, Vehiculo, Producto, Ubicacion, Aplicacion, Compania, Inspeccion
from datetime import date, datetime, timedelta
from ftplib import FTP as fileTP
import glob
import os

def ftp_descarga():
    hoy = date.today()
    year = hoy.year
    month = hoy.month
    day = hoy.day
    if month < 10:
        month = f"0{month}"
    if day < 10:
        day = f"0{day}"
    ftp1 = fileTP("208.109.20.121")
    ftp1.login(user="tyrecheck@aeto.com", passwd="TyreDB!25")
    entries = list(ftp1.mlsd())
    entries.sort(key = lambda entry: entry[1]['modify'])
    """for file_name, i in entries:
        file_type1 = file_name[0:18]

        if file_type1 == f"Products{year}_{month}_{day}":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_read_file = open(file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(local_read_file, delimiter=",")
            for row in reader:
                try:
                    if file_type1 == f"Products{year}_{month}_{day}":
                        company = row[1]
                        if company == "SOLAQRO":
                            if company == "SOLAQRO":
                                company = Compania.objects.get(compania="SOLAQRO")
                            try:
                                producto = Producto.objects.get(producto=row[4], compania=company)
                                marca = row[6]
                                dibujo = row[7]
                                dimension = row[8]
                                profundidad_inicial = int(float(row[10]))
                                vida = row[9]
                                if vida == "New":
                                    vida = "Nueva"
                                elif vida == "Retread":
                                    vida = "Renovada"
                                precio = row[12]
                                if precio == "":
                                    precio = 2000
                                else:
                                    precio = int(float(row[12]))
                                producto.marca=marca
                                producto.dibujo=dibujo
                                producto.dimension=dimension
                                producto.profundidad_inicial=profundidad_inicial
                                producto.vida=vida
                                producto.precio=precio
                                producto.save()
                            except:
                                marca = row[6]
                                dibujo = row[7]
                                dimension = row[8]
                                profundidad_inicial = int(float(row[10]))
                                vida = row[9]
                                if vida == "New":
                                    vida = "Nueva"
                                elif vida == "Retread":
                                    vida = "Renovada"
                                precio = row[12]
                                if precio == "":
                                    precio = 2000
                                else:
                                    precio = int(float(row[12]))

                                Producto.objects.create(producto=row[4],
                                                        compania=company,
                                                        marca=marca,
                                                        dibujo=dibujo,
                                                        dimension=dimension,
                                                        profundidad_inicial=profundidad_inicial,
                                                        vida=vida,
                                                        precio=precio
                                                    )

                except:
                    pass
            local_file.close()
            local_read_file.close()
            os.remove(os.path.abspath(file_name))"""

    for file_name, i in entries:
        file_type1 = file_name[0:18]

        if file_type1 == f"Vehicles{year}_{month}_{day}":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_read_file = open(file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(local_read_file, delimiter=",")
            for row in reader:
                try:
                    if file_type1 == f"Vehicles{year}_{month}_{day}":
                        company = row[3]
                        if company == "TRAMO DEL CENTRO":
                            if company == "TRAMO DEL CENTRO":
                                company = Compania.objects.get(compania="Tramo")
                            try:
                                vehiculo = Vehiculo.objects.get(numero_economico=row[9], compania=company)
                                status = row[20]
                                if status != "Inactive":
                                    try:
                                        ubicacion = Ubicacion.objects.get(nombre=row[5], compania=company)
                                    except:
                                        ubicacion = Ubicacion.objects.create(nombre=row[5], compania=company)
                                    try:
                                        aplicacion = Aplicacion.objects.get(nombre=row[7], compania=company)
                                    except:
                                        aplicacion = Aplicacion.objects.create(nombre=row[7], compania=company)
                                    km = row[10]
                                    if km == "":
                                        km = None
                                    else:
                                        km = int(float(row[10]))

                                    presion_establecida_1 = row[22]
                                    if presion_establecida_1 == "":
                                        presion_establecida_1 = None
                                    else:
                                        presion_establecida_1 = int(float(row[22]) * 14.5038)
                                    presion_establecida_2 = row[23]
                                    if presion_establecida_2 == "":
                                        presion_establecida_2 = None
                                    else:
                                        presion_establecida_2 = int(float(row[23]) * 14.5038)
                                    presion_establecida_3 = row[24]
                                    if presion_establecida_3 == "":
                                        presion_establecida_3 = None
                                    else:
                                        presion_establecida_3 = int(float(row[24]) * 14.5038)
                                    presion_establecida_4 = row[25]
                                    if presion_establecida_4 == "":
                                        presion_establecida_4 = None
                                    else:
                                        presion_establecida_4 = int(float(row[25]) * 14.5038)
                                    presion_establecida_5 = row[26]
                                    if presion_establecida_5 == "":
                                        presion_establecida_5 = None
                                    else:
                                        presion_establecida_5 = int(float(row[26]) * 14.5038)
                                    functions_create.crear_clase(row[12])
                                    fecha_de_creacion = row[21]
                                    fecha_de_creacion = functions.convertir_fecha3(fecha_de_creacion)
                                    vehiculo.numero_economico=row[9]
                                    vehiculo.modelo=row[18]
                                    vehiculo.marca=row[16]
                                    vehiculo.compania=company
                                    vehiculo.ubicacion=ubicacion
                                    vehiculo.aplicacion=aplicacion
                                    vehiculo.numero_de_llantas = functions.cantidad_llantas(row[14])
                                    vehiculo.clase = row[12].upper()
                                    vehiculo.configuracion = row[14]
                                    vehiculo.presion_establecida_1=presion_establecida_1
                                    vehiculo.presion_establecida_2=presion_establecida_2
                                    vehiculo.presion_establecida_3=presion_establecida_3
                                    vehiculo.presion_establecida_4=presion_establecida_4
                                    vehiculo.presion_establecida_5=presion_establecida_5
                                    vehiculo.km=km
                                    vehiculo.fecha_de_creacion=fecha_de_creacion
                                    vehiculo.tirecheck=True
                                    vehiculo.save()
                                    llantas = Llanta.objects.filter(vehiculo=vehiculo)
                                    for llanta in llantas:
                                        if (llanta.km_montado or llanta.km_montado == 0) and km:
                                            if llanta.km_montado <= km:
                                                llanta.km_actual = km - llanta.km_montado
                                                llanta.save()
                            except:
                                status = row[20]
                                if status != "Inactive":
                                    try:
                                        ubicacion = Ubicacion.objects.get(nombre=row[5], compania=company)
                                    except:
                                        ubicacion = Ubicacion.objects.create(nombre=row[5], compania=company)
                                    try:
                                        aplicacion = Aplicacion.objects.get(nombre=row[7], compania=company)
                                    except:
                                        aplicacion = Aplicacion.objects.create(nombre=row[7], compania=company)
                                    km = row[10]
                                    if km == "":
                                        km = None
                                    else:
                                        km = int(float(row[10]))


                                    presion_establecida_1 = row[22]
                                    if presion_establecida_1 == "":
                                        presion_establecida_1 = None
                                    else:
                                        presion_establecida_1 = int(float(row[22]) * 14.5038)
                                    presion_establecida_2 = row[23]
                                    if presion_establecida_2 == "":
                                        presion_establecida_2 = None
                                    else:
                                        presion_establecida_2 = int(float(row[23]) * 14.5038)
                                    presion_establecida_3 = row[24]
                                    if presion_establecida_3 == "":
                                        presion_establecida_3 = None
                                    else:
                                        presion_establecida_3 = int(float(row[24]) * 14.5038)
                                    presion_establecida_4 = row[25]
                                    if presion_establecida_4 == "":
                                        presion_establecida_4 = None
                                    else:
                                        presion_establecida_4 = int(float(row[25]) * 14.5038)
                                    presion_establecida_5 = row[26]
                                    if presion_establecida_5 == "":
                                        presion_establecida_5 = None
                                    else:
                                        presion_establecida_5 = int(float(row[26]) * 14.5038)
                                    functions_create.crear_clase(row[12])
                                    fecha_de_creacion = row[21]
                                    fecha_de_creacion = functions.convertir_fecha3(fecha_de_creacion)
                                    vehiculo = Vehiculo.objects.create(numero_economico=row[9],
                                                                    modelo=row[18],
                                                                    marca=row[16],
                                                                    compania=company,
                                                                    ubicacion=ubicacion,
                                                                    aplicacion=aplicacion,
                                                                    numero_de_llantas = functions.cantidad_llantas(row[14]),
                                                                    clase = row[12].upper(),
                                                                    configuracion = row[14],
                                                                    presion_establecida_1=presion_establecida_1,
                                                                    presion_establecida_2=presion_establecida_2,
                                                                    presion_establecida_3=presion_establecida_3,
                                                                    presion_establecida_4=presion_establecida_4,
                                                                    presion_establecida_5=presion_establecida_5,
                                                                    km=km,
                                                                    fecha_de_creacion=fecha_de_creacion,
                                                                    tirecheck=True
                                                                    )
                except:
                    pass
            local_file.close()
            local_read_file.close()
            os.remove(os.path.abspath(file_name))

    """for file_name, i in entries:
        file_type5 = file_name[0:22]

        if file_type5 == f"RollingStock{year}_{month}_{day}":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_read_file = open(file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(local_read_file, delimiter=",")
            for row in reader:
                try:
                    if file_type5 == f"RollingStock{year}_{month}_{day}":
                        company = row[1]
                        if company == "TRAMO DEL CENTRO":
                            if company == "TRAMO DEL CENTRO":
                                company = Compania.objects.get(compania="Tramo")
                                usuario = Perfil.objects.get(user=User.objects.get(username="Tramo"))
                            numero_economico = row[9]
                            try:
                                llanta = Llanta.objects.get(numero_economico=numero_economico, compania=company)
                                vehiculo = Vehiculo.objects.get(numero_economico=row[6], compania=company)
                                vida = row[15]
                                if vida == "New":
                                    vida = "Nueva"
                                elif vida == "1st Retread":
                                    vida = "1R"
                                elif vida == "2st Retread":
                                    vida = "2R"
                                elif vida == "3st Retread":
                                    vida = "3R"
                                elif vida == "4st Retread":
                                    vida = "4R"
                                elif vida == "Retread":
                                    vida = "1R"

                                posicion = row[7]
                                tipo_de_eje = functions.sacar_eje(int(posicion[0]), vehiculo)
                                eje = int(posicion[0])

                                if tipo_de_eje[0] == "S":
                                    nombre_de_eje = "Dirección"
                                elif tipo_de_eje[0] == "D":
                                    nombre_de_eje = "Tracción"
                                elif tipo_de_eje[0] == "T":
                                    nombre_de_eje = "Arrastre"
                                elif tipo_de_eje[0] == "C":
                                    nombre_de_eje = "Loco"
                                elif tipo_de_eje[0] == "L":
                                    nombre_de_eje = "Retractil"

                                producto = row[10]
                                producto = Producto.objects.get(producto=producto, compania=company)

                                try:
                                    aplicacion = Aplicacion.objects.get(nombre=row[4], compania=company)
                                except:
                                    aplicacion = Aplicacion.objects.create(nombre=row[4], compania=company)

                                presion_actual = row[11]
                                if presion_actual == "":
                                    presion_actual = None
                                else:
                                    presion_actual = int(float(row[11]) * 14.5038)

                                min_profundidad = row[12]
                                if min_profundidad == "":
                                    min_profundidad = None
                                else:
                                    min_profundidad = float(row[12])

                                inventario = "Rodante"
                                fecha_de_entrada_inventario = None
                                try:
                                    fecha_de_entrada_inventario = functions.convertir_fecha3(row[18])
                                except:
                                    fecha_de_entrada_inventario = None
                                km_montado = row[13]
                                if km_montado == "":
                                    km_montado = None
                                else:
                                    km_montado = int(float(row[13]))

                                llanta.numero_economico=numero_economico
                                llanta.compania=company
                                llanta.vehiculo=vehiculo
                                llanta.ubicacion=vehiculo.ubicacion
                                llanta.aplicacion=aplicacion
                                llanta.vida=vida
                                llanta.tipo_de_eje=tipo_de_eje
                                llanta.eje=eje
                                llanta.posicion=posicion
                                llanta.nombre_de_eje=nombre_de_eje
                                llanta.presion_actual=presion_actual
                                llanta.profundidad_izquierda=min_profundidad
                                llanta.producto=producto
                                llanta.inventario=inventario
                                llanta.fecha_de_entrada_inventario=fecha_de_entrada_inventario
                                llanta.km_montado=km_montado
                                llanta.tirecheck=True
                                llanta.save()

                            except:
                                try:
                                    vehiculo = Vehiculo.objects.get(numero_economico=row[6], compania=company)
                                    vida = row[15]
                                    if vida == "New":
                                        vida = "Nueva"
                                    elif vida == "1st Retread":
                                        vida = "1R"
                                    elif vida == "2st Retread":
                                        vida = "2R"
                                    elif vida == "3st Retread":
                                        vida = "3R"
                                    elif vida == "4st Retread":
                                        vida = "4R"
                                    elif vida == "Retread":
                                        vida = "1R"

                                    posicion = row[7]
                                    tipo_de_eje = functions.sacar_eje(int(posicion[0]), vehiculo)
                                    eje = int(posicion[0])

                                    if tipo_de_eje[0] == "S":
                                        nombre_de_eje = "Dirección"
                                    elif tipo_de_eje[0] == "D":
                                        nombre_de_eje = "Tracción"
                                    elif tipo_de_eje[0] == "T":
                                        nombre_de_eje = "Arrastre"
                                    elif tipo_de_eje[0] == "C":
                                        nombre_de_eje = "Loco"
                                    elif tipo_de_eje[0] == "L":
                                        nombre_de_eje = "Retractil"

                                    producto = row[10]
                                    producto = Producto.objects.get(producto=producto, compania=company)


                                    try:
                                        aplicacion = Aplicacion.objects.get(nombre=row[4], compania=company)
                                    except:
                                        aplicacion = Aplicacion.objects.create(nombre=row[4], compania=company)

                                    presion_actual = row[11]
                                    if presion_actual == "":
                                        presion_actual = None
                                    else:
                                        presion_actual = int(float(row[11]) * 14.5038)

                                    min_profundidad = row[12]
                                    if min_profundidad == "":
                                        min_profundidad = None
                                    else:
                                        min_profundidad = float(row[12])

                                    inventario = "Rodante"
                                    fecha_de_entrada_inventario = None
                                    try:
                                        fecha_de_entrada_inventario = functions.convertir_fecha3(row[18])
                                    except:
                                        fecha_de_entrada_inventario = None
                                    km_montado = row[13]
                                    if km_montado == "":
                                        km_montado = None
                                    else:
                                        km_montado = int(float(row[13]))

                                    Llanta.objects.create(numero_economico=numero_economico,
                                                        compania=company,
                                                        vehiculo=vehiculo,
                                                        ubicacion=vehiculo.ubicacion,
                                                        aplicacion=aplicacion,
                                                        vida=vida,
                                                        tipo_de_eje=tipo_de_eje,
                                                        eje=eje,
                                                        posicion=posicion,
                                                        nombre_de_eje=nombre_de_eje,
                                                        presion_actual=presion_actual,
                                                        profundidad_izquierda=min_profundidad,
                                                        producto=producto,
                                                        inventario=inventario,
                                                        fecha_de_entrada_inventario=fecha_de_entrada_inventario,
                                                        km_montado=km_montado,
                                                        tirecheck=True
                                                        )
                                except:
                                    pass
                except:
                    pass

            local_file.close()
            local_read_file.close()
            os.remove(os.path.abspath(file_name))"""

    """for file_name, i in entries:
        file_type2 = file_name[0:13]

        if file_type2 == f"ScrappedTires":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_read_file = open(file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(local_read_file, delimiter=",")

            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_file.close()

            with open(file_name, 'r', encoding="utf-8-sig", newline='') as local_read_file:

                reader = csv.reader(local_read_file)
                for row in reader:
                    try:
                        if file_type2 == f"ScrappedTires":
                            company = row[0]
                            if company == "TRAMO DEL CENTRO" or company == "TRAMO":
                                if company == "TRAMO DEL CENTRO" or company == "TRAMO":
                                    company = Compania.objects.get(compania="Tramo")
                                    usuario = Perfil.objects.get(user=User.objects.get(username="Tramo"))
                                numero_economico = row[4]
                                try:
                                    llanta = Llanta.objects.get(numero_economico=numero_economico, compania=company)
                                    vehiculo = Vehiculo.objects.get(numero_economico=row[14], compania=company)
                                    vida = row[13]
                                    if vida == "New":
                                        vida = "Nueva"
                                    elif vida == "1st Retread":
                                        vida = "1R"
                                    elif vida == "2st Retread":
                                        vida = "2R"
                                    elif vida == "3st Retread":
                                        vida = "3R"
                                    elif vida == "4st Retread":
                                        vida = "4R"
                                    elif vida == "Retread":
                                        vida = "1R"

                                    producto = row[5]
                                    producto = Producto.objects.get(producto=producto, compania=company)

                                    try:
                                        aplicacion = Aplicacion.objects.get(nombre=row[2], compania=company)
                                    except:
                                        aplicacion = Aplicacion.objects.create(nombre=row[2], compania=company)

                                    inventario = "Desecho final"
                                    
                                    fecha_de_entrada_inventario = None
                                    try:
                                        fecha_de_entrada_inventario = functions.convertir_fecha3(row[8])
                                    except:
                                        fecha_de_entrada_inventario = None

                                    min_profundidad = row[9]
                                    try:
                                        min_profundidad = float(row[9])
                                    except:
                                        min_profundidad = None

                                    condicion = row[6]
                                    razon = row[7]
                                    try:
                                        desecho = Desecho.objects.get(compania=company,
                                                                    condicion=condicion,
                                                                    razon=razon
                                        )
                                    except:
                                        desecho = Desecho.objects.create(compania=company,
                                                                    condicion=condicion,
                                                                    razon=razon
                                        )

                                    llanta.numero_economico=numero_economico
                                    llanta.compania=company
                                    llanta.vehiculo=vehiculo
                                    llanta.ubicacion=vehiculo.ubicacion
                                    llanta.aplicacion=aplicacion
                                    llanta.vida=vida
                                    llanta.producto=producto
                                    llanta.profundidad_izquierda=min_profundidad
                                    llanta.inventario=inventario
                                    llanta.fecha_de_entrada_inventario=fecha_de_entrada_inventario
                                    llanta.desecho=desecho
                                    llanta.tirecheck=True
                                    llanta.save()
                                except:
                                    vehiculo = Vehiculo.objects.get(numero_economico=row[14], compania=company)
                                    vida = row[13]
                                    if vida == "New":
                                        vida = "Nueva"
                                    elif vida == "1st Retread":
                                        vida = "1R"
                                    elif vida == "2st Retread":
                                        vida = "2R"
                                    elif vida == "3st Retread":
                                        vida = "3R"
                                    elif vida == "4st Retread":
                                        vida = "4R"
                                    elif vida == "Retread":
                                        vida = "1R"

                                    producto = row[5]
                                    producto = Producto.objects.get(producto=producto, compania=company)

                                    try:
                                        aplicacion = Aplicacion.objects.get(nombre=row[2], compania=company)
                                    except:
                                        aplicacion = Aplicacion.objects.create(nombre=row[2], compania=company)

                                    inventario = "Desecho final"
                                    
                                    fecha_de_entrada_inventario = None
                                    try:
                                        fecha_de_entrada_inventario = functions.convertir_fecha3(row[8])
                                    except:
                                        fecha_de_entrada_inventario = None

                                    min_profundidad = row[9]
                                    try:
                                        min_profundidad = float(row[9])
                                    except:
                                        min_profundidad = None

                                    condicion = row[6]
                                    razon = row[7]
                                    try:
                                        desecho = Desecho.objects.get(compania=company,
                                                                    condicion=condicion,
                                                                    razon=razon
                                        )
                                    except:
                                        desecho = Desecho.objects.create(compania=company,
                                                                    condicion=condicion,
                                                                    razon=razon
                                        )
                                    
                                    Llanta.objects.create(numero_economico=numero_economico,
                                                        compania=company,
                                                        vehiculo=vehiculo,
                                                        ubicacion=vehiculo.ubicacion,
                                                        aplicacion=aplicacion,
                                                        vida=vida,
                                                        producto=producto,
                                                        profundidad_izquierda=min_profundidad,
                                                        inventario=inventario,
                                                        fecha_de_entrada_inventario=fecha_de_entrada_inventario,
                                                        desecho=desecho,
                                                        tirecheck=True
                                                        )
                    except:
                        pass

            local_read_file.close()
            os.remove(os.path.abspath(file_name))"""

    """for file_name, i in entries:
        file_type2 = file_name[0:15]

        if file_type2 == f"Stock{year}_{month}_{day}":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_read_file = open(file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(local_read_file, delimiter=",")
            for row in reader:
                try:
                    if file_type2 == f"Stock{year}_{month}_{day}":
                        company = row[1]
                        if company == "TRAMO DEL CENTRO":
                            if company == "TRAMO DEL CENTRO":
                                company = Compania.objects.get(compania="Tramo")
                                usuario = Perfil.objects.get(user=User.objects.get(username="Tramo"))

                            numero_economico = row[7]
                            try:
                                llanta = Llanta.objects.get(numero_economico=numero_economico, compania=company)
                                vehiculo = Vehiculo.objects.get(numero_economico=row[17], compania=company)
                                vida = row[14]
                                if vida == "New":
                                    vida = "Nueva"
                                elif vida == "1st Retread":
                                    vida = "1R"
                                elif vida == "2st Retread":
                                    vida = "2R"
                                elif vida == "3st Retread":
                                    vida = "3R"
                                elif vida == "4st Retread":
                                    vida = "4R"
                                elif vida == "Retread":
                                    vida = "1R"

                                producto = row[8]
                                producto = Producto.objects.get(producto=producto, compania=company)

                                try:
                                    aplicacion = Aplicacion.objects.get(nombre=row[4], compania=company)
                                except:
                                    aplicacion = Aplicacion.objects.create(nombre=row[4], compania=company)

                                presion_actual = row[9]
                                if presion_actual == "":
                                    presion_actual = None
                                else:
                                    presion_actual = int(float(row[9]) * 14.5038)

                                min_profundidad = row[10]
                                if min_profundidad == "":
                                    min_profundidad = None
                                else:
                                    min_profundidad = float(row[10])

                                inventario = row[5]
                                if inventario == "RollingStock":
                                    inventario = "Rodante"
                                elif inventario == "ForRetread":
                                    inventario = "Antes de Renovar"
                                elif inventario == "StagingArea":
                                    inventario = "Nueva"
                                elif inventario == "InspectionArea":
                                    inventario = "Con renovador"
                                elif inventario == "ForScrapStock":
                                    inventario = "Antes de Desechar"
                                elif inventario == "ScrappedSTock":
                                    inventario = "Desecho final"
                                elif inventario == "FleetStock":
                                    inventario = "Renovada"
                                elif inventario == "ForServiceStock":
                                    inventario = "Servicio"
                                else:
                                    inventario = None
                                
                                fecha_de_entrada_inventario = None
                                try:
                                    fecha_de_entrada_inventario = functions.convertir_fecha3(row[16])
                                except:
                                    fecha_de_entrada_inventario = None
                                
                                try:
                                    km_montado = int(float(row[12]))
                                except:
                                    km_montado = None

                                llanta.numero_economico=numero_economico
                                llanta.compania=company
                                llanta.vehiculo=vehiculo
                                llanta.ubicacion=vehiculo.ubicacion
                                llanta.aplicacion=aplicacion
                                llanta.vida=vida
                                llanta.presion_actual=presion_actual
                                llanta.profundidad_izquierda=min_profundidad
                                llanta.producto=producto
                                llanta.inventario=inventario
                                llanta.fecha_de_entrada_inventario=fecha_de_entrada_inventario
                                llanta.km_montado=km_montado
                                llanta.tirecheck=True
                                llanta.save()

                            except:
                                vehiculo = Vehiculo.objects.get(numero_economico=row[17], compania=company)
                                vida = row[14]
                                if vida == "New":
                                    vida = "Nueva"
                                elif vida == "1st Retread":
                                    vida = "1R"
                                elif vida == "2st Retread":
                                    vida = "2R"
                                elif vida == "3st Retread":
                                    vida = "3R"
                                elif vida == "4st Retread":
                                    vida = "4R"
                                elif vida == "Retread":
                                    vida = "1R"

                                producto = row[8]
                                producto = Producto.objects.get(producto=producto, compania=company)

                                try:
                                    aplicacion = Aplicacion.objects.get(nombre=row[4], compania=company)
                                except:
                                    aplicacion = Aplicacion.objects.create(nombre=row[4], compania=company)

                                presion_actual = row[9]
                                if presion_actual == "":
                                    presion_actual = None
                                else:
                                    presion_actual = int(float(row[9]) * 14.5038)

                                min_profundidad = row[10]
                                if min_profundidad == "":
                                    min_profundidad = None
                                else:
                                    min_profundidad = float(row[10])

                                inventario = row[5]
                                if inventario == "RollingStock":
                                    inventario = "Rodante"
                                elif inventario == "ForRetread":
                                    inventario = "Antes de Renovar"
                                elif inventario == "StagingArea":
                                    inventario = "Nueva"
                                elif inventario == "InspectionArea":
                                    inventario = "Con renovador"
                                elif inventario == "ForScrapStock":
                                    inventario = "Antes de Desechar"
                                elif inventario == "ScrappedSTock":
                                    inventario = "Desecho final"
                                elif inventario == "FleetStock":
                                    inventario = "Renovada"
                                elif inventario == "ForServiceStock":
                                    inventario = "Servicio"
                                else:
                                    inventario = None
                                
                                fecha_de_entrada_inventario = None
                                try:
                                    fecha_de_entrada_inventario = functions.convertir_fecha3(row[16])
                                except:
                                    fecha_de_entrada_inventario = None
                                
                                try:
                                    km_montado = int(float(row[12]))
                                except:
                                    km_montado = None
                                Llanta.objects.create(numero_economico=numero_economico,
                                                    compania=company,
                                                    vehiculo=vehiculo,
                                                    ubicacion=vehiculo.ubicacion,
                                                    aplicacion=aplicacion,
                                                    vida=vida,
                                                    presion_actual=presion_actual,
                                                    profundidad_izquierda=min_profundidad,
                                                    producto=producto,
                                                    inventario=inventario,
                                                    fecha_de_entrada_inventario=fecha_de_entrada_inventario,
                                                    km_montado=km_montado,
                                                    tirecheck=True
                                                    )
                except:
                    pass
            local_file.close()
            local_read_file.close()
            os.remove(os.path.abspath(file_name))"""

    """for file_name, i in entries:
        file_type6 = file_name[0:11]

        if file_type6 == f"Inspections" and file_name != "Inspections_Bulk_01142022.csv" and file_name != "Inspections.csv":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_file.close()

            with open(file_name, 'r', encoding="utf-8-sig", newline='') as local_read_file:

                reader = csv.reader(local_read_file)

                for row in reader:
                    try:
                        if file_type6 == f"Inspections" and file_name != "Inspections_Bulk_01142022.csv" and file_name != "Inspections.csv":
                            company = row[1]
                            if company == "TRAMO DEL CENTRO":
                                if company == "TRAMO DEL CENTRO":
                                    company = Compania.objects.get(compania="Tramo")
                                    usuario = Perfil.objects.get(user=User.objects.get(username="Tramo"))

                                llanta = row[12]

                                try:
                                    llanta_hecha = Llanta.objects.get(numero_economico=llanta, compania=company)
                                except:
                                    llanta_hecha = None
                                if llanta_hecha:
                                    fecha_hora = row[4]
                                    try:
                                        fecha_hora = functions.convertir_fecha4(fecha_hora)
                                    except:
                                        fecha_hora = functions.convertir_fecha2(fecha_hora)
                                    try:
                                        km = int(float(row[6]))
                                    except:
                                        km = None

                                    try:
                                        presion = float(row[21])
                                        presion = int(presion * 14.5038)
                                    except:
                                        presion = None

                                    if llanta_hecha.eje == 1:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_1
                                    elif llanta_hecha.eje == 2:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_2
                                    elif llanta_hecha.eje == 3:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_3
                                    elif llanta_hecha.eje == 4:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_4
                                    elif llanta_hecha.eje == 5:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_5
                                    elif llanta_hecha.eje == 6:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_6
                                    elif llanta_hecha.eje == 7:
                                        presion_establecida = llanta_hecha.vehiculo.presion_establecida_7


                                    try:
                                        profundidad_izquierda = float(row[18])
                                    except:
                                        profundidad_izquierda = 10000

                                    try:
                                        profundidad_central = float(row[19])
                                    except:
                                        profundidad_central = 10000

                                    try:
                                        profundidad_derecha = float(row[20])
                                    except:
                                        profundidad_derecha = 10000

                                    min_profundidad = [profundidad_izquierda, profundidad_central, profundidad_derecha]
                                    min_profundidad = min(min_profundidad)

                                    inspeccion_creada = Inspeccion.objects.create(tipo_de_evento="Inspección",
                                                            llanta=llanta_hecha,
                                                            usuario=usuario,
                                                            vehiculo=llanta_hecha.vehiculo,
                                                            fecha_hora=fecha_hora,
                                                            vida=llanta_hecha.vida,
                                                            km_vehiculo=km,
                                                            presion=presion,
                                                            presion_establecida=presion_establecida,
                                                            profundidad_izquierda=min_profundidad,
                                                            evento = str({\
                                                            "llanta_inicial" : llanta_hecha, "llanta_mod" : "",\
                                                            "producto_inicial" : llanta_hecha.producto, "producto_mod" : "",\
                                                            "vida_inicial" : llanta_hecha.vida, "vida_mod" : "",\
                                                            "km_inicial" : km, "km_mod" : "",\
                                                            "presion_inicial" : presion, "presion_mod" : "",\
                                                            "profundidad_izquierda_inicial" : min_profundidad, "profundidad_izquierda_mod" : "",\
                                                            "profundidad_central_inicial" : "", "profundidad_central_mod" : "",\
                                                            "profundidad_derecha_inicial" : "", "profundidad_derecha_mod" : ""\
                                                            })
                                    )
                                    if llanta_hecha:
                                        llanta_hecha.profundidad_izquierda = min_profundidad
                                        if (llanta_hecha.km_montado or llanta_hecha.km_montado == 0) and km:
                                            if llanta_hecha.km_montado <= km:
                                                llanta_hecha.km_actual = km - llanta_hecha.km_montado
                                                print("km_montado1", llanta_hecha.km_montado)
                                            else:
                                                llanta_hecha.km_actual = None
                                        elif km:
                                            inspecciones_llanta = Inspeccion.objects.filter(llanta=llanta_hecha)
                                            km_actual = functions.km_actual(inspecciones_llanta)
                                            print("inspecciones_llanta", inspecciones_llanta)
                                            print("km_montado2", km_actual)
                                            if km_actual:
                                                llanta_hecha.km_actual = km_actual
                                            else:
                                                llanta_hecha.km_actual = None
                                        else:
                                            llanta_hecha.km_actual = None
                                        llanta_hecha.save()
                                    try:
                                        vehiculo = Vehiculo.objects.get(numero_economico=llanta_hecha.vehiculo.numero_economico)
                                        vehiculo.ultima_inspeccion = inspeccion_creada
                                        vehiculo.save()
                                    except:
                                        pass
                    except:
                        pass

                local_read_file.close()
                os.remove(os.path.abspath(file_name))"""

    ftp1.quit()

def ftp_descarga2():
    hoy = date(2022, 4, 12)
    year = hoy.year
    month = hoy.month
    day = hoy.day
    if month < 10:
        month = f"0{month}"
    if day < 10:
        day = f"0{day}"
    ftp1 = fileTP("208.109.20.121")
    ftp1.login(user="tyrecheck@aeto.com", passwd="TyreDB!25")
    file_write = open("Scrapped.csv", "w", encoding="utf-8-sig", newline='')
    writer = csv.writer(file_write, delimiter=",")
    for file_name in ftp1.nlst():
        file_type6 = file_name[0:13]

        if file_type6 == f"ScrappedTires" or file_name == "ScrappedTires_Bulk.csv":
            print(file_name)
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            local_file.close()
            file = open(file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(file, delimiter=",")
            
            for row in reader:
                try:
                    company = row[0]
                    if company == "NEW PICK SA DE CV" or company == "CSI" or company == "MPV360" or company == "SOLAQRO" or company == "TRAMO DEL CENTRO":
                        writer.writerow(row)
                except:
                    pass

            file.close()
            os.remove(os.path.abspath(file_name))
    
    file_write.close()

def ftp1():

    DIR = "D:/aetoweb/"
    DIR_PATH = os.listdir(DIR)
    ftp2 = fileTP("208.109.20.121")
    ftp2.login(user="tdr@aeto.com", passwd="486dbintegracion!")
    for FILE_PATH in DIR_PATH:
        print(FILE_PATH)
        file_type1 = FILE_PATH[0:10]
        file_type2 = FILE_PATH[0:7]
        file_type3 = FILE_PATH[0:10]
        file_type4 = FILE_PATH[0:15]
        file_type5 = FILE_PATH[0:14]
        file_type6 = FILE_PATH[0:13]
        file_type7 = FILE_PATH[0:8]
        #if file_type1 == "Vehicles20" or file_type2 == "Stock20" or file_type3 == "Services20" or file_type4 == "ScrappedTires20" or file_type5 == "RollingStock20" or file_type6 == "Inspections20" or file_type7 == "Casing20":
        if file_type4 == "ScrappedTires20" or file_type6 == "Inspections20":
            file = open(DIR + FILE_PATH, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(file, delimiter=",")
            file_write = open("TDR_" + FILE_PATH, "w", encoding="utf-8-sig", newline='')
            writer = csv.writer(file_write, delimiter=",")

            csv_dict_reader = csv.DictReader(file)
            column_names = csv_dict_reader.fieldnames
            writer.writerow(column_names)

            for row in reader:
                try:
                    if file_type1 == "Vehicles20":
                        company = row[3]
                    elif file_type2 == "Stock20":
                        company = row[1]
                    elif file_type3 == "Services20":
                        company = row[1]
                    elif file_type4 == "ScrappedTires20":
                        company = row[0]
                    elif file_type5 == "RollingStock20":
                        company = row[1]
                    elif file_type6 == "Inspections20":
                        company = row[1]
                    elif file_type7 == "Casing20":
                        company = row[8]
                except:
                    break
                if company == "MPV360":
                    writer.writerow(row)

            file.close()
            file_write.close()

            file_read = open("TDR_" + FILE_PATH, "rb")

            ftp2.storbinary('STOR ' + "TDR_" + FILE_PATH, file_read)
            file_read.close()
            os.remove(os.path.abspath("TDR_" + FILE_PATH))

            os.remove(os.path.abspath(FILE_PATH))
    ftp2.quit()

def ftp2(user):

    DIR = "D:/Aetoweb/aeto/"
    ftp1 = fileTP("208.109.20.121")
    ftp1.login(user="tyrecheck@aeto.com", passwd="TyreDB!25")
    for file_name in ftp1.nlst():
        file_type1 = file_name[0:10]
        file_type2 = file_name[0:7]
        file_type3 = file_name[0:10]
        file_type4 = file_name[0:15]
        file_type5 = file_name[0:14]
        file_type6 = file_name[0:13]
        file_type7 = file_name[0:8]
        if file_type1 == "Vehicles20" or file_type2 == "Stock20" or file_type3 == "Services20" or file_type4 == "ScrappedTires20" or file_type5 == "RollingStock20" or file_type6 == "Inspections20" or file_type7 == "Casing20":
            local_file = open(file_name, "wb")
            ftp1.retrbinary("RETR " + file_name, local_file.write)
            file = open(DIR + file_name, "r", encoding="utf-8-sig", newline='')
            reader = csv.reader(file, delimiter=",")
            if file_type1 == "Vehicles20":
                for row in reader:
                    compania = row[3]
                    if compania == "MPV360":
                        company = Compania.objects.get(compania="TDR")
                        ubicacion = Ubicacion.objects.create(nombre=row[5], compania=company)
                        aplicacion = Aplicacion.objects.create(nombre=row[7], compania=company)
                        vehiculo = Vehiculo.objects.create(numero_economico=row[9],
                                                        modelo=row[18],
                                                        marca=row[16],
                                                        compania=company,
                                                        ubicacion=ubicacion,
                                                        aplicacion=aplicacion,
                                                        numero_de_llantas = functions.cantidad_llantas(row[14]),
                                                        clase = row[12],
                                                        configuracion = row[14]
                                                        )
            """if file_type1 == "Stock20":
                for row in reader:
                    compania = row[1]
                    if compania == "MPV360":
                        llanta = Llanta.objects.create()
                        llanta.numero_economico = row[7]
                        llanta.usuario = Perfil.objects.get(user=user)
                        llanta.vehiculo = row[18]
                        vida = row[14]
                        if vida == "New":
                            vida = "Nueva"
                        elif vida == "1st Retread":
                            vida = "1R"
                        elif vida == "2st Retread":
                            vida = "2R"
                        elif vida == "3st Retread":
                            vida = "3R"
                        elif vida == "Retread":
                            vida = "4R"

                        llanta.vida = vida
                        producto = Producto.objects.create(producto=row[8])
                        llanta.producto = producto
                        llanta.modelo = row[18]
                        llanta.marca = row[16]
                        llanta.compania = row[3]
                        llanta.ubicacion = row[5]
                        llanta.aplicacion = row[7]
                        llanta.numero_de_llantas = functions.cantidad_llantas(row[14])
                        llanta.clase = row[12]
                        llanta.configuracion = row[14]
                        llanta.save()"""
            file.close()
            local_file.close()
            os.remove(os.path.abspath(file_name))

    ftp1.quit()



    """if file_type1 == "Vehicles20" or file_type2 == "Stock20" or file_type3 == "Services20" or file_type4 == "ScrappedTires20" or file_type5 == "RollingStock20" or file_type6 == "Inspections20" or file_type7 == "Casing20":
        file = open(DIR + FILE_PATH, "r", encoding="utf-8-sig", newline='')
        reader = csv.reader(file, delimiter=",")
        file_write = open("TDR_" + FILE_PATH, "w", encoding="utf-8-sig", newline='')
        writer = csv.writer(file_write, delimiter=",")

        csv_dict_reader = csv.DictReader(file)
        column_names = csv_dict_reader.fieldnames
        writer.writerow(column_names)


        for row in reader:
            try:
                if file_type1 == "Vehicles20":
                    company = row[3]
                elif file_type2 == "Stock20":
                    company = row[1]
                elif file_type3 == "Services20":
                    company = row[1]
                elif file_type4 == "ScrappedTires20":
                    company = row[0]
                elif file_type5 == "RollingStock20":
                    company = row[1]
                elif file_type6 == "Inspections20":
                    company = row[1]
                elif file_type7 == "Casing20":
                    company = row[8]
            except:
                break
            if company == "MPV360":
                writer.writerow(row)



        file.close()
        file_write.close()

        file_read = open("TDR_" + FILE_PATH, "rb")

        ftp2.storbinary('STOR ' + "TDR_" + FILE_PATH, file_read)
        file_read.close()
        os.remove(os.path.abspath("TDR_" + FILE_PATH))

        os.remove(os.path.abspath(FILE_PATH))
    ftp2.quit()"""

