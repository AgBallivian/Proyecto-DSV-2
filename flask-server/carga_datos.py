import os
import csv


def cargar_regiones():
    regiones = {}
    ruta_archivo = os.path.join(os.path.dirname(__file__), 'csv', 'regiones.csv')
    with open(ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
        lector = csv.reader(archivo, delimiter=';')
        encabezados = next(lector)  # Obtener los encabezados de la primera fila
        for fila in lector:
            id_region = int(fila[encabezados.index('id_region')])
            descripcion = fila[encabezados.index('descripcion')]
            regiones[id_region] = descripcion
    print(regiones)
    return regiones

def cargar_comunas():
    comunas = {}
    ruta_archivo = os.path.join(os.path.dirname(__file__), 'csv', 'comunas.csv')
    with open(ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
        lector = csv.reader(archivo, delimiter=';')
        encabezados = next(lector)  
        for fila in lector:
            id_comuna = int(fila[encabezados.index('id_comuna')])
            id_region = int(fila[encabezados.index('id_region')])
            descripcion = fila[encabezados.index('descripcion')]

            comunas[id_comuna] = {
                'descripcion': descripcion,
                'id_region': id_region
            }
    return comunas