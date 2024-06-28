from DBmanager import (_obtener_siguiente_id_transferencias, _insert_enajenantes_to_transferencias,
                        _insert_adquirientes_to_transferencias, obtener_transferencias_por_com_man_pred, 
                        agregar_formulario, agregar_enajenante, agregar_adquirente, _actualizar_multipropietarios_por_vigencia,
                        _obtener_ano_final, _obtener_ultimo_ano_inicial,delete_transferencias_antiguos,
                        obtener_multipropietarios_commanpred, _obtener_siguiente_id_multipropietarios,
                        actualizar_transferia_por_vigencia, _insert_enajenantes_to_multipropietarios,
                        obtener_multipropietario_commanpred, _insert_adquirientes_to_multipropietarios,
                        obtener_numer_de_atencion)
from utils import (obtener_ano_inscripcion,_construir_com_man_pred, obtener_total_porcentaje)
from Errores import ERROR_MESSAGE
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
        try:
            self.enajenantes_data = formulario['enajenantes']
        except Exception as e:
            self.enajenantes_data = []
            
        if formulario['adquirentes'] != []:
            self.adquirentes_data = formulario['adquirentes']
        else:
            self.adquirentes_data = []

        self.agregar_transferencias()
        for adquirente in self.adquirentes_data:
            print(adquirente)
            agregar_adquirente(obtener_numer_de_atencion(), adquirente["RUNRUT"], adquirente["porcDerecho"])
        for enajenantes in self.enajenantes_data:
            print(enajenantes)
            agregar_enajenante(obtener_numer_de_atencion(), enajenantes["RUNRUT"], enajenantes["porcDerecho"])

    def agregar_multipropietarios(self):
        id_multipropietario = _obtener_siguiente_id_multipropietarios()
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)
        for enajenante in self.enajenantes_data:
            _insert_enajenantes_to_multipropietarios(id_multipropietario,
                com_man_pred, enajenante, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_multipropietario += 1

        for adquirente in self.adquirentes_data:
            _insert_adquirientes_to_multipropietarios(id_multipropietario,
                com_man_pred, adquirente, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_multipropietario += 1

    def agregar_transferencias(self):
        id_transferencias = _obtener_siguiente_id_transferencias()
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)
        #print(self.enajenantes_data)
        for enajenante in self.enajenantes_data:
            _insert_enajenantes_to_transferencias(id_transferencias,
                com_man_pred, enajenante, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_transferencias += 1

        for adquirente in self.adquirentes_data:
            _insert_adquirientes_to_transferencias(id_transferencias,
                com_man_pred, adquirente, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_transferencias += 1

    def eliminar_antiguos_y_reemplazar(self, last_initial_year):
        delete_transferencias_antiguos(last_initial_year)
        agregar_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)


    def determinar_y_procesar_escenario(self):
        if self.cne == COMPRAVENTA:
            self.procesar_escenario_compraventa()
        elif self.cne == REGULARIZACION_DE_PATRIMONIO:
            self._procesar_escenario_regularizacion_patrimonio()
        self.agregar_multipropietarios()

    
    def procesar_escenario_compraventa(self):
        com_man_pred = str(_construir_com_man_pred(self.comuna, self.manzana, self.predio))
        datos_temporales_totales = obtener_multipropietario_commanpred(
            com_man_pred
        )
        print("datos temporales:", datos_temporales_totales)
        lista_duenos = []
        for personas in datos_temporales_totales:
            for enajenante in self.enajenantes_data:
                if(enajenante['RUNRUT'] == personas['RUNRUT']):
                    lista_duenos.append(personas)
        


        for enajenante in self.enajenantes_data:
            if(enajenante['porcDerecho'] == 0):
                is_ghost = True
                enajenante['porcDerecho'] = 100
                break
        total_porc_enajenantes = obtener_total_porcentaje(lista_duenos)
        total_porc_adquirentes = obtener_total_porcentaje(self.adquirentes_data)
        primer_caso = True if total_porc_adquirentes == 100 else False
        segundo_caso = True if total_porc_adquirentes == 0 else False
        tercer_caso = (len(self.enajenantes_data) == 1) and (len(self.adquirentes_data) == 1)

        if(primer_caso or segundo_caso):
            if(is_ghost):
                total_porc_enajenantes = 100
            else:
                for personas in lista_duenos:
                        print("SOY PTO",personas)
                        personas["porcDerecho"] += total_porc_enajenantes 
            porcentaje_igual = total_porc_enajenantes / len(self.adquirentes_data)

            if primer_caso:
                print(str(int(self.fecha_inscripcion[:4]) - 1))
                actualizar_transferia_por_vigencia(com_man_pred,  str(int(self.fecha_inscripcion[:4]) - 1))
                for adquirente in self.adquirentes_data:
                    adquirente["porcDerecho"] = float(adquirente
                    ["porcDerecho"]) * (total_porc_enajenantes / 100)
                
                for enajenante in self.enajenantes_data:
                    for personas in lista_duenos:
                        if(enajenante['RUNRUT'] == personas['RUNRUT']):
                            self.enajenantes_data.remove(enajenante)
                
                
                    
            elif segundo_caso:
                #los adquirientes tienen 0%, por ende, se multiplica el porcentaje de enajenantes de la bbdd por el porcentaje total(100%) dividido pro en numero de adquirentes
                for adquirente in self.adquirentes_data:
                    adquirente['porcDerecho'] = porcentaje_igual * (total_porc_enajenantes / 100)

        elif(tercer_caso):
            actualizar_transferia_por_vigencia(com_man_pred,  str(int(self.fecha_inscripcion[:4]) - 1))
            adquirente = self.adquirentes_data[0]
            enajenante = self.enajenantes_data[0]
            if not is_ghost:
                porcentaje = float(lista_duenos[0]["porcDerecho"]) * float(adquirente["porcDerecho"]) / 100
            else:
                porcentaje = 100 * float(adquirente["porcDerecho"]) / 100

            if not is_ghost:
                enajenante["porcDerecho"] = float(lista_duenos[0]["porcDerecho"]) - porcentaje
            adquirente["porcDerecho"] = porcentaje

        else:
            actualizar_transferia_por_vigencia(com_man_pred,  str(int(self.fecha_inscripcion[:4]) - 1))
            #toda la gente con el mismo comapredio
            for personas in datos_temporales_totales:
                if personas not in self.enajenantes_data and personas not in self.adquirentes_data:
                    self.enajenantes_data.append(personas)
            
            for dueno in lista_duenos:
                for index, enajenante in enumerate(self.enajenantes_data[:]):
                    if dueno["RUNRUT"] == enajenante["RUNRUT"]:
                        dueno["porcDerecho"] -= float(enajenante["porcDerecho"])
                        if dueno["porcDerecho"] <= 0:
                            self.enajenantes_data.remove(enajenante)
                            break
                        else:
                            # Update the value in the original list
                            self.enajenantes_data[index]["porcDerecho"] = str(dueno["porcDerecho"])
                        print(f"Updated: index {index}, new porcDerecho: {self.enajenantes_data[index]['porcDerecho']}")

        print(self.enajenantes_data)
        if(is_ghost):
            diferencia = 100 - total_porc_adquirentes
            lista_personas = []
            for adquirente in self.adquirentes_data:
                porcentaje = float(adquirente["porcDerecho"])
                if float(porcentaje) <= 0:
                    adquirente["porcDerecho"] = 0
                    lista_personas.append(adquirente)
            for enajenante in self.enajenantes_data:
                porcentaje = float(enajenante["porcDerecho"])
                if float(porcentaje) <= 0:
                    enajenante["porcDerecho"] = 0
                    lista_personas.append(enajenante)
            if (total_porc_adquirentes>100):
                for adquirente in self.adquirentes_data:
                    adquirente["porcDerecho"] = (float(adquirente["porcDerecho"])/total_porc_adquirentes)*100
            if(total_porc_adquirentes<100):
                for multipropietario in lista_personas:
                    multipropietario["porcDerecho"] = (diferencia/(len(lista_personas)))

    def _procesar_escenario_regularizacion_patrimonio(self):
        print("Procesando escenario de regularización de patrimonio")
        
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)
        transferencias_existentes = obtener_transferencias_por_com_man_pred(com_man_pred)

        if not transferencias_existentes:
            return True
        
        #PROBAR CON UNA WEA QUE YA ESXISTE IGAL PARA LOS OTROS CASOS
        else:
            print("Transferencias existentes: ALOALAOALAOLAOALAOALOA")
            ultimo_ano_inicial_transferencias = _obtener_ultimo_ano_inicial(self.comuna, self.manzana, self.predio)
            ano_inscripcion_actual = obtener_ano_inscripcion(self.fecha_inscripcion)
            if ano_inscripcion_actual > ultimo_ano_inicial_transferencias:
                self.procesar_escenario_2(com_man_pred)

            elif ano_inscripcion_actual < ultimo_ano_inicial_transferencias:
                self.procesar_escenario_3(com_man_pred, ultimo_ano_inicial_transferencias)
            else:
                # Aquí se implementará el escenario 4 en el futuro
                pass

    def procesar_escenario_2(self, com_man_pred):
        print("Procesando Escenario 2: Llega un formulario posterior")    
        self._acotar_registros_previos(com_man_pred)


    def procesar_escenario_3(self, com_man_pred, ultimo_ano_inicial):
        print("Procesando Escenario 3: Llega un formulario previo")
        #TODO: Implementar escenario 3

    def procesar_escenario_4(self, last_initial_year):
        print("Escenario 4")
        #TODO: Implementar escenario 4

    def _insertar_adquirente_en_transferencias(self, com_man_pred, adquirente): 
        _insert_adquirientes_to_transferencias(
            id_transferencia=_obtener_siguiente_id_transferencias(),
            com_man_pred=com_man_pred,
            adquirente=adquirente,
            fojas=self.fojas,
            fecha_inscripcion=self.fecha_inscripcion,
            numero_inscripcion=self.numero_inscripcion
        )

    def _acotar_registros_previos(self, com_man_pred):
        ano_vigencia_final = obtener_ano_inscripcion(self.fecha_inscripcion) - 1
        actualizar_transferia_por_vigencia(com_man_pred, ano_vigencia_final)

    def _acotar_formulario_entrante(self, com_man_pred, transferencias_existentes):
        #Obtener el año de inscripción de transferencias mas antiguo
        pass
        

    def ajustar_porcentajes_adquirentes(self):
        sum_porc_derecho_adquirente = self._calcular_suma_porc_derecho_adquirente()
        # print("Suma de porcentajes de derecho de adquirentes: " + str(sum_porc_derecho_adquirente))

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
