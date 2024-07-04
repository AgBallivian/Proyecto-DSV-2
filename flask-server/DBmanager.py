from flask import jsonify
import pymysql

from config import Config
from utils import (_deconstruir_com_man_pred,
                   _obtener_ano_desde_query,
                     obtener_ano_inscripcion)
from Queries import (
    QUERY_ALL_FORMULARIOS, QUERY_INSERTAR_FORM, INTERNAL_SERVER_ERROR,
    QUERY_ALL_ENAJENANTES, QUERY_INSERTAR_ENAJENANTES, QUERY_ALL_ADQUIRENTES,
    QUERY_INSERTAR_ADQUIRENTES, QUERY_ID_TRANSFERENCIAS, QUERY_INSERTAR_ENAJENANTES_TRANSFERENCIAS_SQL,
    QUERY_INSERTAR_ADQUIRENTES_TRANSFERENCIAS_SQL, QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIOS_SQL,
    QUERY_CONNECTOR, QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIOS_SQL,
    QUERY_ACTUALIZAR_TRANSFERENCIAS, QUERY_SELECT_MULTIPROPIETARIOS_VIGENTES,
    QUERY_ALL_MULTIPROPIETARIOS, QUERY_ID_MULTIPROPIETARIOS,
    QUERY_FORMULARIO_COM_MAN_PRED, QUERY_ENAJENANTES_POR_FORMULARIO, QUERY_ADQUIRENTES_POR_FORMULARIO,
    QUERY_OBTENER_TRANFERENCIAS_DESDE_ANO, QUERY_OBTENER_ULT_ANO_INSCRIPCION_EXCLUSIVO, QUERY_ELIMINAR_FILA_MULTIPROPIETARIOS_DESDE_ANO,
    QUERY_SELECT_FORMULARIO_NUMERO_INSCRIPCION, QUERY_OBTENER_TRANFERENCIAS_IGUAL_ANO,
    QUERY_OBTENER_ULT_ANO_INSCRIPCION, OBTENER_MULTIPROPIETARIO_COMMANPRED_SQL,
    QUERY_ELIMINAR_FILA_MULTIPROPIETARIOS_IGUAL_ANO, QUERY_ACTUALIZAR_MULTIPROPIETARIOS_POR_VIGENCIA,
    QUERY_OBTENER_NUM_MULTIPROPIETARIO_SEGUN_ID, QUERY_OBTENER_ID_MULTIPROPIETARIO_SEGUN_NUM)

ERROR_MESSAGE = "Error in DBmanager:  "
config = Config()

def obtener_conexion_db():
    connection = pymysql.connect(host=config.MYSQL_HOST,
                                 user=config.MYSQL_USER,
                                 password=config.MYSQL_PASSWORD,
                                 db=config.MYSQL_DB,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def _ejecutar_query(query, parameters = None):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            if(parameters):
                cursor.execute(query, parameters)
            else:
                 cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, query, e)
        raise e
    finally:
        connect.commit()
        connect.close()

def obtener_numero_de_atencion():
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            cursor.execute(QUERY_ALL_FORMULARIOS)
            formularios = cursor.fetchall()
            return len(formularios)
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        raise e
    finally:
        connect.close()

def agregar_formulario(cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            cursor.execute(QUERY_ALL_FORMULARIOS)
            formularios = cursor.fetchall()
            numero_de_atencion = len(formularios) + 1
            cursor.execute(QUERY_INSERTAR_FORM, (
                numero_de_atencion,
                cne,
                comuna,
                manzana,
                predio,
                fojas,
                fecha_inscripcion,
                numero_inscripcion
            ))
        connect.commit()
        return numero_de_atencion
    except Exception as e:
        connect.rollback()
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

def agregar_enajenante(numero_de_atencion, runrut, porcentaje_derecho):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            #Obtain next id from 'enajenantes' table
            cursor.execute(QUERY_ALL_ENAJENANTES)
            enajenantes = cursor.fetchall()
            enjante_id = len(enajenantes) + 1
            # Insert enajenantes data into the 'enajenantes' table
            cursor.execute(QUERY_INSERTAR_ENAJENANTES, (
                enjante_id,
                numero_de_atencion,
                runrut,
                porcentaje_derecho,
            ))
        connect.commit()
        return "Ingreso el enajenante"
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, QUERY_INSERTAR_ADQUIRENTES, e)
    finally:
        connect.close()

