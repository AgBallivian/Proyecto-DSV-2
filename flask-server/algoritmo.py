from flask import request, jsonify
import json
import pymysql
from Queries import *

#revisar
# QUERY_OBTENER_SUMA_PORC_DERECHO_SQL = """
# SELECT SUM(porcDerecho) AS sum
# FROM Multipropietarios
# WHERE com_man_pred='{com_man_pred}'
#   AND RUNRUT IN {run_rut_enajenantes}
# """
#Mover esto a otro archivo
def formatear_runrut_enajenantes(runrut_enajenantes):
    return str(runrut_enajenantes).replace("[", "(").replace("]", ")")

class form_solver(): 
    def __init__(self, formulario, connection):
        self.formulario = formulario
        self.cne = int(formulario['CNE'])
        self.comuna = int(formulario['bienRaiz']['comuna'])
        self.manzana = int(formulario['bienRaiz']['manzana'])
        self.predio = int(formulario['bienRaiz']['predio'])
        self.fojas = int(formulario['fojas'])
        self.fecha_inscripcion = formulario['fechaInscripcion']
        self.numero_inscripcion = int(formulario['nroInscripcion'])
        self.connection = connection

        try:
            self.enajenantes_data = formulario['enajenantes']
        except:
            self.enajenantes_data = []
        try:
            self.adquirentes_data = formulario['adquirentes']
        except:
            self.adquirentes_data = []

    def obtener_numer_de_atencion(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:   
                cursor.execute(QUERY_ALL_FORMULARIOS)
                formularios = cursor.fetchall()
                return len(formularios)
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            raise e
        finally:
            connect.close()

    def add_formulario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:               
                cursor.execute(QUERY_ALL_FORMULARIOS)
                formularios = cursor.fetchall()
                numero_de_atencion = len(formularios) + 1
                
                cursor.execute(QUERY_INSERTAR_FORM, (
                    numero_de_atencion, 
                    self.cne, 
                    self.comuna, 
                    self.manzana, 
                    self.predio, 
                    self.fojas, 
                    self.fecha_inscripcion, 
                    self.numero_inscripcion
                ))
            connect.commit()
            return numero_de_atencion
        except Exception as e:
            connect.rollback()
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def add_enajenante(self, numero_de_atencion):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                #Obtain next id from 'enajenantes' table
                cursor.execute(QUERY_ALL_ENAJENANTES)
                enajenantes = cursor.fetchall()
                id = len(enajenantes) + 1
                # Insert enajenantes data into the 'enajenantes' table
                for num_enajenante, enajenante in enumerate(self.enajenantes_data):
                    cursor.execute(QUERY_INSERTAR_ENAJENANTES, (
                        (id + num_enajenante), 
                        numero_de_atencion, 
                        enajenante['RUNRUT'], 
                        enajenante['porcDerecho']
                ))
            connect.commit()
            return "Ingreso el enajenante"
        except Exception as e:
            connect.rollback()
            print("Error: ", str(e))
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def add_adquirente(self, numero_de_atencion):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                #Obtain next id from 'Adquirentes' table
                cursor.execute(QUERY_ALL_ADQUIRENTES)
                adquirentes = cursor.fetchall()
                id = len(adquirentes) + 1
                # Insert adquirentes data into the 'Adquirentes' table
                for num_adquirente, adquirente in enumerate(self.adquirentes_data):
                    cursor.execute(QUERY_INSERTAR_ADQUIRENTES, (
                        (id + num_adquirente),
                        numero_de_atencion, 
                        adquirente['RUNRUT'], 
                        int(adquirente['porcDerecho'])
                    ))
                connect.commit()
            return "Ingreso el Adquirente"
        except Exception as e:
            connect.rollback()
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def add_multipropietario(self):
        id_multipropietario = self._obtener_siguiente_id_multipropietario()
        com_man_pred = self._construir_com_man_pred()

        for enajenante in self.enajenantes_data:
            self._insert_enajenantes_to_multipropietarios(id_multipropietario, com_man_pred, enajenante)
            id_multipropietario += 1

        for adquirente in self.adquirentes_data:
            self._insert_adquirientes_to_multipropietarios(id_multipropietario, com_man_pred, adquirente)
            id_multipropietario += 1
        

    def obtener_ano_inscripcion(self):
        return int(self.fecha_inscripcion.split("-")[0])

    def _obtener_siguiente_id_multipropietario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                cursor.execute(QUERY_ID_MULTIPROPIETARIOS)
                id_multipropietario = cursor.fetchall()
                return id_multipropietario[0]["id"] + 1 if id_multipropietario else 0
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()
    


#Revisar
    def _actualizar_multipropietarios_por_vigencia(self, last_initial_year_in):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = self._construir_com_man_pred()
                ano_final = self.obtener_ano_inscripcion() - 1
                query_multipropietarios = QUERY_UPDATE_MULTIPROPIETARIO_SQL.format(
                    ano_final=ano_final,
                    last_initial_year=last_initial_year_in,
                    com_man_pred=com_man_pred
                )
                print("Number of rows modified: ", cursor.execute(query_multipropietarios))
                connect.commit()
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def delete_multipropietarios_antiguos(self, last_initial_year):
        print("SOY UN FURROOOOOOOOOOOOOOOOOOOO "+ str(last_initial_year))
        connect = self.connection()
        com_man_pred = self._construir_com_man_pred()
        try:
            with connect.cursor() as cursor:
                delete_vigencia_final_query = QUERY_DELETE_MULTIPROPIETARIOS.format(
                    last_initial_year=str(last_initial_year),
                    com_man_pred=com_man_pred
                )
                print("Number of rows modified: ", cursor.execute(delete_vigencia_final_query))
                connect.commit()
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def obtener_multipropietarios(self):
        com_man_pred = self._construir_com_man_pred()
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                multipropietario_sql = QUERY_OBTENER_MULTIPROPIETARIOS_SQL.format(com_man_pred=com_man_pred)
                cursor.execute(multipropietario_sql)
                multipropietarios = cursor.fetchall()
                return multipropietarios[0]['COUNT(*)']
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

#revisar

    #def _obtener_suma_porc_Dercho_enjantes(self, Run_Rut_enajenantes):
        print(Run_Rut_enajenantes)
        com_man_pred = self._construir_com_man_pred()
        runrut_enajenantes_formateado = formatear_runrut_enajenantes(Run_Rut_enajenantes)
        print("HOLAAAAAAAAAAAAAAAAAAAAAAAAAA"+runrut_enajenantes_formateado)
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                multipropietario_sql = QUERY_OBTENER_SUMA_PORC_DERECHO_SQL.format(
                com_man_pred=com_man_pred,
                run_rut_enajenantes=runrut_enajenantes_formateado
            )
                print("multipropietario_sql :" + multipropietario_sql)
                cursor.execute(multipropietario_sql)
                multipropietarios = cursor.fetchall()
                return int(multipropietarios[0]['sum'])
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close() 

    def _construir_com_man_pred(self):
        return f"{self.comuna}-{self.manzana}-{self.predio}"

    def _insert_enajenantes_to_multipropietarios(self, id_multipropietario, com_man_pred, enajenante):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                cursor.execute(QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIO_SQL, (
                    id_multipropietario,
                    com_man_pred,
                    enajenante['RUNRUT'],
                    enajenante['porcDerecho'],
                    self.fojas,
                    int(self.obtener_ano_inscripcion()),
                    self.numero_inscripcion,
                    self.fecha_inscripcion,
                    int(self.obtener_ano_inscripcion()),
                    None,
                    "Enajenante"
                ))
                connect.commit()
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _insert_adquirientes_to_multipropietarios(self, id_multipropietario, com_man_pred, adquirente):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                cursor.execute(QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIO_SQL, (
                    id_multipropietario,
                    com_man_pred,
                    adquirente['RUNRUT'],
                    adquirente['porcDerecho'],
                    self.fojas,
                    int(self.obtener_ano_inscripcion()),
                    self.numero_inscripcion,
                    self.fecha_inscripcion,
                    int(self.obtener_ano_inscripcion()),
                    None,
                    "Aquirente"
                ))
                connect.commit()
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _obtener_ultimo_ano_inicial(self):
        com_man_pred = self._construir_com_man_pred()
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                cursor.execute(QUERY_OBTENER_ULT_ANO_INIT.format(com_man_pred=com_man_pred)
                )
                last_initial_year_query = cursor.fetchall()
                return last_initial_year_query[0]['Ano']
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def agregar_nuevo_formulario(self):

        numero_de_atencion = self.add_formulario()
        self.add_enajenante(numero_de_atencion)
        self.add_adquirente(numero_de_atencion)
        self.add_multipropietario()

    def actualizar_vigencia(self, last_initial_year):
        self._actualizar_multipropietarios_por_vigencia(last_initial_year)

        numero_de_atencion = self.add_formulario()
        self.add_enajenante(numero_de_atencion)
        self.add_adquirente(numero_de_atencion)
        self.add_multipropietario() 
        return True

    def procesar_escenario_3(self, last_initial_year):
        pass

    def eliminar_antiguos_y_reemplazar(self, last_initial_year):
        self.delete_multipropietarios_antiguos(last_initial_year)
        numero_de_atencion = self.add_formulario()
        self.add_enajenante(numero_de_atencion)
        self.add_adquirente(numero_de_atencion)
        self.add_multipropietario() 

    def determinar_y_procesar_escenario(self):
        if(self.cne == COMPRAVENTA):
            pass#TODO

        if(self.cne == REGULARIZACION_DE_PATRIMONIO):
            count_multipropietario = self.obtener_multipropietarios()
            if(count_multipropietario == 0):#esta malo arreglar
                print("Escenario 1")
                self.agregar_nuevo_formulario()
            else:
                last_initial_year = self._obtener_ultimo_ano_inicial()
                if(last_initial_year < self.obtener_ano_inscripcion()):
                    print("Escenario 2")
                    self.actualizar_vigencia(last_initial_year)
                if(last_initial_year > self.obtener_ano_inscripcion()):
                    print("Es menor pero este escenario no esta listo")
                    self.procesar_escenario_3(last_initial_year)
                    #TODO
                if(last_initial_year == self.obtener_ano_inscripcion()):
                    print("Escenario 4")
                    self.eliminar_antiguos_y_reemplazar(last_initial_year)

    def ajustar_porcentajes_adquirentes(self):
        sum_porc_Derecho_adquirente = 0
        for adquirente in self.adquirentes_data:
            porc_Derecho = int(adquirente.get('porcDerecho'))
            if porc_Derecho is not None:
                sum_porc_Derecho_adquirente += porc_Derecho

        print("q pijas " + str(sum_porc_Derecho_adquirente))
        if sum_porc_Derecho_adquirente == 100:
            Run_Rut_enajenantes = [enajenante['RUNRUT'] for enajenante in self.enajenantes_data]
            if(Run_Rut_enajenantes != []):
                sum_porc_Derecho_enajenante = 0
                for enajenante in self.enajenantes_data:
                    porc_Derecho = int(enajenante.get('porcDerecho'))
                    if porc_Derecho is not None:
                        sum_porc_Derecho_enajenante += porc_Derecho
                for adquirente in self.adquirentes_data:
                    porc_Derecho = int(adquirente.get('porcDerecho'))
                    if porc_Derecho is not None:
                        print()
                        porc_Derecho *= sum_porc_Derecho_enajenante / 100
                        adquirente['porcDerecho'] = str(porc_Derecho)
                print(self.adquirentes_data)