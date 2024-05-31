from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import json
import pymysql
from algoritmo import form_solver

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4321"]}})

#Configuracion
# app.config['MYSQL_HOST'] = 'db'
# app.config['MYSQL_USER'] = 'root'

#Esto solo es para testeo sin docker.
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'

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

        print(data)
        formulario = form_solver(data, get_db_connection)
        numero_de_atencion = formulario.add_formulario()
        formulario.add_enajenante(numero_de_atencion)
        formulario.add_adquirente(numero_de_atencion)
        formulario.add_multipropietario()
        formulario.determinar_y_procesar_escenario()
        formulario.ajustar_porcentajes_adquirentes()
        
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

            errores = []
            for datos in datos_json:
                try:
                    formulario = form_solver(datos, get_db_connection)
                    formulario.determinar_y_procesar_escenario()
                    formulario.ajustar_porcentajes_adquirentes()
                except Exception as e:
                    errores.append(str(e))

            if errores:
                return render_template('subir_json.html', errores=errores)
            else:
                return render_template('exito.html')

    return render_template('subir_json.html')

@app.route('/ver_formularios', methods=['GET'])
def ver_formularios():
    connection = get_db_connection()
    filters = {}
    filters["CNE"] = request.args.get('CNE')
    filters["Comuna"] = request.args.get('Comuna')
    filters["Manzana"] = request.args.get('Manzana')
    filters["Predio"] = request.args.get('Predio')
    search_filters = ""
    if any(v is not None for v in list(filters.values())):
        search_filters = " WHERE "
        for key in filters.keys():
            if filters[key] is not None:
                search_filters += key + " = " + str(filters[key]) + " AND "
        search_filters = search_filters[:-5] 

    try:
        with connection.cursor() as cursor:
            formulario_sql = "SELECT * FROM formulario" + search_filters
            cursor.execute(formulario_sql)
            formularios = cursor.fetchall()
        return render_template('ver_formularios.html', formularios=formularios)

    finally:
        connection.close()

@app.route('/ver_formulario/<int:id>', methods=['GET'])
def ver_formulario(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            formulario_sql = "SELECT * FROM formulario WHERE Numero_de_atencion = %s"
            cursor.execute(formulario_sql, (id,))
            formulario = cursor.fetchone()

            enajenantes_sql = "SELECT RUNRUT, porcDerecho FROM Enajenantes WHERE enajenante_id = %s"
            cursor.execute(enajenantes_sql, (id,))
            enajenantes = cursor.fetchall()

            adquirentes_sql = "SELECT RUNRUT, porcDerecho FROM Adquirentes WHERE Adquirente_id = %s"
            cursor.execute(adquirentes_sql, (id,))
            adquirentes = cursor.fetchall()

        return render_template('ver_formulario.html', formulario=formulario, enajenantes=enajenantes, adquirentes=adquirentes)

    finally:
        connection.close()

@app.route('/ver_multipropietarios')
def ver_multipropietarios():
    # Obtener la lista de multipropietarios desde la base de datos
    multipropietarios = [...] 
    return render_template('ver_multipropietarios.html', multipropietarios=multipropietarios)

#LAS FUCNIONES COMENTADAS SON REDUNDANTES, NO SE USAN. VEO SI HAGO ALGO CON ELLAS O LAS FUNO.

# @app.route('/show_formularios', methods=['GET'])
# def show_formularios():
#     connection = get_db_connection()
#     filters = {}
#     filters["CNE"] = request.args.get('CNE')
#     filters["Comuna"] = request.args.get('Comuna')
#     filters["Manzana"] = request.args.get('Manzana')
#     filters["Predio"] = request.args.get('Predio')
#     search_filters = ""
#     if(any(v != None for v in list(filters.values()))):
#         search_filters = " WHERE "
#         for key in filters.keys():
#             if(filters[key] != None):
#                 search_filters += key + " = " + filters[key] + " AND "

#     try:
#         with connection.cursor() as cursor:
#             formulario_sql = "SELECT * FROM formulario" + search_filters[0:-4]
#             cursor.execute(formulario_sql)
#             formularios = cursor.fetchall()
#             formularios= json.dumps(formularios, default=str)
#             print(formularios)
#         return formularios

#     finally:
#         connection.close()


# @app.route('/show_formulario', methods=['GET'])
# def show_formulario():
#     connection = get_db_connection()
#     id  = request.args.get('id')
#     try:
#         with connection.cursor() as cursor:
#             # Obtener los datos de la tabla 'formulario'
#             formulario_sql = "SELECT * FROM formulario WHERE Numero_de_atencion = " + str(id)
#             cursor.execute(formulario_sql)
#             formulario = cursor.fetchall()
#             adquirentes_sql = "SELECT * FROM Adquirentes WHERE Adquirente_id = " + str(id)
#             cursor.execute(adquirentes_sql)
#             adquirentes = cursor.fetchall()
#             enajenantes_sql = "SELECT * FROM Enajenantes WHERE Enajenante_id = " + str(id)
#             cursor.execute(enajenantes_sql)
#             enajenantes = cursor.fetchall()
#             formulario[0]["enajenantes"] = enajenantes
#             formulario[0]["adquirentes"] = adquirentes
#             formulario= json.dumps(formulario, default=str)
#             print(formulario)
            
#         return formulario

#     finally:
#         connection.close()

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

# @app.route('/add_formulario', methods=['POST'])
# def add_formulario():
#     data = request.get_json()
#     print(f"Data recieved: {data['CNE']}")
    
#     # Extract the form data from the JSON object
#     cne = data['CNE']
#     comuna = data['bienRaiz']['comuna']
#     manzana = data['bienRaiz']['manzana']
#     predio = data['bienRaiz']['predio']
#     fojas = data['fojas']
#     fecha_inscripcion = data['fechaInscripcion']
#     numero_inscripcion = data['nroInscripcion']

#     # Extract enajenantes and adquirentes data from the JSON object
#     try:
#         enajenantes_data = data['enajenantes']
#     except:
#         enajenantes_data = []
#     try:
#         adquirentes_data = data['adquirentes']
#     except:
#         adquirentes_data = []
#     formulario = form_solver(data, get_db_connection)
#     formulario.determinar_y_procesar_escenario()
#     formulario.ajustar_porcentajes_adquirentes()
#     return jsonify({"message": "Formulario submitted successfully"})
if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')