def agregar_adquirente(numero_de_atencion, runrut, porcentaje_derecho):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            #Obtain next id from 'Adquirentes' table
            cursor.execute(QUERY_ALL_ADQUIRENTES)
            adquirentes = cursor.fetchall()
            adquirentes_id = len(adquirentes) + 1
            # Insert adquirentes data into the 'Adquirentes' table
            cursor.execute(QUERY_INSERTAR_ADQUIRENTES, (
                adquirentes_id,
                numero_de_atencion,
                runrut,
                porcentaje_derecho
            ))
            connect.commit()
        return "Ingreso el Adquirente"
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, QUERY_INSERTAR_ADQUIRENTES, e)
    finally:
        connect.close()

def _obtener_siguiente_id_transferencias():
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            cursor.execute(QUERY_ID_TRANSFERENCIAS)
            id_transferencias = cursor.fetchall()
            return id_transferencias[0]["id"] + 1 if id_transferencias else 0
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

def _obtener_siguiente_id_multipropietarios():
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            cursor.execute(QUERY_ID_MULTIPROPIETARIOS)
            id_multipropietarios = cursor.fetchall()
            return id_multipropietarios[0]["id"] + 1 if id_multipropietarios else 0
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()


def eliminar_multipropietarios_desde_ano(ano_inscripcion_actual, com_man_pred):
    _ejecutar_query(QUERY_ELIMINAR_FILA_MULTIPROPIETARIOS_DESDE_ANO.format(
        com_man_pred=com_man_pred,
        ano_inscripcion=ano_inscripcion_actual
        ))
def eliminar_multipropietarios_igual_ano(ano_inscripcion_actual, com_man_pred):
    _ejecutar_query(QUERY_ELIMINAR_FILA_MULTIPROPIETARIOS_IGUAL_ANO.format(
        com_man_pred=com_man_pred,
        ano_inscripcion=ano_inscripcion_actual
        ))


def aplicar_filtros(region_id, comuna_id, block_number, property_number, year):
    filtros = []
    if region_id:
        filtros.append(f"com_man_pred IN (SELECT CONCAT(SUBSTRING_INDEX(m.com_man_pred, '-', 1), '-', SUBSTRING_INDEX(SUBSTRING_INDEX(m.com_man_pred, '-', -2), '-', 1), '-', SUBSTRING_INDEX(m.com_man_pred, '-', -1)) FROM transferencias m JOIN comunas c ON SUBSTRING_INDEX(m.com_man_pred, '-', 1) = c.id_comuna WHERE c.id_region = {region_id})")
    if comuna_id:
        filtros.append(f"SUBSTRING_INDEX(com_man_pred, '-', 1) = '{comuna_id}'")
    if block_number:
        filtros.append(f"SUBSTRING_INDEX(SUBSTRING_INDEX(com_man_pred, '-', -2), '-', 1) = '{block_number}'")
    if property_number:
        filtros.append(f"SUBSTRING_INDEX(com_man_pred, '-', -1) = '{property_number}'")
    if year:
        filtros.append(f"(Ano_vigencia_final IS NULL OR Ano_vigencia_final >= {year}) AND Ano_vigencia_inicial <= {year}")

    return filtros


