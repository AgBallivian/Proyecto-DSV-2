from flask import request, jsonify
import json
import pymysql


class form_solver(): 
    def __init__(self, formulario, connection):
        self.formulario = formulario
            # Extract the form data from the JSON object
        self.cne = formulario['CNE']
        self.comuna = formulario['bienRaiz']['comuna']
        self.manzana = formulario['bienRaiz']['manzana']
        self.predio = formulario['bienRaiz']['predio']
        self.fojas = formulario['fojas']
        self.fecha_inscripcion = formulario['fechaInscripcion']
        self.numero_inscripcion = formulario['nroInscripcion']
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
            return jsonify({"error": str(e)}), 500
        finally:
            connect.close()

    def add_formulario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                # Obtener los datos de la tabla 'formulario'
                formulario_sql = "SELECT * FROM formulario"
                cursor.execute(formulario_sql)
                formularios = cursor.fetchall()
                numero_de_atencion = len(formularios) + 1
                
                # Insert the data into the 'formulario' table
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
            connect.commit()
            return numero_de_atencion
        except Exception as e:
            connect.rollback()
            return jsonify({"error": str(e)}), 500
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
            return jsonify({"error": str(e)}), 500
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
            return jsonify({"error": str(e)}), 500
        finally:
            connect.close()

    def add_multipropietario(self):
        connect = self.connection()
        try:
            with connect.cursor() as cursor:
                #Obtain next id from 'Multipropietario' table
                multipropietario_sql = "SELECT id FROM Multipropietarios ORDER BY id DESC LIMIT 1"
                cursor.execute(multipropietario_sql)
                id = cursor.fetchall()
                if(id == ()):
                    id = 0
                else:
                    id = id[0]["id"]
                print("id: ", id)
                com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
                # Insert enajenantes data into the 'Multipropietarios' table
                for enajenante in self.enajenantes_data:
                    id += 1
                    enajenante_sql = """
                        INSERT INTO Multipropietarios (id,
                                                       com_man_pred,
                                                       RUNRUT,
                                                       porcDerecho, 
                                                       Fojas, 
                                                       Ano_inscripcion, 
                                                       Numero_inscripcion,
                                                       Fecha_de_inscripcion,
                                                       Ano_vigencia_inicial,
                                                       Ano_vigencia_final,
                                                       Tipo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(enajenante_sql, (
                        id,
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
                # Insert adquirente data into the 'Multipropietarios' table
                for adquirente in self.adquirentes_data:
                    id += 1
                    adquirente_sql = """
                        INSERT INTO Multipropietarios (id,
                                                       com_man_pred,
                                                       RUNRUT,
                                                       porcDerecho, 
                                                       Fojas, 
                                                       Ano_inscripcion, 
                                                       Numero_inscripcion,
                                                       Fecha_de_inscripcion,
                                                       Ano_vigencia_inicial,
                                                       Ano_vigencia_final,
                                                       Tipo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(adquirente_sql, (
                        id,
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
            connect.commit()

        except Exception as e:
            connect.rollback()
            print("error: ", e)
            return jsonify({"error": str(e)}), 500
        finally:
            connect.close()

    def scenario_1(self):
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
            return jsonify({"error": str(e)}), 500
        finally:
            connect.close()

    def scenario_2(self, last_initial_year):
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
            return jsonify({"error": str(e)}), 500
        finally:
            connect.close()

    def scenario_3(self, last_initial_year):
        pass
        # connect = self.connection()
        # try:
        #     with connect.cursor() as cursor:

        #         update_vigencia_final_query = "UPDATE Multipropietarios SET Ano_vigencia_final=" + str(int(self.fecha_inscripcion[0:4]) - 1) + " WHERE Ano_vigencia_inicial=" + str(last_initial_year) + " AND Ano_vigencia_final IS NULL"
        #         self.execute_Update_query(update_vigencia_final_query)

        #         numero_de_atencion = self.add_formulario()
        #         self.add_enajenante(numero_de_atencion)
        #         self.add_adquirente(numero_de_atencion)
        #         self.add_multipropietario() 
        #         return True
        # except Exception as e:
        #     connect.rollback()
        #     print("error: ", e)
        #     return jsonify({"error": str(e)}), 500
        # finally:
        #     connect.close()

    def scenario_4(self, last_initial_year):
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
            return jsonify({"error": str(e)}), 500
        finally:
            connect.close()


    def nivel_0(self):
        if(self.cne == 8):
            pass

        if(self.cne == 99):
            com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
            count_multipropietario = "SELECT COUNT(*) FROM Multipropietarios WHERE com_man_pred=" + '\'' + com_man_pred + '\''
            if(self.execute_Select_query(count_multipropietario)[0]['COUNT(*)'] == 0):
                print("Escenario 1")
                self.scenario_1()
            else:
                com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
                last_initial_year_query = "SELECT Ano_vigencia_inicial AS Ano FROM Multipropietarios WHERE com_man_pred=" + '\'' + com_man_pred + '\'' + " ORDER BY Ano_vigencia_inicial DESC LIMIT 1"
                last_initial_year = self.execute_Select_query(last_initial_year_query)[0]['Ano']
                if(last_initial_year < int(self.fecha_inscripcion[0:4])):
                    print("Escenario 2")
                    self.scenario_2(last_initial_year)
                if(last_initial_year > int(self.fecha_inscripcion[0:4])):
                    print("Es menor pero este escenario no esta listo")
                    self.scenario_3(last_initial_year)
                if(last_initial_year == int(self.fecha_inscripcion[0:4])):
                    print("Escenario 4")
                    self.scenario_4(last_initial_year)

    def nivel_1(self):
        sum_porcDerecho_adquirente = 0
        for i in self.adquirentes_data:
            sum_porcDerecho_adquirente += i['porcDerecho']
        print(sum_porcDerecho_adquirente)
        if(sum_porcDerecho_adquirente == 100):
            com_man_pred = str(self.comuna) + "-" + str(self.manzana) + "-" + str(self.predio)
            print(self.enajenantes_data)
            RunRut_enajenantes = []
            for i in self.enajenantes_data:
                RunRut_enajenantes.append(i['RUNRUT'])
            sum_porcDerecho_enajenante_query = "SELECT SUM(porcDerecho) as sum FROM Multipropietarios WHERE com_man_pred=" + '\'' + com_man_pred + '\'' + " AND RUNRUT IN " + str(RunRut_enajenantes).replace("[","(").replace("]",")")
            print(sum_porcDerecho_enajenante_query)
            sum_porcDerecho_enajenante = int(self.execute_Select_query(sum_porcDerecho_enajenante_query)[0]['sum'])
            print(sum_porcDerecho_enajenante)
            for i in self.adquirentes_data:
                i['porcDerecho'] *= sum_porcDerecho_enajenante/100
            print(self.adquirentes_data)
            #update enajenantes vigencias
            #add adjacentes


#Check to add the query as a function so as to not repeate the execute and fetchall arguments
#Maybe this can be added directly in add.py