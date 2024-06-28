from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import json
import pymysql
from algoritmo import form_solver
from collections import defaultdict
from config import Config
from carga_datos import cargar_regiones, cargar_comunas
from Queries import QUERY_CONNECTOR, QUERY_ALL_FORMULARIOS, QUERY_FORMULARIO_FILTER_ID, QUERY_ALL_MULTIPROPIETARIOS, QUERY_FORMULARIO_FILTER_NUM_ATENCION, QUERY_ENAJENANTES_INFO, QUERY_ADQUIRENTES_INFO
from DBmanager import obtener_transferencias_filtrados, obtener_numer_de_atencion, obtener_multipropietarios_filtrados, agregar_formulario
from Errores import (ERROR_RUT_INVALIDO, ERROR_RUT_VERIFICADOR)

INDEX_ARG = '['
CAMPO_ARG = ']'

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8000"]}})

app.config.from_object(Config)

def obtener_conexion_db():
    connection = pymysql.connect(host=app.config['MYSQL_HOST'],
                                 user=app.config['MYSQL_USER'],
                                 password=app.config['MYSQL_PASSWORD'],
                                 db=app.config['MYSQL_DB'],
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crear_formulario', methods=['GET', 'POST'])
def crear_formulario():
    if request.method != 'POST':
        return render_template('crear_formulario.html')

    try:
        datos_formulario = extraer_datos_formulario(request.form)
        datos = preparar_datos(datos_formulario)
        formulario = procesar_formulario(datos)
        numero_de_atencion = obtener_numer_de_atencion()
        if numero_de_atencion:
            return redirect(url_for('ver_formulario', id=numero_de_atencion))
    except ValueError as e:
        return render_template('crear_formulario.html', error=str(e))
    
    return render_template('error.html', mensaje="Error al procesar el formulario.")

def extraer_datos_formulario(formulario):
    return {
        'cne': formulario['cne'],
        'comuna': formulario['comuna'],
        'manzana': formulario['manzana'],
        'predio': formulario['predio'],
        'fojas': formulario['fojas'],
        'fecha_inscripcion': formulario['fecha_inscripcion'],
        'numero_inscripcion': formulario['numero_inscripcion'],
        'listas_formulario': formulario.lists()
    }

def preparar_datos(datos_formulario):
    # Convertir el generador en una lista
    listas_formulario = list(datos_formulario['listas_formulario'])
    
    datos_enajenantes = procesar_datos_participantes(listas_formulario, 'enajenantes')
    datos_adquirentes = procesar_datos_participantes(listas_formulario, 'adquirentes')
    
    return {
        'CNE': datos_formulario['cne'],
        'bienRaiz': {
            'comuna': datos_formulario['comuna'],
            'manzana': datos_formulario['manzana'],
            'predio': datos_formulario['predio']
        },
        'enajenantes': datos_enajenantes,
        'adquirentes': datos_adquirentes,
        'fojas': datos_formulario['fojas'],
        'fechaInscripcion': datos_formulario['fecha_inscripcion'],
        'nroInscripcion': datos_formulario['numero_inscripcion']
    }

def procesar_datos_participantes(listas_formulario, tipo_participante):
    datos_participante = []
    for clave, valor in listas_formulario:
        if clave.startswith(tipo_participante):
            indice, campo = analizar_clave(clave)
            asegurar_existencia_participante(datos_participante, indice)
            datos_participante[indice][campo] = valor[0]
    
    return datos_participante

def analizar_clave(clave):
    partes = clave.split(INDEX_ARG)
    indice = int(partes[1].split(CAMPO_ARG)[0])
    campo = partes[2].split(CAMPO_ARG)[0]
    return indice, campo

def asegurar_existencia_participante(datos_participante, indice):
    while len(datos_participante) <= indice:
        datos_participante.append({'RUNRUT': None, 'porcDerecho': None})

def procesar_formulario(datos):
    agregar_formulario(datos["CNE"], datos["bienRaiz"]["comuna"], datos["bienRaiz"]["manzana"], datos["bienRaiz"]["predio"], datos["fojas"], datos["fechaInscripcion"], datos["nroInscripcion"])
    formulario = form_solver(datos, obtener_conexion_db)
    formulario.determinar_y_procesar_escenario()
    formulario.ajustar_porcentajes_adquirentes()
    return formulario

@app.route('/subir_json', methods=['GET', 'POST'])
def subir_json():
    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            contenido = archivo.read()
            datos_json = json.loads(contenido)
            result = datos_json.get("F2890", [])
            errores = []
            for datos in result:
                try:
                    procesar_formulario(datos)
                except ValueError as e:
                    errores.append(f"Error en formulario: {str(e)}")
            if errores:
                return render_template('subir_json.html', errores=errores)
            else:
                return redirect(url_for('ver_todos_formularios'))

    return render_template('subir_json.html')


@app.route('/ver_todos_formularios', methods=['GET'])
def ver_todos_formularios():
    filtros = {
        "CNE": request.args.get('CNE'),
        "Comuna": request.args.get('Comuna'),
        "Manzana": request.args.get('Manzana'),
        "Predio": request.args.get('Predio')
    }

    formularios = obtener_formularios(filtros)
    return render_template('ver_todos_formularios.html', formularios=formularios)

@app.route('/ver_formulario/<int:id>', methods=['GET'])
def ver_formulario(id):
    formulario = obtener_formulario(id)
    enajenantes = obtener_enajenantes(id)
    adquirentes = obtener_adquirentes(id)
    return render_template('ver_formulario.html', formulario=formulario, enajenantes=enajenantes, adquirentes=adquirentes)

@app.route('/ver_todos_multipropietarios', methods=['GET'])
def ver_todos_multipropietarios():
    regiones = cargar_regiones()
    comunas = cargar_comunas()

    region_id = request.args.get('region', type=int)
    comuna_id = request.args.get('comuna', type=int)
    block_number = request.args.get('block', type=int)
    property_number = request.args.get('property', type=int)
    year = request.args.get('year', type=int)

    multipropietarios = obtener_multipropietarios_filtrados(region_id, comuna_id, block_number, property_number, year)
    return render_template('ver_todos_multipropietarios.html', multipropietarios=multipropietarios, regiones=regiones, comunas=comunas, region_id=region_id, comuna_id=comuna_id, block_number=block_number, property_number=property_number, year=year)

@app.route('/ver_multipropietarios_filtrados', methods=['GET'])
def ver_multipropietarios_filtrados():
    regiones = cargar_regiones()
    comunas = cargar_comunas()
    id_region = request.args.get('region')
    id_comuna = request.args.get('comuna')
    runrut = request.args.get('runrut')
    fojas = request.args.get('fojas')

    # Construir la consulta SQL con los filtros
    consulta = QUERY_ALL_MULTIPROPIETARIOS
    condiciones = []
    if id_region:
        comunas_filtradas = [id_comuna for id_comuna, datos in comunas.items() if datos['id_region'] == int(id_region)]
        condiciones.append(f"Comuna IN ({','.join(map(str, comunas_filtradas))})")
    if id_comuna:
        condiciones.append(f"Comuna = {id_comuna}")
    if runrut:
        condiciones.append(f"RUNRUT LIKE '%{runrut}%'")
    if fojas:
        condiciones.append(f"Fojas = {fojas}")

    if condiciones:
        consulta += QUERY_CONNECTOR.join(condiciones)

    connection = obtener_conexion_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(consulta)
            multipropietarios = cursor.fetchall()
        return render_template('ver_todos_multipropietarios.html', multipropietarios=multipropietarios, regiones=regiones, comunas=comunas)
    finally:
        connection.close()

@app.route('/ver_multipropietario/<int:id>', methods=['GET'])
def ver_multipropietario(id):
    connection = obtener_conexion_db()
    try:
        with connection.cursor() as cursor:
            # multipropietario_sql = "SELECT * FROM Multipropietarios WHERE id = %s"
            cursor.execute(QUERY_FORMULARIO_FILTER_ID, (id,))
            multipropietario = cursor.fetchone()
        return render_template('ver_multipropietario.html', multipropietario=multipropietario)
    finally:
        connection.close()

def obtener_formularios(filtros):
    connection = obtener_conexion_db()
    search_filters = ""
    if any(v is not None for v in list(filtros.values())):
        search_filters = " WHERE "
        for key in filtros.keys():
            if filtros[key] is not None:
                search_filters += f"{key} = {filtros[key]} AND "
        search_filters = search_filters[:-5]

    try:
        with connection.cursor() as cursor:
            cursor.execute(QUERY_ALL_FORMULARIOS.format(search_filters))
            formularios = cursor.fetchall()
            return formularios
    finally:
        connection.close()

def obtener_formulario(id):
    connection = obtener_conexion_db()
    # formulario_sql = f"SELECT * FROM formulario WHERE Numero_de_atencion = {id}"
    try:
        with connection.cursor() as cursor:
            cursor.execute(QUERY_FORMULARIO_FILTER_NUM_ATENCION, (id,))
            formulario = cursor.fetchone()
            return formulario
    finally:
        connection.close()

def obtener_enajenantes(id):
    connection = obtener_conexion_db()
    # enajenantes_sql = "SELECT RUNRUT, porcDerecho FROM Enajenantes WHERE enajenante_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(QUERY_ENAJENANTES_INFO, (id,))
            enajenantes = cursor.fetchall()
            return enajenantes
    finally:
        connection.close()

def obtener_adquirentes(id):
    connection = obtener_conexion_db()
    # adquirentes_sql = "SELECT RUNRUT, porcDerecho FROM Adquirentes WHERE Adquirente_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(QUERY_ADQUIRENTES_INFO, (id,))
            adquirentes = cursor.fetchall()
            return adquirentes
    finally:
        connection.close()

def validar_runrut(datos):
    for dato in datos:
        if dato["RUNRUT"]:
            runrut_ingresado = dato["RUNRUT"]
            if not validar_formato_runrut(runrut_ingresado):
                raise ValueError(ERROR_RUT_INVALIDO.format(runrut_ingresado))
            if not validar_digito_verificador(runrut_ingresado):
                raise ValueError(ERROR_RUT_VERIFICADOR.format(runrut_ingresado))
    return True

def validar_formato_runrut(runrut):
    return runrut.count("-") == 1

def validar_digito_verificador(runrut):
    digitos_rut, digito_verificador = runrut.split("-")
    suma = calcular_suma_digitos(digitos_rut)
    resto = suma % 11
    verificador = obtener_verificador_runrut(resto)
    return str(verificador) == digito_verificador

def calcular_suma_digitos(digitos_rut):
    suma = 0
    multiplicador = 2
    for digito in reversed(digitos_rut):
        suma += int(digito) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    return suma

def obtener_verificador_runrut(resto):
    if resto == 0:
        return 11
    if resto == 1:
        return "K"
    return 11 - resto

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
    