def _insert_enajenantes_to_transferencias(id_transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion):
    # query, parameters = _construir_query_insertar_enajenantes(id_transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion)
    query = QUERY_INSERTAR_ENAJENANTES_TRANSFERENCIAS_SQL
    parameters = (id_transferencia,
        com_man_pred,
        enajenante['RUNRUT'],
        enajenante['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None,
        "Enajenante")
    _ejecutar_query(query, parameters)


def _insert_enajenantes_to_multipropietarios(id_transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion):
    # query, parameters = _construir_query_insertar_enajenantes(id_transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion)
    query = QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIOS_SQL
    parameters = (
        id_transferencia,
        com_man_pred,
        enajenante['RUNRUT'],
        enajenante['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None
    )
    _ejecutar_query(query, parameters)


def _insert_adquirientes_to_transferencias(id_transferencia, com_man_pred, adquirente, fojas, fecha_inscripcion, numero_inscripcion):
    query = QUERY_INSERTAR_ADQUIRENTES_TRANSFERENCIAS_SQL
    parameters = (
        id_transferencia,
        com_man_pred,
        adquirente['RUNRUT'],
        adquirente['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None,
        "Adquirente"
    )
    _ejecutar_query(query, parameters)

def _insert_adquirientes_to_multipropietarios(id_transferencia, com_man_pred, adquirente, fojas, fecha_inscripcion, numero_inscripcion):
    if("Numero_inscripcion" in adquirente.keys()):
        numero_inscripcion = adquirente["Numero_inscripcion"]
    query = QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIOS_SQL
    parameters = (
        id_transferencia,
        com_man_pred,
        adquirente['RUNRUT'],
        adquirente['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None,
    )
    _ejecutar_query(query, parameters)


def _obtener_ultimo_ano_inscripcion_exclusivo(com_man_pred, numero_inscripcion):
    query = construir_query_obtener_ultimo_ano_inscripcion_exclusivo(com_man_pred, numero_inscripcion)
    last_initial_year_query = _ejecutar_query(query)
    if(not last_initial_year_query):
        query = construir_query_obtener_ultimo_ano_inscripcion(com_man_pred)
        last_initial_year_query = _ejecutar_query(query)
    return _obtener_ano_desde_query(last_initial_year_query)

def construir_query_obtener_ultimo_ano_inscripcion_exclusivo(com_man_pred, numero_inscripcion):
    return QUERY_OBTENER_ULT_ANO_INSCRIPCION_EXCLUSIVO.format(com_man_pred=com_man_pred, numero_inscripcion=numero_inscripcion)

def _obtener_ultimo_ano_inscripcion(com_man_pred):
    query = construir_query_obtener_ultimo_ano_inscripcion(com_man_pred)
    last_initial_year_query = _ejecutar_query(query)
    return _obtener_ano_desde_query(last_initial_year_query)

def construir_query_obtener_ultimo_ano_inscripcion(com_man_pred):
    return QUERY_OBTENER_ULT_ANO_INSCRIPCION.format(com_man_pred=com_man_pred)

    
def actualizar_multipropietarios_por_vigencia(com_man_pred, ano_final, numero_inscripcion):
    try:
        query_multipropietarios_id = QUERY_OBTENER_ID_MULTIPROPIETARIO_SEGUN_NUM.format(com_man_pred=com_man_pred, numero_inscripcion=numero_inscripcion)
        multipropietarios_id = _ejecutar_query(query_multipropietarios_id)
        query_multipropietarios_num_inscripcion = QUERY_OBTENER_NUM_MULTIPROPIETARIO_SEGUN_ID.format(com_man_pred=com_man_pred, id=multipropietarios_id[0]["id"])
        multipropietarios_num_inscripcion = _ejecutar_query(query_multipropietarios_num_inscripcion)
        actualizar_vigencia_multipropietarios = QUERY_ACTUALIZAR_MULTIPROPIETARIOS_POR_VIGENCIA.format(
            com_man_pred=com_man_pred, 
            numero_inscripcion=multipropietarios_num_inscripcion[0]["Numero_inscripcion"], 
            ano_final=ano_final,
            id=multipropietarios_id[0]["id"])
        _ejecutar_query(actualizar_vigencia_multipropietarios)
        return True
    except Exception as e:
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR

def actualizar_transferia_por_vigencia(com_man_pred, ano_final):
    try:
        query_multipropietarios = QUERY_ACTUALIZAR_TRANSFERENCIAS.format(ano_final=ano_final, com_man_pred=com_man_pred)
        _ejecutar_query(query_multipropietarios)
        return True
    except Exception as e:
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR

def obtener_multipropietarios_filtrados(region_id, comuna_id, block_number, property_number, year):
    connection = obtener_conexion_db()
    try:
        with connection.cursor() as cursor:
            multipropietarios_sql = QUERY_ALL_MULTIPROPIETARIOS
            filtros = aplicar_filtros(region_id, comuna_id, block_number, property_number, year)
            if filtros:
                multipropietarios_sql += QUERY_CONNECTOR.join(filtros)

            cursor.execute(multipropietarios_sql)
            multipropietarios = cursor.fetchall()
            return multipropietarios
    finally:
        connection.close()

def obtener_multipropietarios_commanpred(com_man_pred):
    try:
            multipropietarios_sql = OBTENER_MULTIPROPIETARIO_COMMANPRED_SQL.format(
                 com_man_pred=com_man_pred,
            )

            multipropietarios = _ejecutar_query(multipropietarios_sql)
            return multipropietarios
    except Exception as e:
        print(ERROR_MESSAGE, e)
        return None
    

def obtener_multipropietarios_vigentes(com_man_pred):
    query = QUERY_SELECT_MULTIPROPIETARIOS_VIGENTES.format(
        com_man_pred=com_man_pred,
    )
    return _ejecutar_query(query) 

def obtener_formularios_por_com_man_pred(com_man_pred):
    try:
        formularios_raw = _ejecutar_query(_construir_query_obtener_formulario_por_commanpred(com_man_pred))
        formularios = []
        for formulario in formularios_raw:
            formulario_procesado = {
                'CNE': formulario['CNE'],
                'bienRaiz': {
                    'comuna': formulario['Comuna'],
                    'manzana': formulario['Manzana'],
                    'predio': formulario['Predio']
                },
                'fojas': formulario['Fojas'],
                'fechaInscripcion': formulario['Fecha_de_inscripcion'].strftime('%Y-%m-%d'),
                'nroInscripcion': formulario['Numero_de_insripcion'],
                'enajenantes': obtener_enajenantes_por_formulario(formulario['Numero_de_atencion']),
                'adquirentes': obtener_adquirentes_por_formulario(formulario['Numero_de_atencion'])
            }
            formularios.append(formulario_procesado)
        return formularios
    except Exception as e:
        print(f"Error al obtener formularios: {e}")
        return []
    
def obtener_formulario_por_numero_inscripcion(numero_inscripcion):
    try:
        query = _construir_query_obtener_formulario_por_num(numero_inscripcion)
        formularios_raw = _ejecutar_query(query)
        formularios = []
        for formulario in formularios_raw:
            formulario_procesado = {
                'CNE': formulario['CNE'],
                'bienRaiz': {
                    'comuna': formulario['Comuna'],
                    'manzana': formulario['Manzana'],
                    'predio': formulario['Predio']
                },
                'fojas': formulario['Fojas'],
                'fechaInscripcion': formulario['Fecha_de_inscripcion'].strftime('%Y-%m-%d'),
                'nroInscripcion': formulario['Numero_de_insripcion'],
                'enajenantes': obtener_enajenantes_por_formulario(formulario['Numero_de_atencion']),
                'adquirentes': obtener_adquirentes_por_formulario(formulario['Numero_de_atencion'])
            }
            formularios.append(formulario_procesado)
        return formularios[0]
    except Exception as e:
        print(f"Error al obtener formularios: {e}")
        return []

def _construir_query_obtener_formulario_por_num(numero_inscripcion):
    return QUERY_SELECT_FORMULARIO_NUMERO_INSCRIPCION.format(
        numero_de_inscripcion = numero_inscripcion
    )

def _construir_query_obtener_formulario_por_commanpred(com_man_pred):
    comuna, manzana, predio = _deconstruir_com_man_pred(com_man_pred)
    return QUERY_FORMULARIO_COM_MAN_PRED.format(
        comuna=int(comuna),
        manzana=int(manzana),
        predio=int(predio)
    )
def obtener_enajenantes_por_formulario(numero_atencion):
    try:
        enajenantes = _ejecutar_query(QUERY_ENAJENANTES_POR_FORMULARIO.format(numero_atencion=numero_atencion))
        return [{'RUNRUT': e['RUNRUT'], 'porcDerecho': float(e['porcDerecho'])} for e in enajenantes]
    except Exception as e:
        print(ERROR_MESSAGE, e)
        return []

def obtener_adquirentes_por_formulario(numero_atencion):
    try:
        adquirentes = _ejecutar_query(QUERY_ADQUIRENTES_POR_FORMULARIO.format(numero_atencion=numero_atencion))
        return [{'RUNRUT': a['RUNRUT'], 'porcDerecho': float(a['porcDerecho'])} for a in adquirentes]
    except Exception as e:
        print(ERROR_MESSAGE, e)
        return []

def obtener_transferencias_desde_ano(com_man_pred, ano_inscripcion):
    query = QUERY_OBTENER_TRANFERENCIAS_DESDE_ANO.format(
        com_man_pred = com_man_pred,
        ano_inscripcion = ano_inscripcion
        )
    num_inscripcion_transferenicas = []
    transferenicas = _ejecutar_query(query)
    for transferencia in transferenicas:
        if(transferencia["Numero_inscripcion"] not in num_inscripcion_transferenicas):
            num_inscripcion_transferenicas.append(transferencia["Numero_inscripcion"])
    return num_inscripcion_transferenicas

def obtener_transferencias_igual_ano(com_man_pred, ano_inscripcion):
    query = QUERY_OBTENER_TRANFERENCIAS_IGUAL_ANO.format(
        com_man_pred = com_man_pred,
        ano_inscripcion = ano_inscripcion
        )
    transferenicas = _ejecutar_query(query)
    return transferenicas