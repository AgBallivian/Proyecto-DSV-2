# from flask import jsonify
# from Queries import (
#     QUERY_ALL_FORMULARIOS, QUERY_INSERTAR_FORM, INTERNAL_SERVER_ERROR,
#     QUERY_ALL_ENAJENANTES, QUERY_INSERTAR_ENAJENANTES, QUERY_ALL_ADQUIRENTES,
#     QUERY_INSERTAR_ADQUIRENTES, QUERY_ID_MULTIPROPIETARIOS,
#     QUERY_UPDATE_MULTIPROPIETARIO_SQL, QUERY_DELETE_MULTIPROPIETARIOS,
#     QUERY_OBTENER_MULTIPROPIETARIOS_SQL, QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIO_SQL,
#     QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIO_SQL,
#     COMPRAVENTA, REGULARIZACION_DE_PATRIMONIO, QUERY_OBTENER_ULT_ANO_INIT
#     )
from DBmanager import _obtener_siguiente_id_multipropietario, _insert_enajenantes_to_multipropietarios, _insert_adquirientes_to_multipropietarios, obtener_multipropietarios, add_formulario, add_enajenante, add_adquirente
from utils import _construir_com_man_pred

# ERROR_MESSAGE = "Error "
COMPRAVENTA = 8
REGULARIZACION_DE_PATRIMONIO = 99

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

        if formulario['enajenantes'] != []:
            self.enajenantes_data = formulario['enajenantes']
        else:
            self.enajenantes_data = []
        if formulario['adquirentes'] != []:
            self.adquirentes_data = formulario['adquirentes']
        else:
            self.adquirentes_data = []


    # def _ejecutar_query(self, cursor, query):
    #     cursor.execute(query)
    #     return cursor.fetchall()

    # def obtener_numer_de_atencion(self):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             cursor.execute(QUERY_ALL_FORMULARIOS)
    #             formularios = cursor.fetchall()
    #             return len(formularios)
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         raise e
    #     finally:
    #         connect.close()

    # def add_formulario(self):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             cursor.execute(QUERY_ALL_FORMULARIOS)
    #             formularios = cursor.fetchall()
    #             numero_de_atencion = len(formularios) + 1
    #             print(3)
    #             cursor.execute(QUERY_INSERTAR_FORM, (
    #                 numero_de_atencion,
    #                 self.cne,
    #                 self.comuna,
    #                 self.manzana,
    #                 self.predio,
    #                 self.fojas,
    #                 self.fecha_inscripcion,
    #                 self.numero_inscripcion
    #             ))
    #         connect.commit()
    #         return numero_de_atencion
    #     except Exception as e:
    #         connect.rollback()
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def add_enajenante(self, numero_de_atencion):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             #Obtain next id from 'enajenantes' table
    #             cursor.execute(QUERY_ALL_ENAJENANTES)
    #             enajenantes = cursor.fetchall()
    #             enjante_id = len(enajenantes) + 1
    #             # Insert enajenantes data into the 'enajenantes' table
    #             for num_enajenante, enajenante in enumerate(self.enajenantes_data):
    #                 cursor.execute(QUERY_INSERTAR_ENAJENANTES, (
    #                     (enjante_id + num_enajenante),
    #                     numero_de_atencion,
    #                     enajenante['RUNRUT'],
    #                     enajenante['porcDerecho']
    #             ))
    #         connect.commit()
    #         return "Ingreso el enajenante"
    #     except Exception as e:
    #         connect.rollback()
    #         print("Error: ", str(e))
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def add_adquirente(self, numero_de_atencion):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             #Obtain next id from 'Adquirentes' table
    #             cursor.execute(QUERY_ALL_ADQUIRENTES)
    #             adquirentes = cursor.fetchall()
    #             adquirentes_id = len(adquirentes) + 1
    #             # Insert adquirentes data into the 'Adquirentes' table
    #             for num_adquirente, adquirente in enumerate(self.adquirentes_data):
    #                 cursor.execute(QUERY_INSERTAR_ADQUIRENTES, (
    #                     (adquirentes_id + num_adquirente),
    #                     numero_de_atencion,
    #                     adquirente['RUNRUT'],
    #                     int(adquirente['porcDerecho'])
    #                 ))
    #             connect.commit()
    #         return "Ingreso el Adquirente"
    #     except Exception as e:
    #         connect.rollback()
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def add_multipropietario(self):
    #     id_multipropietario = self._obtener_siguiente_id_multipropietario()
    #     com_man_pred = self._construir_com_man_pred()

    #     for enajenante in self.enajenantes_data:
    #         self._insert_enajenantes_to_multipropietarios(id_multipropietario,
    #          com_man_pred, enajenante)
    #         id_multipropietario += 1

    #     for adquirente in self.adquirentes_data:
    #         self._insert_adquirientes_to_multipropietarios(id_multipropietario, com_man_pred, adquirente)
    #         id_multipropietario += 1
    # def obtener_ano_inscripcion(self):
    #     return int(self.fecha_inscripcion.split("-")[0])

    # def _obtener_siguiente_id_multipropietario(self):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             cursor.execute(QUERY_ID_MULTIPROPIETARIOS)
    #             id_multipropietario = cursor.fetchall()
    #             return id_multipropietario[0]["id"] + 1 if id_multipropietario else 0
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()
    

    def _ejecutar_query(self, cursor, query):
        cursor.execute(query)
        return cursor.fetchall()
    
    def obtener_formulario(self, numero_de_atencion):
        connect = self.connection()
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



