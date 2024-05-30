from flask import request, jsonify
import json
import pymysql

INTERNAL_SERVER_ERROR = 500

class form_solver(): 
    def __init__(self, formulario, connection):
        self.formulario = formulario
        self.cne = formulario['CNE']
        self.comuna = formulario['bienRaiz']['comuna']
        self.manzana = formulario['bienRaiz']['manzana']
        self.predio = formulario['bienRaiz']['predio']
        self.fojas = formulario['fojas']
        self.fecha_inscripcion = formulario['fechaInscripcion']
        self.numero_inscripcion = formulario['nroInscripcion']
        self.numero_de_atencion = None
        self.connection = connection

        try:
            self.enajenantes_data = formulario['enajenantes']
        except:
            self.enajenantes_data = []
        try:
            self.adquirentes_data = formulario['adquirentes']
        except:
            self.adquirentes_data = []

    def execute_Select_query(self, query):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:   
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            raise e
        finally:
            connect.close()
    
    def execute_Update_query(self, query):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:   
                print("Number of rows modified: ", cursor.execute(query))
                connect.commit()
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def add_formulario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                
                formulario_sql = "SELECT * FROM formulario"
                cursor.execute(formulario_sql)
                formularios = cursor.fetchall()
                numero_de_atencion = len(formularios) + 1
                
                
                formulario_sql = """
                    INSERT INTO formulario (
                        Numero_de_atencion, CNE, Comuna, Manzana, Predio, Fojas, Fecha_de_inscripcion, Numero_de_insripcion
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(formulario_sql, (
                    numero_de_atencion, 
                    self.cne, 
                    self.comuna, 
                    self.manzana, 
                    self.predio, 
                    self.fojas, 
                    self.fecha_inscripcion, 
                    self.numero_inscripcion
                ))
            self.numero_de_atencion = numero_de_atencion
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
                enajenante_sql = "SELECT * FROM enajenantes"
                cursor.execute(enajenante_sql)
                enajenantes = cursor.fetchall()
                id = len(enajenantes) + 1
                # Insert enajenantes data into the 'enajenantes' table
                for num_enajenante, enajenante in enumerate(self.enajenantes_data):
                    enajenante_sql = """
                        INSERT INTO enajenantes (id, enajenante_id, RUNRUT, porcDerecho)
                        VALUES ( %s, %s, %s, %s)
                    """
                    cursor.execute(enajenante_sql, (
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
                adquirente_sql = "SELECT * FROM Adquirentes"
                cursor.execute(adquirente_sql)
                adquirentes = cursor.fetchall()
                id = len(adquirentes) + 1
                # Insert adquirentes data into the 'Adquirentes' table
                for num_adquirente, adquirente in enumerate(self.adquirentes_data):
                    adquirente_sql = """
                        INSERT INTO Adquirentes (id, Adquirente_id, RUNRUT, porcDerecho)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(adquirente_sql, (
                        (id + num_adquirente),
                        numero_de_atencion, 
                        adquirente['RUNRUT'], 
                        adquirente['porcDerecho']
                    ))
                connect.commit()
            return "Ingreso el Adquirente"
        except Exception as e:
            connect.rollback()
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def add_multipropietario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                id_multipropietario = self._obtener_siguiente_id_multipropietario(cursor)
                com_man_pred = self._construir_com_man_pred()

                for enajenante in self.enajenantes_data:
                    self._insertar_enajenante(cursor, id_multipropietario, com_man_pred, enajenante)
                    id_multipropietario += 1

                for adquirente in self.adquirentes_data:
                    self._insertar_adquirente(cursor, id_multipropietario, com_man_pred, adquirente)
                    id_multipropietario += 1

                connect.commit()

        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def _obtener_siguiente_id_multipropietario(self, cursor):
        multipropietario_sql = "SELECT id FROM Multipropietarios ORDER BY id DESC LIMIT 1"
        cursor.execute(multipropietario_sql)
        id_multipropietario = cursor.fetchall()
        return id_multipropietario[0]["id"] + 1 if id_multipropietario else 0

    def _construir_com_man_pred(self):
        return f"{self.comuna}-{self.manzana}-{self.predio}"

    def _insertar_enajenante(self, cursor, id_multipropietario, com_man_pred, enajenante):
        enajenante_sql = """
            INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho,
                                        Fojas, Ano_inscripcion, Numero_inscripcion,
                                        Fecha_de_inscripcion, Ano_vigencia_inicial,
                                        Ano_vigencia_final, Tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(enajenante_sql, (
            id_multipropietario,
            com_man_pred,
            enajenante['RUNRUT'],
            enajenante['porcDerecho'],
            self.fojas,
            int(self.fecha_inscripcion[0:4]),
            self.numero_inscripcion,
            self.fecha_inscripcion,
            int(self.fecha_inscripcion[0:4]),
            None,
            "Enajenante"
        ))

    def _insertar_adquirente(self, cursor, id_multipropietario, com_man_pred, adquirente):
        adquirente_sql = """
            INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho,
                                        Fojas, Ano_inscripcion, Numero_inscripcion,
                                        Fecha_de_inscripcion, Ano_vigencia_inicial,
                                        Ano_vigencia_final, Tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(adquirente_sql, (
            id_multipropietario,
            com_man_pred,
            adquirente['RUNRUT'],
            adquirente['porcDerecho'],
            self.fojas,
            int(self.fecha_inscripcion[0:4]),
            self.numero_inscripcion,
            self.fecha_inscripcion,
            int(self.fecha_inscripcion[0:4]),
            None,
            "Aquirente"
        ))


    def agregar_nuevo_formulario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                numero_de_atencion = self.add_formulario()
                self.add_enajenante(numero_de_atencion)
                self.add_adquirente(numero_de_atencion)
                self.add_multipropietario()
                return True
        except Exception as e:
            connect.rollback()
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def actualizar_vigencia(self, last_initial_year):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
                update_vigencia_final_query = "UPDATE Multipropietarios SET Ano_vigencia_final=" + str(int(self.fecha_inscripcion[0:4]) - 1) + " WHERE Ano_vigencia_inicial=" + str(last_initial_year) + " AND Ano_vigencia_final IS NULL AND com_man_pred=" + '\'' + com_man_pred + '\''
                self.execute_Update_query(update_vigencia_final_query)

                numero_de_atencion = self.add_formulario()
                self.add_enajenante(numero_de_atencion)
                self.add_adquirente(numero_de_atencion)
                self.add_multipropietario() 
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()

    def procesar_escenario_3(self, last_initial_year):
        pass

    def eliminar_antiguos_y_reemplazar(self, last_initial_year):
        pass
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
                delete_vigencia_final_query = "DELETE FROM Multipropietarios WHERE Ano_vigencia_inicial=" + str(last_initial_year) + " AND com_man_pred=" + '\'' + com_man_pred + '\''
                self.execute_Update_query(delete_vigencia_final_query)
                print("aqui")
                numero_de_atencion = self.add_formulario()
                self.add_enajenante(numero_de_atencion)
                self.add_adquirente(numero_de_atencion)
                self.add_multipropietario() 
                print("aqui 2")
                return True
        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), INTERNAL_SERVER_ERROR
        finally:
            connect.close()


    def determinar_y_procesar_escenario(self):
        if(self.cne == 8):
            pass

        if(self.cne == 99):
            com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
            count_multipropietario = "SELECT COUNT(*) FROM Multipropietarios WHERE com_man_pred=" + '\'' + com_man_pred + '\''
            if(self.execute_Select_query(count_multipropietario)[0]['COUNT(*)'] == 0):
                print("Escenario 1")
                self.agregar_nuevo_formulario()
            else:
                com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
                last_initial_year_query = "SELECT Ano_vigencia_inicial AS Ano FROM Multipropietarios WHERE com_man_pred=" + '\'' + com_man_pred + '\'' + " ORDER BY Ano_vigencia_inicial DESC LIMIT 1"
                last_initial_year = self.execute_Select_query(last_initial_year_query)[0]['Ano']
                if(last_initial_year < int(self.fecha_inscripcion[0:4])):
                    print("Escenario 2")
                    self.actualizar_vigencia(last_initial_year)
                if(last_initial_year > int(self.fecha_inscripcion[0:4])):
                    print("Es menor pero este escenario no esta listo")
                    self.scenario_3(last_initial_year)
                if(last_initial_year == int(self.fecha_inscripcion[0:4])):
                    print("Escenario 4")
                    self.eliminar_antiguos_y_reemplazar(last_initial_year)

    def ajustar_porcentajes_adquirentes(self):
        sum_porc_Derecho_adquirente = 0
        for adquirente in self.adquirentes_data:
            porc_Derecho = adquirente.get('porcDerecho')
            if porc_Derecho is not None:
                sum_porc_Derecho_adquirente += porc_Derecho

        print(sum_porc_Derecho_adquirente)
        if sum_porc_Derecho_adquirente == 100:
            com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
            Run_Rut_enajenantes = [enajenante['RUNRUT'] for enajenante in self.enajenantes_data]
            sum_porc_Derecho_enajenante_query = "SELECT SUM(porcDerecho) as sum FROM Multipropietarios WHERE com_man_pred=" + '\'' + com_man_pred + '\'' + " AND RUNRUT IN " + str(Run_Rut_enajenantes).replace("[", "(").replace("]", ")")
            print(sum_porc_Derecho_enajenante_query)
            sum_porc_Derecho_enajenante = int(self.execute_Select_query(sum_porc_Derecho_enajenante_query)[0]['sum'])
            print(sum_porc_Derecho_enajenante)
            for adquirente in self.adquirentes_data:
                porc_Derecho = adquirente.get('porcDerecho')
                if porc_Derecho is not None:
                    adquirente['porcDerecho'] *= sum_porc_Derecho_enajenante / 100
            print(self.adquirentes_data)