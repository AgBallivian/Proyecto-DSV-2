from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import json
import pymysql
from algoritmo import form_solver

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4321"]}})

#Configuracion
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'proyectodsv'
app.config['CORS_HEADERS'] = 'Content-Type'

def get_db_connection():
    connection = pymysql.connect(host=app.config['MYSQL_HOST'],
                                 user=app.config['MYSQL_USER'],
                                 password=app.config['MYSQL_PASSWORD'],
                                 db=app.config['MYSQL_DB'],
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


@app.route('/show_formularios', methods=['GET'])
def show_formularios():
    connection = get_db_connection()
    filters = {}
    filters["CNE"] = request.args.get('CNE')
    filters["Comuna"] = request.args.get('Comuna')
    filters["Manzana"] = request.args.get('Manzana')
    filters["Predio"] = request.args.get('Predio')
    search_filters = ""
    if(any(v != None for v in list(filters.values()))):
        search_filters = " WHERE "
        for key in filters.keys():
            if(filters[key] != None):
                search_filters += key + " = " + filters[key] + " AND "

    try:
        with connection.cursor() as cursor:
            formulario_sql = "SELECT * FROM formulario" + search_filters[0:-4]
            cursor.execute(formulario_sql)
            formularios = cursor.fetchall()
            formularios= json.dumps(formularios, default=str)
            print(formularios)
        return formularios
        # return render_template('index.html', formularios=formularios)

    finally:
        connection.close()


@app.route('/show_formulario', methods=['GET'])
def show_formulario():
    connection = get_db_connection()
    id  = request.args.get('id')
    try:
        with connection.cursor() as cursor:
            # Obtener los datos de la tabla 'formulario'
            formulario_sql = "SELECT * FROM formulario WHERE Numero_de_atencion = " + str(id)
            cursor.execute(formulario_sql)
            formulario = cursor.fetchall()
            adquirentes_sql = "SELECT * FROM Adquirentes WHERE Adquirente_id = " + str(id)
            cursor.execute(adquirentes_sql)
            adquirentes = cursor.fetchall()
            enajenantes_sql = "SELECT * FROM Enajenantes WHERE Enajenante_id = " + str(id)
            cursor.execute(enajenantes_sql)
            enajenantes = cursor.fetchall()
            formulario[0]["enajenantes"] = enajenantes
            formulario[0]["adquirentes"] = adquirentes
            formulario= json.dumps(formulario, default=str)
            print(formulario)
            
        return formulario
        # return render_template('show_form.html', formulario=formulario, enajenantes=enajenantes, adquirentes=adquirentes)

    finally:
        connection.close()
@app.route('/show_multipropietarios', methods=['GET'])
def show_multipropietarios():
    connection = get_db_connection()
    filters = {}
    # if(not request.args.get('com_man_pred'))
    if(request.args.get('com_man_pred')):
        filters["com_man_pred"] = '\'' + request.args.get('com_man_pred') + '\''
    else:
        filters["com_man_pred"] = request.args.get('com_man_pred')
    filters["RUNRUT"] = request.args.get('RUNRUT')
    filters["Fojas"] = request.args.get('Fojas')
    search_filters = ""
    if(any(v != None for v in list(filters.values()))):
        search_filters = " WHERE "
        for key in filters.keys():
            if(filters[key] != None):
                search_filters += key + " = " + filters[key] + " AND "

    try:
        with connection.cursor() as cursor:
            # Obtener los datos de la tabla 'multipropietarios'
            multipropietarios_sql = "SELECT * FROM Multipropietarios"  + search_filters[0:-4]
            cursor.execute(multipropietarios_sql)
            multipropietarios = cursor.fetchall()
            multipropietarios= json.dumps(multipropietarios, default=str)
            print(multipropietarios)
        return multipropietarios
        # return render_template('show_multis.html', multipropietarios=multipropietarios)

    finally:
        connection.close()

@app.route('/show_multipropietario', methods=['GET'])
def show_multipropietario():
    connection = get_db_connection()
    id  = request.args.get('id')
    try:
        with connection.cursor() as cursor:
            # Obtener los datos de la tabla 'multipropietario'
            multipropietario_sql = "SELECT * FROM Multipropietarios WHERE com_man_pred = " + '\''+ id +'\''
            cursor.execute(multipropietario_sql)
            multipropietario = cursor.fetchall()
            multipropietario= json.dumps(multipropietario, default=str)
        return multipropietario
        # return render_template('show_multi.html', multipropietario=multipropietario)

    finally:
        connection.close()

@app.route('/add_formulario', methods=['POST'])
def add_formulario():
    data = request.get_json()
    print(f"Data recieved: {data['CNE']}")
    
    # Extract the form data from the JSON object
    cne = data['CNE']
    comuna = data['bienRaiz']['comuna']
    manzana = data['bienRaiz']['manzana']
    predio = data['bienRaiz']['predio']
    fojas = data['fojas']
    fecha_inscripcion = data['fechaInscripcion']
    numero_inscripcion = data['nroInscripcion']

    # Extract enajenantes and adquirentes data from the JSON object
    try:
        enajenantes_data = data['enajenantes']
    except:
        enajenantes_data = []
    try:
        adquirentes_data = data['adquirentes']
    except:
        adquirentes_data = []
    formulario = form_solver(data, get_db_connection)
    formulario.nivel_0()
    formulario.nivel_1()
    return jsonify({"message": "Formulario submitted successfully"})
if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')