#Revisar
    # def _actualizar_multipropietarios_por_vigencia(self, last_initial_year_in):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             com_man_pred = self._construir_com_man_pred()
    #             ano_final = self._obtener_ano_final()
    #             query_multipropietarios = self._construir_query_actualizar_multipropietarios(ano_final, last_initial_year_in, com_man_pred)
    #             self._ejecutar_query_actualizar_multipropietarios(cursor, query_multipropietarios)
    #             connect.commit()
    #             return True
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def _obtener_ano_final(self):
    #     return self.obtener_ano_inscripcion() - 1

    # def _construir_query_actualizar_multipropietarios(self, ano_final, last_initial_year, com_man_pred):
    #     return QUERY_UPDATE_MULTIPROPIETARIO_SQL.format(
    #         ano_final=ano_final,
    #         last_initial_year=last_initial_year,
    #         com_man_pred=com_man_pred
    #     )

    # def _ejecutar_query_actualizar_multipropietarios(self, cursor, query):
    #     print("Number of rows modified: ", cursor.execute(query))


#revisar SUS METODOS ---
    # def delete_multipropietarios_antiguos(self, last_initial_year):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             com_man_pred = self._construir_com_man_pred()
    #             delete_vigencia_final_query = self._construir_query_delete_multipropietarios(last_initial_year, com_man_pred)
    #             self._ejecutar_query(cursor, delete_vigencia_final_query)
    #             connect.commit()
    #             return True
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def _construir_query_delete_multipropietarios(self, last_initial_year, com_man_pred):
    #     return QUERY_DELETE_MULTIPROPIETARIOS.format(
    #         last_initial_year=str(last_initial_year),
    #         com_man_pred=com_man_pred
    #     )


    # def obtener_multipropietarios(self):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             com_man_pred = self._construir_com_man_pred()
    #             multipropietario_sql = self._construir_query_obtener_multipropietarios(com_man_pred)
    #             multipropietarios = self._ejecutar_query(cursor, multipropietario_sql)
    #             return self._obtener_count_multipropietarios(multipropietarios)
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()
    # def _construir_query_obtener_multipropietarios(self, com_man_pred):
    #     return QUERY_OBTENER_MULTIPROPIETARIOS_SQL.format(com_man_pred=com_man_pred)

    # def _obtener_count_multipropietarios(self, multipropietarios):
    #     return multipropietarios[0]['COUNT(*)']
