from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import json
import pymysql
from algoritmo import form_solver
from collections import defaultdict
from config import Config 

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
    if request.method == 'POST':
        cne = request.form['cne']
        comuna = request.form['comuna']
        manzana = request.form['manzana']
        predio = request.form['predio']
        fojas = request.form['fojas']
        fecha_inscripcion = request.form['fecha_inscripcion']
        numero_inscripcion = request.form['numero_inscripcion']

        enajenantes_data = []
        adquirentes_data = []

        for key, value in request.form.lists():
            if key.startswith('enajenantes'):
                index = int(key.split('[')[1].split(']')[0])
                field = key.split('[')[2].split(']')[0]
                
                if len(enajenantes_data) <= index:
                    enajenantes_data.append({'RUNRUT': None, 'porcDerecho': None})
                
                if field == 'RUNRUT':
                    enajenantes_data[index]['RUNRUT'] = value[0]
                elif field == 'porcDerecho':
                    enajenantes_data[index]['porcDerecho'] = value[0]
            
            elif key.startswith('adquirentes'):
                index = int(key.split('[')[1].split(']')[0])
                field = key.split('[')[2].split(']')[0]
                
                if len(adquirentes_data) <= index:
                    adquirentes_data.append({'RUNRUT': None, 'porcDerecho': None})
                
                if field == 'RUNRUT':
                    adquirentes_data[index]['RUNRUT'] = value[0]
                elif field == 'porcDerecho':
                    adquirentes_data[index]['porcDerecho'] = value[0]
        
        data = {
            'CNE': cne,
            'bienRaiz': {
                'comuna': comuna,
                'manzana': manzana,
                'predio': predio
            },
            'enajenantes': enajenantes_data,
            'adquirentes': adquirentes_data,
            'fojas': fojas,
            'fechaInscripcion': fecha_inscripcion,
            'nroInscripcion': numero_inscripcion
        }

        # print(data)
        formulario = form_solver(data, obtener_conexion_db)
        numero_de_atencion = formulario.add_formulario()
        formulario.determinar_y_procesar_escenario()
        formulario.ajustar_porcentajes_adquirentes()
        formulario.add_enajenante(numero_de_atencion)
        formulario.add_adquirente(numero_de_atencion)
        formulario.add_multipropietario()
        
        if numero_de_atencion:
            return redirect(url_for('ver_formulario', id=numero_de_atencion))
        else:
            return render_template('error.html', mensaje="Error al procesar el formulario.")

    return render_template('crear_formulario.html')


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
                print(datos)
                try:
                    formulario = form_solver(datos, obtener_conexion_db)
                    numero_de_atencion = formulario.add_formulario()
                    formulario.determinar_y_procesar_escenario()
                    formulario.ajustar_porcentajes_adquirentes()
                    formulario.add_enajenante(numero_de_atencion)
                    formulario.add_adquirente(numero_de_atencion)
                    formulario.add_multipropietario()
                except Exception as e:
                    errores.append(str(e))

            if errores:
                return render_template('subir_json.html', errores=errores)
            else:
                return render_template('ver_todos_formularios.html')

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
    connection = obtener_conexion_db()
    try:
        with connection.cursor() as cursor:
            multipropietarios_sql = "SELECT * FROM Multipropietarios"
            cursor.execute(multipropietarios_sql)
            multipropietarios = cursor.fetchall()
        return render_template('ver_todos_multipropietarios.html', multipropietarios=multipropietarios)
    finally:
        connection.close()

@app.route('/ver_multipropietario/<int:id>', methods=['GET'])
def ver_multipropietario(id):
    connection = obtener_conexion_db()
    try:
        with connection.cursor() as cursor:
            multipropietario_sql = "SELECT * FROM Multipropietarios WHERE id = %s"
            cursor.execute(multipropietario_sql, (id,))
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

    formulario_sql = f"SELECT * FROM formulario{search_filters}"
    try:
        with connection.cursor() as cursor:
            cursor.execute(formulario_sql)
            formularios = cursor.fetchall()
            return formularios
    finally:
        connection.close()

def obtener_formulario(id):
    connection = obtener_conexion_db()
    formulario_sql = f"SELECT * FROM formulario WHERE Numero_de_atencion = {id}"
    try:
        with connection.cursor() as cursor:
            cursor.execute(formulario_sql)
            formulario = cursor.fetchone()
            return formulario
    finally:
        connection.close()

def obtener_enajenantes(id):
    connection = obtener_conexion_db()
    enajenantes_sql = f"SELECT RUNRUT, porcDerecho FROM Enajenantes WHERE enajenante_id = {id}"
    try:
        with connection.cursor() as cursor:
            cursor.execute(enajenantes_sql)
            enajenantes = cursor.fetchall()
            return enajenantes
    finally:
        connection.close()

def obtener_adquirentes(id):
    connection = obtener_conexion_db()
    adquirentes_sql = f"SELECT RUNRUT, porcDerecho FROM Adquirentes WHERE Adquirente_id = {id}"
    try:
        with connection.cursor() as cursor:
            cursor.execute(adquirentes_sql)
            adquirentes = cursor.fetchall()
            return adquirentes
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')