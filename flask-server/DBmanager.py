from flask import jsonify
import pymysql

from config import Config
from utils import _construir_com_man_pred, _obtener_count_Transferencias, _obtener_ano_desde_query, obtener_ano_inscripcion
from Queries import (
    QUERY_ALL_FORMULARIOS, QUERY_INSERTAR_FORM, INTERNAL_SERVER_ERROR,
    QUERY_ALL_ENAJENANTES, QUERY_INSERTAR_ENAJENANTES, QUERY_ALL_ADQUIRENTES,
    QUERY_INSERTAR_ADQUIRENTES, QUERY_ID_TRANSFERENCIAS,
    QUERY_UPDATE_TRANSFERENCIAS_SQL, QUERY_DELETE_TRANSFERENCIAS,
    QUERY_OBTENER_TRANSFERENCIAS_SQL, QUERY_INSERTAR_ENAJENANTES_TRANSFERENCIAS_SQL,
    QUERY_INSERTAR_ADQUIRENTES_TRANSFERENCIAS_SQL,
    COMPRAVENTA, REGULARIZACION_DE_PATRIMONIO, QUERY_OBTENER_ULT_ANO_INIT, QUERY_CONNECTOR,
    QUERY_AGREGAR_MULTIPROPIETARIO, QUERY_OBTENER_ID_MULTIPROPIETARIOS_SQL, QUERY_ACTUALIZAR_MULTIPROPIETARIO
    )

ERROR_MESSAGE = "Error "
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
        print(ERROR_MESSAGE, e)
        raise e
    finally:
        connect.close()

def obtener_numer_de_atencion():
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

def add_formulario(cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion):
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

def add_enajenante(numero_de_atencion, runrut, porcentaje_derecho):#cambiar a enajenante{id:id, num:num, runrut:runrut, procderecho:porcderecho}
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
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

def add_adquirente(numero_de_atencion, runrut, porcentaje_derecho):
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
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

# def add_multipropietario(self):
#     id_multipropietario = _obtener_siguiente_id_multipropietario()
#     com_man_pred = self._construir_com_man_pred()

#     for enajenante in self.enajenantes_data:
#         self._insert_enajenantes_to_multipropietarios(id_multipropietario,
#             com_man_pred, enajenante)
#         id_multipropietario += 1

#     for adquirente in self.adquirentes_data:
#         self._insert_adquirientes_to_multipropietarios(id_multipropietario, com_man_pred, adquirente)
#         id_multipropietario += 1
    
# def obtener_ano_inscripcion(self):
#     return int(self.fecha_inscripcion.split("-")[0])

def _obtener_siguiente_id_Transferencias():
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            cursor.execute(QUERY_ID_TRANSFERENCIAS)
            id_Transferencias = cursor.fetchall()
            return id_Transferencias[0]["id"] + 1 if id_Transferencias else 0
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

def _actualizar_multipropietarios_por_vigencia(last_initial_year_in, comuna, manzana, predio, fecha_inscripcion):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            com_man_pred = _construir_com_man_pred(comuna, manzana, predio)
            ano_final = _obtener_ano_final(fecha_inscripcion)
            query_multipropietarios = _construir_query_actualizar_Transferencias(ano_final, last_initial_year_in, com_man_pred)
            _ejecutar_query_actualizar_Transferencias(cursor, query_multipropietarios)
            connect.commit()
            return True
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

def _obtener_ano_final(fecha_inscripcion):
    return obtener_ano_inscripcion(fecha_inscripcion) - 1

def _construir_query_actualizar_Transferencias(ano_final, last_initial_year, com_man_pred):
    return QUERY_UPDATE_TRANSFERENCIAS_SQL.format(
        ano_final=ano_final,
        last_initial_year=last_initial_year,
        com_man_pred=com_man_pred
    )

def _ejecutar_query_actualizar_Transferencias(query):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            print("Number of rows modified: ", cursor.execute(query))
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        raise e
    finally:
        connect.close()

def delete_Transferencias_antiguos(last_initial_year, comuna, manzana, predio):
    # connect = obtener_conexion_db()
    # try:
    #     with connect.cursor() as cursor:
            com_man_pred = _construir_com_man_pred(comuna, manzana, predio)
            delete_vigencia_final_query = _construir_query_delete_Transferencias(last_initial_year, com_man_pred)
            _ejecutar_query(delete_vigencia_final_query)
    #         connect.commit()
    #         return True
    # except Exception as e:
    #     connect.rollback()
    #     print(ERROR_MESSAGE, e)
    #     return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    # finally:
    #     connect.close()

def _construir_query_delete_Transferencias(last_initial_year, com_man_pred):
    return QUERY_DELETE_TRANSFERENCIAS.format(
        last_initial_year=str(last_initial_year),
        com_man_pred=com_man_pred
    )