#End revisar SUS metodos ---

    def add_multipropietario(self):
        id_multipropietario = _obtener_siguiente_id_multipropietario()
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)

        for enajenante in self.enajenantes_data:
            _insert_enajenantes_to_multipropietarios(id_multipropietario,
                com_man_pred, enajenante, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_multipropietario += 1

        for adquirente in self.adquirentes_data:
            _insert_adquirientes_to_multipropietarios(id_multipropietario,
                com_man_pred, adquirente, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_multipropietario += 1


    # def _construir_com_man_pred(self):
    #     return f"{self.comuna}-{self.manzana}-{self.predio}"

    # def _insert_enajenantes_to_multipropietarios(self, id_multipropietario, com_man_pred, enajenante):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             query = self._construir_query_insertar_enajenantes(id_multipropietario, com_man_pred, enajenante)
    #             self._ejecutar_query(cursor, query)
    #             connect.commit()
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def _construir_query_insertar_enajenantes(self, id_multipropietario, com_man_pred, enajenante):
    #     return QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIO_SQL, (
    #         id_multipropietario,
    #         com_man_pred,
    #         enajenante['RUNRUT'],
    #         enajenante['porcDerecho'],
    #         self.fojas,
    #         int(self.obtener_ano_inscripcion()),
    #         self.numero_inscripcion,
    #         self.fecha_inscripcion,
    #         int(self.obtener_ano_inscripcion()),
    #         None,
    #         "Enajenante"
    #     )

    # def _insert_adquirientes_to_multipropietarios(self, id_multipropietario, com_man_pred, adquirente):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             query = self._construir_query_insertar_adquirientes(id_multipropietario, com_man_pred, adquirente)
    #             self._ejecutar_query(cursor, query)
    #             connect.commit()
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def _construir_query_insertar_adquirientes(self, id_multipropietario, com_man_pred, adquirente):
    #     return QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIO_SQL, (
    #         id_multipropietario,
    #         com_man_pred,
    #         adquirente['RUNRUT'],
    #         adquirente['porcDerecho'],
    #         self.fojas,
    #         int(self.obtener_ano_inscripcion()),
    #         self.numero_inscripcion,
    #         self.fecha_inscripcion,
    #         int(self.obtener_ano_inscripcion()),
    #         None,
    #         "Aquirente"
    #     )

    # def _obtener_ultimo_ano_inicial(self):
    #     connect = self.connection()
    #     try:
    #         with connect.cursor() as cursor:
    #             com_man_pred = self._construir_com_man_pred()
    #             query = self._construir_query_obtener_ultimo_ano_inicial(com_man_pred)
    #             last_initial_year_query = self._ejecutar_query(cursor, query)
    #             return self._obtener_ano_desde_query(last_initial_year_query)
    #     except Exception as e:
    #         connect.rollback()
    #         print(ERROR_MESSAGE, e)
    #         return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
    #     finally:
    #         connect.close()

    # def _construir_query_obtener_ultimo_ano_inicial(self, com_man_pred):
    #     return QUERY_OBTENER_ULT_ANO_INIT.format(com_man_pred=com_man_pred)

    # def _obtener_ano_desde_query(self, query_result):
    #     return query_result[0]['Ano']


    def agregar_nuevo_formulario(self):
        numero_de_atencion = add_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
        self.add_all(numero_de_atencion)

    def actualizar_vigencia(self, last_initial_year):
        self._actualizar_multipropietarios_por_vigencia(last_initial_year)

        numero_de_atencion = add_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
        self.add_all(numero_de_atencion)
        return True

    def eliminar_antiguos_y_reemplazar(self, last_initial_year):
        self.delete_multipropietarios_antiguos(last_initial_year)
        numero_de_atencion = add_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
        self.add_all(numero_de_atencion)

    def add_all(self, numero_de_atencion):
        for enajenante in self.enajenantes_data:
            add_enajenante(numero_de_atencion, enajenante['RUNRUT'], enajenante['porcDerecho'])
        for adquirente in self.adquirentes_data:
            add_adquirente(numero_de_atencion, adquirente['RUNRUT'], adquirente['porcDerecho'])
        self.add_multipropietario()
        # self.handle_enajenante_fantasma()
        

    def determinar_y_procesar_escenario(self):
        if self.cne == COMPRAVENTA:
            self.procesar_escenario_compraventa()
        elif self.cne == REGULARIZACION_DE_PATRIMONIO:
            self._procesar_escenario_regularizacion_patrimonio()

    def get_total_perc(transactions):
        total = 0
        for transaction in transactions:
            total += transaction['porcDerecho']
        return total
    
    def procesar_escenario_compraventa(self):
        # TODO: Implementar lógica para el escenario de compraventa
        #Cne = 8
        #fecha de vigencia del form ya subido < a la fecha de inscripcion del nuevo form.
        
        if(self._obtener_ano_final() < self.fecha_inscripcion):
            #evaluar escenario 1 y 2

            total_porc_enajenantes = self.get_total_perc(self.enajenantes_data)
            total_porc_adquirentes = self.get_total_perc(self.adquirentes_data)

            primer_caso = True if total_porc_adquirentes == 100 else False
            segundo_caso = True if total_porc_adquirentes == 0 else False
            tercer_caso = (len(self.enajenantes_data) == 1) and (len(self.adquirentes_data) == 1)


            if(primer_caso or segundo_caso):
                porcentaje_igual = total_porc_enajenantes / len(self.adquirentes_data)

                for adquirente in self.adquirentes_data:
                    if primer_caso:
                        adquirente["porDerecho"] = adquirente["porDerecho"] * (total_porc_enajenantes / 100)
                    elif segundo_caso:
                        adquirente.percentage = porcentaje_igual
            elif(tercer_caso):
                #agarrar los primeros de ambos enajenente y adquirientes y darle el porcentaje respectivo al adquirentes y restarle al enajenente
                adquirente = self.adquirentes_data[0]
                enajenante = self.enajenantes_data[0]
                #aqui necesito restar enajenante del form viejo con adquirente del form nuevo
                numero_de_atencion = self._construir_com_man_pred()
                form = self.obtener_formulario(numero_de_atencion)
                porcentaje = form["enajenante"]["porcDerecho"] * adquirente["porcDerecho"] / 100
                enajenante["porcDerecho"] = enajenante["porcDerecho"] - porcentaje
                adquirente["porcDerecho"] = porcentaje

            else:
                for dueños in form["enajenante"]:
                    for vendiendo in self.enajenantes_data:
                        if dueños["RUNRUT"] == vendiendo["RUNRUT"]:
                            dueños["porDerecho"] -= vendiendo["porDerecho"]
                            if dueños["porDerecho"] <= 0:
                                #borrar al dueño que tiene 0 porcentaje de derechos
                                pass




    def _procesar_escenario_regularizacion_patrimonio(self):

        count_multipropietario = obtener_multipropietarios(self.comuna, self.manzana, self.predio)

        count_multipropietario = self.obtener_multipropietarios()
        print(count_multipropietario)

        if count_multipropietario == 0:
            self.procesar_escenario_1()
        else:
            last_initial_year = self._obtener_ultimo_ano_inicial()
            if last_initial_year < self.obtener_ano_inscripcion():
                self.procesar_escenario_2(last_initial_year)
            elif last_initial_year > self.obtener_ano_inscripcion():
                #self.procesar_escenario_3(last_initial_year)
                pass
            else:
                self.procesar_escenario_4(last_initial_year)

    def procesar_escenario_1(self):
        print("Escenario 1")
        self.agregar_nuevo_formulario()

    def procesar_escenario_2(self, last_initial_year):
        print("Escenario 2")
        self.actualizar_vigencia(last_initial_year)

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
    
    def handle_enajenante_fantasma(self):
        # Check if there is an "enajenante fantasma" (0% ownership)
        enajenante_fantasma = next((enajenante for enajenante in self.enajenantes_data if int(enajenante['porcDerecho']) == 0), None)

        if enajenante_fantasma:
            # Calculate the sum of ownership percentages
            sum_porc_derecho = sum(int(enajenante['porcDerecho']) for enajenante in self.enajenantes_data if int(enajenante['porcDerecho']) != 0) + sum(int(adquirente['porcDerecho']) for adquirente in self.adquirentes_data)

            if sum_porc_derecho > 100:
                # Prorate the ownership percentages
                self.prorate_ownership_percentages(sum_porc_derecho)
                self.remove_owners_with_zero_ownership()
            elif sum_porc_derecho < 100:
                # Distribute the remaining percentage
                remaining_percentage = 100 - sum_porc_derecho
                self.distribute_remaining_percentage(remaining_percentage)

            # Adjust the ownership percentages of the adquirentes
            self.ajustar_porcentajes_adquirentes()

        # Add the processed data to the database
        self.add_all(...)

    def prorate_ownership_percentages(self, sum_porc_derecho):
        # Scale down the ownership percentages proportionally
        for enajenante in self.enajenantes_data:
            if int(enajenante['porcDerecho']) != 0:
                enajenante['porcDerecho'] = str(int(enajenante['porcDerecho']) * 100 / sum_porc_derecho)

        for adquirente in self.adquirentes_data:
            adquirente['porcDerecho'] = str(int(adquirente['porcDerecho']) * 100 / sum_porc_derecho)

    def remove_owners_with_zero_ownership(self):
        self.enajenantes_data = [enajenante for enajenante in self.enajenantes_data if int(enajenante['porcDerecho']) != 0]
        self.adquirentes_data = [adquirente for adquirente in self.adquirentes_data if int(adquirente['porcDerecho']) != 0]

    def distribute_remaining_percentage(self, remaining_percentage):
        owners_with_zero_ownership = [enajenante for enajenante in self.enajenantes_data if int(enajenante['porcDerecho']) == 0] + [adquirente for adquirente in self.adquirentes_data if int(adquirente['porcDerecho']) == 0]
        num_owners_with_zero_ownership = len(owners_with_zero_ownership)

        if num_owners_with_zero_ownership > 0:
            portion = remaining_percentage / num_owners_with_zero_ownership
            for owner in owners_with_zero_ownership:
                owner['porcDerecho'] = str(portion)

"""
def procesar_escenario_3(self, last_initial_year):
        # 1. Select the multipropietario record(s) registered after the new form's year and store them in a temporary object or variable.
        old_records = self.select_multipropietarios_after_year(last_initial_year)

        # 2. Delete from the Multipropietarios table the records that have an Ano_vigencia_inicial greater than or equal to the new form's year.
        self.delete_multipropietarios_antiguos(last_initial_year)

        # 3. Re-process the forms in chronological order, including the old form (stored in the temporary object) and the new form(s).
        processed_records = []
        processed_records.extend(old_records)
        new_record = self.process_new_form()
        processed_records.append(new_record)

        # 4. Insert the re-processed form data (including the old form and the new form(s)) into the Multipropietarios table.
        self.insert_multipropietarios(processed_records)

    def select_multipropietarios_after_year(self, last_initial_year):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = self._construir_com_man_pred()
                query = f"SELECT * FROM Multipropietarios WHERE Ano_vigencia_inicial >= {last_initial_year} AND com_man_pred = '{com_man_pred}' ORDER BY Ano_vigencia_inicial ASC"
                cursor.execute(query)
                old_records = cursor.fetchall()
                return old_records
        except Exception as e:
            connect.rollback()
            print(ERROR_MESSAGE, str(e))
            return []
        finally:
            connect.close()

    def _delete_multipropietarios_antiguos(self, last_initial_year):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = self._construir_com_man_pred()
                query = QUERY_DELETE_MULTIPROPIETARIOS.format(last_initial_year=last_initial_year, com_man_pred=com_man_pred)
                cursor.execute(query)
            connect.commit()
        except Exception as e:
            connect.rollback()
            print(ERROR_MESSAGE, str(e))
        finally:
            connect.close()

    def _process_new_form(self):
        # Implement the logic to process the new form data
        # Set Ano_vigencia_final to self.obtener_ano_inscripcion() - 1
        new_record = {
            'com_man_pred': self._construir_com_man_pred(),
            'RUNRUT': None,  # Set RUNRUT for each enajenante/adquirente
            'porcDerecho': None,  # Set porcDerecho for each enajenante/adquirente
            'Fojas': self.fojas,
            'Ano_inscripcion': self.obtener_ano_inscripcion(),
            'Numero_inscripcion': self.numero_inscripcion,
            'Fecha_de_inscripcion': self.fecha_inscripcion,
            'Ano_vigencia_inicial': self.obtener_ano_inscripcion(),
            'Ano_vigencia_final': self.obtener_ano_inscripcion() - 1,
            'Tipo': None  # Set 'Enajenante' or 'Adquirente'
        }

        # Process enajenantes
        for enajenante in self.enajenantes_data:
            enajenante_record = new_record.copy()
            enajenante_record['RUNRUT'] = enajenante['RUNRUT']
            enajenante_record['porcDerecho'] = enajenante['porcDerecho']
            enajenante_record['Tipo'] = 'Enajenante'
            # Add enajenante_record to the list of processed records

        # Process adquirentes
        for adquirente in self.adquirentes_data:
            adquirente_record = new_record.copy()
            adquirente_record['RUNRUT'] = adquirente['RUNRUT']
            adquirente_record['porcDerecho'] = adquirente['porcDerecho']
            adquirente_record['Tipo'] = 'Adquirente'
            # Add adquirente_record to the list of processed records

        return processed_records

    def insert_multipropietarios(self, processed_records):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                for record in processed_records:
                    query = f"INSERT INTO Multipropietarios (com_man_pred, RUNRUT, porcDerecho, Fojas, Ano_inscripcion, Numero_inscripcion, Fecha_de_inscripcion, Ano_vigencia_inicial, Ano_vigencia_final, Tipo) VALUES ('{record['com_man_pred']}', '{record['RUNRUT']}', {record['porcDerecho']}, {record['Fojas']}, {record['Ano_inscripcion']}, {record['Numero_inscripcion']}, '{record['Fecha_de_inscripcion']}', {record['Ano_vigencia_inicial']}, {record['Ano_vigencia_final']}, '{record['Tipo']}')"
                    cursor.execute(query)
            connect.commit()
        except Exception as e:
            connect.rollback()
            print("Error: ", str(e))
        finally:
            connect.close()
"""