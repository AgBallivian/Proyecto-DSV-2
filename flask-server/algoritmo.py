from DBmanager import (_obtener_siguiente_id_transferencias, _insert_enajenantes_to_transferencias,
                        _insert_adquirientes_to_transferencias, 
                        agregar_enajenante, agregar_adquirente, actualizar_multipropietarios_por_vigencia,
                        obtener_multipropietarios_commanpred, _obtener_siguiente_id_multipropietarios,
                        actualizar_transferia_por_vigencia, _insert_enajenantes_to_multipropietarios,
                        obtener_multipropietarios_vigentes, _insert_adquirientes_to_multipropietarios,
                        obtener_numero_de_atencion, obtener_transferencias_desde_ano,
                        _insert_adquirientes_to_transferencias, obtener_formularios_por_com_man_pred,
                        eliminar_multipropietarios_desde_ano, obtener_formulario_por_numero_inscripcion,
                        obtener_transferencias_igual_ano,
                        _obtener_ultimo_ano_inscripcion_exclusivo, eliminar_multipropietarios_igual_ano
                        )
from utils import (obtener_ano_inscripcion,_construir_com_man_pred, obtener_total_porcentaje)

COMPRAVENTA = 8
REGULARIZACION_DE_PATRIMONIO = 99

class form_solver():
    formularios_procesados = set()
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
        self.form_anterior = None
        self.formularios_por_procesar = []
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
            agregar_adquirente(obtener_numero_de_atencion(), adquirente["RUNRUT"], adquirente["porcDerecho"])
        for enajenantes in self.enajenantes_data:
            agregar_enajenante(obtener_numero_de_atencion(), enajenantes["RUNRUT"], enajenantes["porcDerecho"])
        
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
        for enajenante in self.enajenantes_data:
            _insert_enajenantes_to_transferencias(id_transferencias,
                com_man_pred, enajenante, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_transferencias += 1

        for adquirente in self.adquirentes_data:
            _insert_adquirientes_to_transferencias(id_transferencias,
                com_man_pred, adquirente, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)
            id_transferencias += 1
        

    def determinar_y_procesar_escenario(self):
        subir_formulario = True
        if self.cne == COMPRAVENTA:
            self.procesar_escenario_compraventa()
        elif self.cne == REGULARIZACION_DE_PATRIMONIO:
            subir_formulario = self._procesar_escenario_regularizacion_patrimonio()
        if subir_formulario:
            pass
            # self.agregar_transferencias()
            # self.agregar_multipropietarios()


    
    def procesar_escenario_compraventa(self):
        is_ghost=False
        com_man_pred = str(_construir_com_man_pred(self.comuna, self.manzana, self.predio))
        multipropietarios = obtener_multipropietarios_vigentes(com_man_pred)
        multipropietarios_runrut = [propietarios["RUNRUT"] for propietarios in multipropietarios]
        for enajenante in self.enajenantes_data:
            if (enajenante["RUNRUT"] not in multipropietarios_runrut):
                is_ghost = True
                enajenante['porcDerecho'] = 0
                enajenante['fecha_inscripcion'] = None
                enajenante['ano'] = None
                enajenante['numero_inscripcion'] = None


        lista_duenos_enajenantes = []
        for enajenante in self.enajenantes_data:
            for propietario in multipropietarios:
                if(enajenante['RUNRUT'] == propietario['RUNRUT']):
                    lista_duenos_enajenantes.append(propietario)
        lista_duenos_adquirientes = []
        for adquiriente in self.adquirentes_data:
            for propietario in multipropietarios:
                if(adquiriente['RUNRUT'] == propietario['RUNRUT']):
                    lista_duenos_adquirientes.append(propietario)
                
        for enajenante in self.enajenantes_data:
            if(float(enajenante['porcDerecho']) == 0):
                is_ghost = True
                break
        total_porc_enajenantes = obtener_total_porcentaje(lista_duenos_enajenantes)
        total_porc_adquirentes = obtener_total_porcentaje(self.adquirentes_data)

        # primer_caso = (total_porc_adquirentes == 100)
        # segundo_caso =(total_porc_adquirentes == 0)
        # tercer_caso = (len(self.enajenantes_data) == 1) and (len(self.adquirentes_data) == 1)
        self.aplicar_nivel_1(total_porc_adquirentes, total_porc_enajenantes, lista_duenos_enajenantes, multipropietarios, is_ghost)
        # self.primer_y_segundo_caso_cne8(primer_caso, segundo_caso, is_ghost, lista_duenos, total_porc_enajenantes)
        # if(tercer_caso):
        #     print("tercer caso enajenante fantasma")
        #     self.caso_3_cne8(is_ghost, lista_duenos)
        # else:
        #     print("Cuarto caso enajenante fantasma", is_ghost)
        #     #toda la gente con el mismo comapredio
        #     self.caso_4_cne8(is_ghost, lista_duenos, multipropietarios)

        # self.casos_fantasmas(is_ghost, lista_duenos, multipropietarios)
        self._acotar_registros_previos(com_man_pred)
        
    def aplicar_nivel_1(self, total_porc_adquirentes, total_porc_enajenantes, lista_duenos_enajenantes, multipropietarios, is_ghost):
        if(total_porc_adquirentes == 100):
            print("Procesando escenario 1: Suma adquirientes igual a 100")
            self.aplicar_primer_caso_cne_8(total_porc_enajenantes, multipropietarios)

        elif(total_porc_adquirentes == 0):
            print("Procesando escenario 2: Suma adquirientes igual a 0")
            self.aplicar_segundo_caso_cne_8(total_porc_enajenantes, multipropietarios)

        elif(len(self.enajenantes_data) == 1) and (len(self.adquirentes_data) == 1):
            print("Procesando escenario 3: 1 adquiriente y 1 enajenante")
            self.aplicar_tercer_caso_cne_8(is_ghost, lista_duenos_enajenantes, multipropietarios)
        else:
            self.aplicar_cuarto_caso_cne_8(is_ghost, lista_duenos_enajenantes, multipropietarios)

    # def primer_y_segundo_caso_cne8(self, primer_caso, segundo_caso, is_ghost, lista_duenos, total_porc_enajenantes):
    #     if primer_caso or segundo_caso:
    #         print("primer caso y segundo caso")
    #         total_porc_enajenantes = self._ajustar_porcentaje_total(is_ghost, lista_duenos, total_porc_enajenantes)
            
    #         if primer_caso:
    #             self._aplicar_primer_caso_cne8(total_porc_enajenantes, lista_duenos)
    #         elif segundo_caso:
    #             self._aplicar_segundo_caso_cne8(total_porc_enajenantes)

    # def _ajustar_porcentaje_total(self, is_ghost, lista_duenos, total_porc_enajenantes):
    #     if is_ghost:
    #         return 100
    #     else:
    #         for persona in lista_duenos:
    #             persona["porcDerecho"] += total_porc_enajenantes
    #         return total_porc_enajenantes

    def aplicar_primer_caso_cne_8(self, total_porc_enajenantes, multipropietarios):
        for adquirente in self.adquirentes_data:
            adquirente["porcDerecho"] = float(adquirente["porcDerecho"]) * (total_porc_enajenantes / 100)

        self.convertir_dueno_no_enajenante_a_adquiriente(multipropietarios)
        self.enajenantes_data = []
        self.agregar_multipropietarios()

    def aplicar_segundo_caso_cne_8(self, total_porc_enajenantes, multipropietarios):
        porcentaje_igual = total_porc_enajenantes / len(self.adquirentes_data)
        for adquirente in self.adquirentes_data:
            adquirente['porcDerecho'] = porcentaje_igual

        self.convertir_dueno_no_enajenante_a_adquiriente(multipropietarios)
        self.agregar_multipropietarios()

    def aplicar_tercer_caso_cne_8(self, is_ghost, lista_duenos_enajenantes, multipropietarios):
        adquirente = self.adquirentes_data[0]
        enajenante = self.enajenantes_data[0]
        if not is_ghost:
            porcentaje = float(lista_duenos_enajenantes[0]["porcDerecho"]) * float(adquirente["porcDerecho"]) / 100
            enajenante["porcDerecho"] = float(lista_duenos_enajenantes[0]["porcDerecho"]) - porcentaje
            adquirente["porcDerecho"] = porcentaje
            self.convertir_dueno_no_enajenante_a_adquiriente(multipropietarios)
            self.agregar_multipropietarios()

    def aplicar_cuarto_caso_cne_8(self, is_ghost, lista_duenos_enajenantes, multipropietarios):
        self.ajustar_porcentaje(is_ghost, lista_duenos_enajenantes)
        self.convertir_dueno_no_enajenante_a_adquiriente(multipropietarios)

        self.sacar_enajenantes_con_0_porcentaje()
        self.agregar_multipropietarios()


    def ajustar_porcentaje(self, is_ghost, lista_duenos_enajenantes):
        for indice, enajenante in enumerate(self.enajenantes_data):
            porcentaje_derecho_dueno = next((item["porcDerecho"] for item in lista_duenos_enajenantes if item["RUNRUT"] == enajenante["RUNRUT"]), enajenante["porcDerecho"])
            if not is_ghost:
                porcentaje_nuevo = porcentaje_derecho_dueno - enajenante["porcDerecho"]
            if is_ghost:
                if porcentaje_derecho_dueno < 0:
                    self.enajenantes_data[indice]["porcDerecho"] = str(porcentaje_derecho_dueno)
                else:
                    self.enajenantes_data[indice]["porcDerecho"] = 0
            else:
                self.enajenantes_data[indice]["porcDerecho"] = str(porcentaje_nuevo)

    def sacar_enajenantes_con_0_porcentaje(self):
        for enajenante in self.enajenantes_data:
            if(int(enajenante["porcDerecho"]) <= 0):
                self.enajenantes_data.remove(enajenante)
        
    def casos_fantasmas(self, is_ghost, lista_duenos, multipropietarios):
        if not is_ghost:
            return

        total_porc_multipropietarios = self._calcular_total_porcentaje(lista_duenos, multipropietarios)
        diferencia = 100 - total_porc_multipropietarios
        lista_personas_con_0_porc = self._identificar_personas_sin_porcentaje()

        if total_porc_multipropietarios > 100:
            self._ajustar_porcentajes_exceso(multipropietarios, total_porc_multipropietarios)
        elif total_porc_multipropietarios < 100:
            self._distribuir_diferencia(lista_personas_con_0_porc, diferencia)

    def _calcular_total_porcentaje(self, lista_duenos, multipropietarios):
        return (sum(float(adquirente["porcDerecho"]) for adquirente in self.adquirentes_data) +
                sum(float(persona["porcDerecho"]) for persona in multipropietarios if persona not in lista_duenos))

    def _identificar_personas_sin_porcentaje(self):
        lista_personas_con_0_porc = []
        self._identificar_adquirentes_sin_porcentaje(lista_personas_con_0_porc)
        self._identificar_enajenantes_sin_porcentaje(lista_personas_con_0_porc)
        return lista_personas_con_0_porc

    def _identificar_adquirentes_sin_porcentaje(self, lista_personas_con_0_porc):
        for adquirente in self.adquirentes_data:
            if float(adquirente["porcDerecho"]) <= 0:
                adquirente["porcDerecho"] = 0
                lista_personas_con_0_porc.append(adquirente)

    def _identificar_enajenantes_sin_porcentaje(self, lista_personas_con_0_porc):
        for enajenante in self.enajenantes_data:
            if float(enajenante["porcDerecho"]) <= 0:
                enajenante["porcDerecho"] = 0
                lista_personas_con_0_porc.append(enajenante)

    def _ajustar_porcentajes_exceso(self, multipropietarios, total_porc_multipropietarios):
        factor_ajuste = 100 / total_porc_multipropietarios
        for mp in multipropietarios:
            mp["porcDerecho"] = float(mp["porcDerecho"]) * factor_ajuste
        for adquirente in self.adquirentes_data:
            adquirente["porcDerecho"] = float(adquirente["porcDerecho"]) * factor_ajuste
        self.adquirentes_data.extend(multipropietarios)

    def _distribuir_diferencia(self, lista_personas_con_0_porc, diferencia):
        if lista_personas_con_0_porc:
            porcentaje_distribuido = diferencia / len(lista_personas_con_0_porc)
            for persona in lista_personas_con_0_porc:
                persona["porcDerecho"] = porcentaje_distribuido

    def _procesar_escenario_regularizacion_patrimonio(self):
        print("Procesando escenario de regularización de patrimonio")
        
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)
        multipropietario_existente = obtener_multipropietarios_commanpred(com_man_pred)
        if not multipropietario_existente:
            print("Procesando Escenario 1: No hay historia")
            self.agregar_multipropietarios()
        else:
            ultimo_ano_inicial_transferencias = _obtener_ultimo_ano_inscripcion_exclusivo(com_man_pred, self.numero_inscripcion)
            ano_inscripcion_actual = obtener_ano_inscripcion(self.fecha_inscripcion)
            if ano_inscripcion_actual > ultimo_ano_inicial_transferencias:
                self.procesar_escenario_2(com_man_pred)
            elif ano_inscripcion_actual < ultimo_ano_inicial_transferencias:
                self.procesar_escenario_3(com_man_pred, ano_inscripcion_actual)
            else:
                self.procesar_escenario_4(com_man_pred, ano_inscripcion_actual)
            return False

    def procesar_escenario_2(self, com_man_pred):
        print("Procesando Escenario 2: Llega un formulario posterior")    

        self.agregar_multipropietarios()
        self._acotar_registros_previos(com_man_pred)
        if(self.formularios_por_procesar):
            numero_inscripcion = self.formularios_por_procesar[0]
            formulario_proximo = obtener_formulario_por_numero_inscripcion(numero_inscripcion)
            self.recibir_proximo_formulario_y_guardar(formulario_proximo, self.formularios_por_procesar[1:])
            self.determinar_y_procesar_escenario()

    def procesar_escenario_3(self, com_man_pred, ano_inscripcion_actual):
        print("Procesando Escenario 3: Llega un formulario previo")
        
        transferencias_posteriores = obtener_transferencias_desde_ano(com_man_pred, ano_inscripcion_actual)
        eliminar_multipropietarios_desde_ano(ano_inscripcion_actual, com_man_pred)

        numero_inscripcion = transferencias_posteriores[0]
        formulario_proximo = obtener_formulario_por_numero_inscripcion(numero_inscripcion)
        self.agregar_multipropietarios()
        self._acotar_registros_previos(com_man_pred)

        self.recibir_proximo_formulario_y_guardar(formulario_proximo, transferencias_posteriores[1:])
        if(transferencias_posteriores):
            self.determinar_y_procesar_escenario()


    def procesar_escenario_4(self, com_man_pred, ano_inscripcion_actual):
        print("Procesando Escenario 4: Llega un formulario para el mismo año")
        transferencias_iguales = obtener_transferencias_igual_ano(com_man_pred, ano_inscripcion_actual)

        eliminar_multipropietarios_igual_ano(ano_inscripcion_actual, com_man_pred)

        numero_inscripcion = transferencias_iguales[0]["Numero_inscripcion"]
        formulario_ultimo = obtener_formulario_por_numero_inscripcion(numero_inscripcion)

        self.agregar_multipropietarios()

        self.recibir_proximo_formulario_y_guardar(formulario_ultimo, self.formularios_por_procesar[1:])
        if(self.formularios_por_procesar):
            self.determinar_y_procesar_escenario()


    def _acotar_registros_previos(self, com_man_pred):
        ano_vigencia_final = obtener_ano_inscripcion(self.fecha_inscripcion) - 1
        actualizar_multipropietarios_por_vigencia(com_man_pred, ano_vigencia_final, self.numero_inscripcion)

    def _guardar_formularios_existentes(self, com_man_pred, ano_inscripcion_actual):
        formularios = obtener_formularios_por_com_man_pred(com_man_pred)
        return [f for f in formularios if obtener_ano_inscripcion(f['fechaInscripcion']) >= ano_inscripcion_actual]

    def _insertar_adquirente_en_transferencias(self, com_man_pred, adquirente):
        _insert_adquirientes_to_transferencias(
            id_transferencia=_obtener_siguiente_id_transferencias(),
            com_man_pred=com_man_pred,
            adquirente=adquirente,
            fojas=self.fojas,
            fecha_inscripcion=self.fecha_inscripcion,
            numero_inscripcion=self.numero_inscripcion,
        )
    def ajustar_porcentajes_adquirentes(self):
        sum_porc_derecho_adquirente = self._calcular_suma_porc_derecho_adquirente()

        if sum_porc_derecho_adquirente == 100:
            run_rut_enajenantes = self._obtener_run_rut_enajenantes()
            if run_rut_enajenantes:
                sum_porc_derecho_enajenante = self._calcular_suma_porc_derecho_enajenante()
                self._ajustar_porc_derecho_adquirentes(sum_porc_derecho_enajenante)

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

    def recibir_proximo_formulario_y_guardar(self, formulario_proximo, formularios_por_procesar):
        self.formulario = formulario_proximo
        self.cne = int(formulario_proximo['CNE'])
        self.comuna = int(formulario_proximo['bienRaiz']['comuna'])
        self.manzana = int(formulario_proximo['bienRaiz']['manzana'])
        self.predio = int(formulario_proximo['bienRaiz']['predio'])
        self.fojas = int(formulario_proximo['fojas'])
        self.fecha_inscripcion = formulario_proximo['fechaInscripcion']
        self.numero_inscripcion = int(formulario_proximo['nroInscripcion'])
        self.form_anterior = None
        self.formularios_por_procesar = formularios_por_procesar
        try:
            self.enajenantes_data = formulario_proximo['enajenantes']#cambiar por una funcion que llame todos los enajenantes para ese num_inscripcion
        except Exception as e:
            self.enajenantes_data = []
            
        if formulario_proximo['adquirentes'] != []:
            self.adquirentes_data = formulario_proximo['adquirentes']#cambiar por una funcion que llame todos los adquirientes para ese num_inscripcion
        else:
            self.adquirentes_data = []

    def convertir_dueno_no_enajenante_a_adquiriente(self, multipropietarios):
        for propietario in multipropietarios:
            if(propietario["RUNRUT"] not in [enajenante['RUNRUT'] for enajenante in self.enajenantes_data]):
                propietario_adquiriente = {
                    "RUNRUT": propietario["RUNRUT"], 
                    "porcDerecho": propietario["porcDerecho"],
                    "Numero_inscripcion": propietario["Numero_inscripcion"]}
                self.adquirentes_data.append(propietario_adquiriente)