def obtener_Transferencias(comuna, manzana, predio):
    # connect = obtener_conexion_db()
    # try:
    #     with connect.cursor() as cursor:
            com_man_pred = _construir_com_man_pred(comuna, manzana, predio)
            Transferencia_sql = _construir_query_obtener_Transferencias(com_man_pred)
            Transferencias = _ejecutar_query(Transferencia_sql)
            return _obtener_count_Transferencias(Transferencias)
    # except Exception as e:
    #     connect.rollback()
    #     print(ERROR_MESSAGE, e)
    #     return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    # finally:
    #     connect.close()
def _construir_query_obtener_Transferencias(com_man_pred):
    return QUERY_OBTENER_TRANSFERENCIAS_SQL.format(com_man_pred=com_man_pred)


def obtener_Transferencias_filtrados(region_id, comuna_id, block_number, property_number, year):
    connection = obtener_conexion_db()
    try:
        with connection.cursor() as cursor:
            Transferencias_sql = "SELECT * FROM Transferencias"
            filtros = aplicar_filtros(region_id, comuna_id, block_number, property_number, year)
            if filtros:
                Transferencias_sql += QUERY_CONNECTOR.join(filtros)

            cursor.execute(Transferencias_sql)
            Transferencias = cursor.fetchall()
            return Transferencias
    finally:
        connection.close()


def aplicar_filtros(region_id, comuna_id, block_number, property_number, year):
    filtros = []
    if region_id:
        filtros.append(f"com_man_pred IN (SELECT CONCAT(SUBSTRING_INDEX(m.com_man_pred, '-', 1), '-', SUBSTRING_INDEX(SUBSTRING_INDEX(m.com_man_pred, '-', -2), '-', 1), '-', SUBSTRING_INDEX(m.com_man_pred, '-', -1)) FROM Transferencias m JOIN comunas c ON SUBSTRING_INDEX(m.com_man_pred, '-', 1) = c.id_comuna WHERE c.id_region = {region_id})")
    if comuna_id:
        filtros.append(f"SUBSTRING_INDEX(com_man_pred, '-', 1) = '{comuna_id}'")
    if block_number:
        filtros.append(f"SUBSTRING_INDEX(SUBSTRING_INDEX(com_man_pred, '-', -2), '-', 1) = '{block_number}'")
    if property_number:
        filtros.append(f"SUBSTRING_INDEX(com_man_pred, '-', -1) = '{property_number}'")
    if year:
        filtros.append(f"(Ano_vigencia_final IS NULL OR Ano_vigencia_final >= {year}) AND Ano_vigencia_inicial <= {year}")

    return filtros

# def _obtener_count_multipropietarios(multipropietarios):
#     return multipropietarios[0]['COUNT(*)']

def _insert_enajenantes_to_Transferencias(id_Transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion):
    # connect = obtener_conexion_db()
    # try:
    #     with connect.cursor() as cursor:
            query, parameters = _construir_query_insertar_enajenantes(id_Transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion)
            _ejecutar_query(query, parameters)
    #         connect.commit()
    # except Exception as e:
    #     connect.rollback()
    #     print(ERROR_MESSAGE, e)
    #     return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    # finally:
    #     connect.close()

