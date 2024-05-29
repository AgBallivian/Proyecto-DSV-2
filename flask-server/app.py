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


#Front end
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crear_formulario', methods=['GET', 'POST'])
def crear_formulario():
    if request.method == 'POST':
        # Lógica para procesar el formulario enviado
        pass
    return render_template('crear_formulario.html')

@app.route('/ver_formularios')
def ver_formularios():
    # Obtener la lista de formularios desde la base de datos
    formularios = [...] # Consulta a la base de datos
    return render_template('ver_formularios.html', formularios=formularios)

@app.route('/ver_multipropietarios')
def ver_multipropietarios():
    # Obtener la lista de multipropietarios desde la base de datos
    multipropietarios = [...] 
    return render_template('ver_multipropietarios.html', multipropietarios=multipropietarios)

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

    finally:
        connection.close()
@app.route('/show_multipropietarios', methods=['GET'])
def show_multipropietarios():
    connection = get_db_connection()
    filters = {}

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
    formulario.determinar_y_procesar_escenario()
    formulario.ajustar_porcentajes_adquirentes()
    return jsonify({"message": "Formulario submitted successfully"})
if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')