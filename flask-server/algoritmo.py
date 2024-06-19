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
            
    def _ejecutar_query(self, cursor, query):
        cursor.execute(query)
        return cursor.fetchall()

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
                ano_final = self._obtener_ano_final()
                query_multipropietarios = self._construir_query_actualizar_multipropietarios(ano_final, last_initial_year_in, com_man_pred)
                self._ejecutar_query_actualizar_multipropietarios(cursor, query_multipropietarios)
                connect.commit()
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _obtener_ano_final(self):
        return self.obtener_ano_inscripcion() - 1

    def _construir_query_actualizar_multipropietarios(self, ano_final, last_initial_year, com_man_pred):
        return QUERY_UPDATE_MULTIPROPIETARIO_SQL.format(
            ano_final=ano_final,
            last_initial_year=last_initial_year,
            com_man_pred=com_man_pred
        )

    def _ejecutar_query_actualizar_multipropietarios(self, cursor, query):
        print("Number of rows modified: ", cursor.execute(query))


#revisar SUS METODOS ---
    def delete_multipropietarios_antiguos(self, last_initial_year):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = self._construir_com_man_pred()
                delete_vigencia_final_query = self._construir_query_delete_multipropietarios(last_initial_year, com_man_pred)
                self._ejecutar_query(cursor, delete_vigencia_final_query)
                connect.commit()
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _construir_query_delete_multipropietarios(self, last_initial_year, com_man_pred):
        return QUERY_DELETE_MULTIPROPIETARIOS.format(
            last_initial_year=str(last_initial_year),
            com_man_pred=com_man_pred
        )


    def obtener_multipropietarios(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = self._construir_com_man_pred()
                multipropietario_sql = self._construir_query_obtener_multipropietarios(com_man_pred)
                multipropietarios = self._ejecutar_query(cursor, multipropietario_sql)
                return self._obtener_count_multipropietarios(multipropietarios)
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()
    
    def _construir_query_obtener_multipropietarios(self, com_man_pred):
        return QUERY_OBTENER_MULTIPROPIETARIOS_SQL.format(com_man_pred=com_man_pred)

    def _obtener_count_multipropietarios(self, multipropietarios):
        return multipropietarios[0]['COUNT(*)']
#End revisar SUS metodos ---


    def _construir_com_man_pred(self):
        return f"{self.comuna}-{self.manzana}-{self.predio}"

    def _insert_enajenantes_to_multipropietarios(self, id_multipropietario, com_man_pred, enajenante):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                query = self._construir_query_insertar_enajenantes(id_multipropietario, com_man_pred, enajenante)
                self._ejecutar_query(cursor, query)
                connect.commit()
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _construir_query_insertar_enajenantes(self, id_multipropietario, com_man_pred, enajenante):
        return QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIO_SQL, (
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
        )

    def _insert_adquirientes_to_multipropietarios(self, id_multipropietario, com_man_pred, adquirente):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                query = self._construir_query_insertar_adquirientes(id_multipropietario, com_man_pred, adquirente)
                self._ejecutar_query(cursor, query)
                connect.commit()
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _construir_query_insertar_adquirientes(self, id_multipropietario, com_man_pred, adquirente):
        return QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIO_SQL, (
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
        )

    def _obtener_ultimo_ano_inicial(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = self._construir_com_man_pred()
                query = self._construir_query_obtener_ultimo_ano_inicial(com_man_pred)
                last_initial_year_query = self._ejecutar_query(cursor, query)
                return self._obtener_ano_desde_query(last_initial_year_query)
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _construir_query_obtener_ultimo_ano_inicial(self, com_man_pred):
        return QUERY_OBTENER_ULT_ANO_INIT.format(com_man_pred=com_man_pred)

    def _obtener_ano_desde_query(self, query_result):
        return query_result[0]['Ano']


    def agregar_nuevo_formulario(self):
        numero_de_atencion = self.add_formulario()
        self.add_all(numero_de_atencion)

    def actualizar_vigencia(self, last_initial_year):
        self._actualizar_multipropietarios_por_vigencia(last_initial_year)

        numero_de_atencion = self.add_formulario()
        self.add_all(numero_de_atencion)
        return True

    def procesar_escenario_3(self, last_initial_year):
        pass

    def eliminar_antiguos_y_reemplazar(self, last_initial_year):
        self.delete_multipropietarios_antiguos(last_initial_year)
        numero_de_atencion = self.add_formulario()
        self.add_all(numero_de_atencion)

    def add_all(self, numero_de_atencion):
        self.add_enajenante(numero_de_atencion)
        self.add_adquirente(numero_de_atencion)
        self.add_multipropietario()

    def determinar_y_procesar_escenario(self):
        if self.cne == COMPRAVENTA:
            self.procesar_escenario_compraventa()
        elif self.cne == REGULARIZACION_DE_PATRIMONIO:
            self.procesar_escenario_regularizacion_patrimonio()

    def procesar_escenario_compraventa(self):
        # TODO: Implementar lógica para el escenario de compraventa
        pass

    def procesar_escenario_regularizacion_patrimonio(self):
        count_multipropietario = self.obtener_multipropietarios()
        if count_multipropietario == 0:
            self.procesar_escenario_1()
        else:
            last_initial_year = self._obtener_ultimo_ano_inicial()
            if last_initial_year < self.obtener_ano_inscripcion():
                self.procesar_escenario_2(last_initial_year)
            elif last_initial_year > self.obtener_ano_inscripcion():
                self.procesar_escenario_3(last_initial_year)
            else:
                self.procesar_escenario_4(last_initial_year)

    def procesar_escenario_1(self):
        print("Escenario 1")
        self.agregar_nuevo_formulario()

    def procesar_escenario_2(self, last_initial_year):
        print("Escenario 2")
        self.actualizar_vigencia(last_initial_year)

    def procesar_escenario_3(self, last_initial_year):
        print("Es menor pero este escenario no esta listo")
        # TODO: Implementar lógica para el escenario 3
        pass

    def procesar_escenario_4(self, last_initial_year):
        print("Escenario 4")
        self.eliminar_antiguos_y_reemplazar(last_initial_year)

    def ajustar_porcentajes_adquirentes(self):
        sum_porc_derecho_adquirente = self._calcular_suma_porc_derecho_adquirente()
        print("Suma de porcentajes de derecho de adquirentes: " + str(sum_porc_derecho_adquirente))

        if sum_porc_derecho_adquirente == 100:
            run_rut_enajenantes = self._obtener_run_rut_enajenantes()
            if run_rut_enajenantes:
                sum_porc_derecho_enajenante = self._calcular_suma_porc_derecho_enajenante()
                self._ajustar_porc_derecho_adquirentes(sum_porc_derecho_enajenante)
                print(self.adquirentes_data)

    def _calcular_suma_porc_derecho_adquirente(self):
        return sum(int(adquirente.get('porcDerecho', 0)) for adquirente in self.adquirentes_data)

    def _obtener_run_rut_enajenantes(self):
        return [enajenante['RUNRUT'] for enajenante in self.enajenantes_data]

    def _calcular_suma_porc_derecho_enajenante(self):
        return sum(int(enajenante.get('porcDerecho', 0)) for enajenante in self.enajenantes_data)

    def _ajustar_porc_derecho_adquirentes(self, sum_porc_derecho_enajenante):
        for adquirente in self.adquirentes_data:
            porc_derecho = int(adquirente.get('porcDerecho', 0))
            if porc_derecho != 0:
                adquirente['porcDerecho'] = str(porc_derecho * sum_porc_derecho_enajenante / 100)
