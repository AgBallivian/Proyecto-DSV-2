from DBmanager import (_obtener_siguiente_id_transferencias, _insert_enajenantes_to_transferencias,
                        _insert_adquirientes_to_transferencias, obtener_transferencias, 
                        agregar_formulario, agregar_enajenante, agregar_adquirente, _actualizar_multipropietarios_por_vigencia,
                        _obtener_ano_final, _obtener_ultimo_ano_inicial,delete_transferencias_antiguos,
                        obtener_multipropietarios_commanpred,
                        actualizar_transferia_por_vigencia,
                        obtener_multipropietario_transferencias_commanpred)
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

    def agregar_transferencias(self):
        id_transferencia = _obtener_siguiente_id_transferencias()
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)
        for enajenante in self.enajenantes_data:
            _insert_enajenantes_to_transferencias(id_transferencia,
                com_man_pred, enajenante, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_transferencia += 1

        for adquirente in self.adquirentes_data:
            _insert_adquirientes_to_transferencias(id_transferencia,
                com_man_pred, adquirente, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_transferencia += 1

    def actualizar_vigencia(self, last_initial_year):
        _actualizar_multipropietarios_por_vigencia(last_initial_year, self.comuna, self.manzana, self.predio, self.fecha_inscripcion)

        numero_de_atencion = agregar_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
        self.add_all(numero_de_atencion)
        return True

    def eliminar_antiguos_y_reemplazar(self, last_initial_year):
        delete_transferencias_antiguos(last_initial_year)
        agregar_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)

    def add_all(self, numero_de_atencion):
        for enajenante in self.enajenantes_data:
            agregar_enajenante(numero_de_atencion, enajenante['RUNRUT'], enajenante['porcDerecho'])
        for adquirente in self.adquirentes_data:
            agregar_adquirente(numero_de_atencion, adquirente['RUNRUT'], adquirente['porcDerecho'])
        self.agregar_transferencias()
        # self.handle_enajenante_fantasma()
        

    def determinar_y_procesar_escenario(self):
        if self.cne == COMPRAVENTA:
            self.procesar_escenario_compraventa()
        elif self.cne == REGULARIZACION_DE_PATRIMONIO:
            self._procesar_escenario_regularizacion_patrimonio()
        self.agregar_ransferencias()


    
    def procesar_escenario_compraventa(self):
        is_ghost=False
        for enajenante in self.enajenantes_data:
            multipropietarios = obtener_multipropietarios_commanpred(
                _construir_com_man_pred(self.comuna, self.manzana, self.predio),
                enajenante['RUNRUT'],
                self.fecha_inscripcion
            )
            if multipropietarios == None:
                is_ghost = True
                enajenante['porcDerecho'] = 0
                enajenante['fecha_inscripcion'] = None
                enajenante['ano'] = None
                enajenante['numero_inscripcion'] = None

        com_man_pred = str(_construir_com_man_pred(self.comuna, self.manzana, self.predio))
        datos_temporales_totales = obtener_multipropietario_transferencias_commanpred(
            com_man_pred
        )
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
                    actualizar_transferia_por_vigencia(com_man_pred,  str(int(self.fecha_inscripcion[:4]) - 1))
                    for adquirente in self.adquirentes_data:
                        adquirente["porcDerecho"] = float(adquirente["porcDerecho"]) * (total_porc_enajenantes / 100)
                    self.enajenantes_data = [enajenante for enajenante in self.enajenantes_data if enajenante not in lista_duenos]
                    
                        
                elif segundo_caso:
                    #los adquirientes tienen 0%, por ende, se multiplica el porcentaje de enajenantes de la bbdd por el porcentaje total(100%) dividido pro en numero de adquirentes
                    for adquirente in self.adquirentes_data:
                        adquirente['porcDerecho'] = porcentaje_igual * (total_porc_enajenantes / 100)

            elif(tercer_caso):
                adquirente = self.adquirentes_data[0]
                enajenante = self.enajenantes_data[0]
                if not is_ghost:
                    porcentaje = float(enajenante["porcDerecho"]) * float(adquirente["porcDerecho"]) / 100
                else:
                    porcentaje = 100 * float(adquirente["porcDerecho"]) / 100

                if not is_ghost:
                    enajenante["porcDerecho"] = float(enajenante["porcDerecho"]) - porcentaje
                adquirente["porcDerecho"] = porcentaje

            else:
                for duenos in lista_duenos:
                    for vendiendo in self.enajenantes_data:
                        if duenos["RUNRUT"] == vendiendo["RUNRUT"]:
                            duenos["porDerecho"] -= vendiendo["porDerecho"]
                            if duenos["porDerecho"] <= 0:
                                pass
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

        count_transferencia = obtener_transferencias(self.comuna, self.manzana, self.predio)

        if not count_transferencia:
            self.procesar_escenario_1()
        else:
            last_initial_year = _obtener_ultimo_ano_inicial(self.comuna, self.manzana, self.predio)
            if last_initial_year < self.fecha_inscripcion[:4]:
                self.procesar_escenario_2(last_initial_year)
            elif last_initial_year > obtener_ano_inscripcion():
                pass
            else:
                self.procesar_escenario_4(last_initial_year)

    def procesar_escenario_1(self):
        print("Escenario 1")
        #self.agregar_nuevo_formulario()

    def procesar_escenario_2(self, last_initial_year):
        print("Escenario 2")
        self.actualizar_vigencia(last_initial_year)

    def procesar_escenario_4(self, last_initial_year):
        print("Escenario 4")
        self.eliminar_antiguos_y_reemplazar(last_initial_year)

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