def _construir_query_insertar_enajenantes(id_Transferencia, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion):
    return QUERY_INSERTAR_ENAJENANTES_TRANSFERENCIAS_SQL, (
        id_Transferencia,
        com_man_pred,
        enajenante['RUNRUT'],
        enajenante['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None,
        "Enajenante"
    )

    # return QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIO_SQL.format(
    #     id = id_multipropietario,
    #     com_man_pred = com_man_pred,
    #     RUNRUT = enajenante['RUNRUT'],
    #     porcDerecho = enajenante['porcDerecho'],
    #     Fojas = fojas,
    #     Ano_inscripcion = int(obtener_ano_inscripcion(fecha_inscripcion)),
    #     Numero_inscripcion = numero_inscripcion,
    #     Fecha_de_inscripcion = fecha_inscripcion,
    #     Ano_vigencia_inicial = int(obtener_ano_inscripcion(fecha_inscripcion)),
    #     Ano_vigencia_final = None,
    #     Tipo = "Enajenante"
# (id = '{id}', com_man_pred = '{com_man_pred}', RUNRUT = '{RUNRUT}', porcDerecho = '{porcDerecho}',
#                                     Fojas = '{Fojas}', Ano_inscripcion = '{Ano_inscripcion}', Numero_inscripcion = '{Numero_inscripcion}',
#                                     Fecha_de_inscripcion = '{Fecha_de_inscripcion}', Ano_vigencia_inicial = '{Ano_vigencia_inicial}',
#                                     Ano_vigencia_final = '{Ano_vigencia_final}', Tipo = '{Tipo}')

def _insert_adquirientes_to_Transferencias(id_Transferencia, com_man_pred, adquirente, fojas, fecha_inscripcion, numero_inscripcion):
    # connect = obtener_conexion_db()
    # try:
    #     with connect.cursor() as cursor:
            query, parameters = _construir_query_insertar_adquirientes(id_Transferencia, com_man_pred, adquirente, fojas, fecha_inscripcion, numero_inscripcion)
            _ejecutar_query(query, parameters)
    #         connect.commit()
    # except Exception as e:
    #     connect.rollback()
    #     print(ERROR_MESSAGE, e)
    #     return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    # finally:
    #     connect.close()

def _construir_query_insertar_adquirientes(id_Transferencia, com_man_pred, adquirente, fojas, fecha_inscripcion, numero_inscripcion):
    return QUERY_INSERTAR_ADQUIRENTES_TRANSFERENCIAS_SQL, (
        id_Transferencia,
        com_man_pred,
        adquirente['RUNRUT'],
        adquirente['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None,
        "Aquirente"
    )

def _obtener_ultimo_ano_inicial(comuna, manzana, predio):
    # connect = obtener_conexion_db()
    # try:
    #     with connect.cursor() as cursor:
            com_man_pred = _construir_com_man_pred(comuna, manzana, predio)
            query = _construir_query_obtener_ultimo_ano_inicial(com_man_pred)
            last_initial_year_query = _ejecutar_query( query)
            return _obtener_ano_desde_query(last_initial_year_query)
    # except Exception as e:
    #     connect.rollback()
    #     print(ERROR_MESSAGE, e)
    #     return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    # finally:
    #     connect.close()

def _construir_query_obtener_ultimo_ano_inicial(com_man_pred):
    return QUERY_OBTENER_ULT_ANO_INIT.format(com_man_pred=com_man_pred)

# def _obtener_ano_desde_query(query_result):
#     return query_result[0]['Ano']
def obtener_multipropietario(numero_de_atencion):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            cursor.execute(QUERY_ALL_FORMULARIOS)
            formularios = cursor.fetchall()
            return formularios[numero_de_atencion - 1]
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        raise e
    finally:
        connect.close()


def agregar_multipropietario(com_man_pred, RUNRUT, porcDerecho,
                            Fojas, Ano_inscripcion, Numero_inscripcion,
                            Fecha_de_inscripcion, Ano_vigencia_inicial):
    connect = obtener_conexion_db()
    try:
        id = _construir_query_obtener_multipropietarios_id(com_man_pred)
        with connect.cursor() as cursor:
            cursor.execute(QUERY_AGREGAR_MULTIPROPIETARIO, (id, com_man_pred, RUNRUT, porcDerecho,
                                    Fojas, Ano_inscripcion, Numero_inscripcion,
                                    Fecha_de_inscripcion, Ano_vigencia_inicial,
                                    None))
            connect.commit()
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        raise e
    finally:
        connect.close()

def _construir_query_obtener_multipropietarios_id(com_man_pred):
        return QUERY_OBTENER_ID_MULTIPROPIETARIOS_SQL.format(com_man_pred=com_man_pred)

def _actualizar_multipropietarios_por_vigencia(last_initial_year_in, comuna, manzana, predio, fecha_inscripcion):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            com_man_pred = _construir_com_man_pred(comuna, manzana, predio)
            ano_final = _obtener_ano_final(fecha_inscripcion)
            query_multipropietarios = _construir_query_actualizar_multipropietarios(ano_final, last_initial_year_in, com_man_pred)
            _ejecutar_query_actualizar_multipropietarios(query_multipropietarios)
            connect.commit()
            return True
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    finally:
        connect.close()

def _construir_query_actualizar_multipropietarios(id_Multipropietario, com_man_pred, enajenante, fojas, fecha_inscripcion, numero_inscripcion):
    return QUERY_ACTUALIZAR_MULTIPROPIETARIO, (
        id_Multipropietario,
        com_man_pred,
        enajenante['RUNRUT'],
        enajenante['porcDerecho'],
        fojas,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        numero_inscripcion,
        fecha_inscripcion,
        int(obtener_ano_inscripcion(fecha_inscripcion)),
        None,
    )

def _ejecutar_query_actualizar_multipropietarios(query):
    connect = obtener_conexion_db()
    try:
        with connect.cursor() as cursor:
            print("Number of rows modified: ", cursor.execute(query))
    except Exception as e:
        connect.rollback()
        print(ERROR_MESSAGE, e)
        raise e
    finally:
        connect.close()