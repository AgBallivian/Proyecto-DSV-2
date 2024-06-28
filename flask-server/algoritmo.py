from DBmanager import (_obtener_siguiente_id_transferencias, _insert_enajenantes_to_transferencias,
                        _insert_adquirientes_to_transferencias, obtener_transferencias_por_com_man_pred, 
                        agregar_formulario, agregar_enajenante, agregar_adquirente, _actualizar_multipropietarios_por_vigencia,
                        _obtener_ano_final, _obtener_ultimo_ano_inicial,delete_transferencias_antiguos,
                        obtener_multipropietarios_commanpred, _obtener_siguiente_id_multipropietarios,
                        actualizar_transferia_por_vigencia, _insert_enajenantes_to_multipropietarios,
                        obtener_multipropietario_commanpred, _insert_adquirientes_to_multipropietarios,
                        obtener_numer_de_atencion, obtener_transferencias_commanpred, 
                        _insert_adquirientes_to_transferencias, obtener_formularios_por_com_man_pred)
from utils import (obtener_ano_inscripcion,_construir_com_man_pred, obtener_total_porcentaje)
from Errores import ERROR_MESSAGE
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
            agregar_adquirente(obtener_numer_de_atencion(), adquirente["RUNRUT"], adquirente["porcDerecho"])
        for enajenantes in self.enajenantes_data:
            agregar_enajenante(obtener_numer_de_atencion(), enajenantes["RUNRUT"], enajenantes["porcDerecho"])

    def ultimo_formulario(self):
        self.form_anterior = (  
            self.comuna, self.manzana, self.predio, self.fojas, self.cne, self.enajenantes_data, self.adquirentes_data
        )
        

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

    # def eliminar_antiguos_y_reemplazar(self, last_initial_year):
    #     delete_transferencias_antiguos(last_initial_year)
    #     agregar_formulario(self.cne, self.comuna, self.manzana, self.predio, self.fojas, self.fecha_inscripcion, self.numero_inscripcion)

    def add_all(self, numero_de_atencion):
        for enajenante in self.enajenantes_data:
            agregar_enajenante(numero_de_atencion, enajenante['RUNRUT'], enajenante['porcDerecho'])
        for adquirente in self.adquirentes_data:
            agregar_adquirente(numero_de_atencion, adquirente['RUNRUT'], adquirente['porcDerecho'])
        self.agregar_transferencias()
        # self.handle_enajenante_fantasma()
        

    def determinar_y_procesar_escenario(self):
        formulario_id = (self.cne, self.comuna, self.manzana, self.predio, self.fecha_inscripcion)
        
        if formulario_id in self.formularios_procesados:
            print(f"Formulario ya procesado: {formulario_id}")
            return

        self.formularios_procesados.add(formulario_id)
        
        subir_formulario = True
        if self.cne == COMPRAVENTA:
            subir_formulario = self.procesar_escenario_compraventa()
        elif self.cne == REGULARIZACION_DE_PATRIMONIO:
            self._procesar_escenario_regularizacion_patrimonio()
        if subir_formulario:
            self.agregar_transferencias()


    
    def procesar_escenario_compraventa(self):
        is_ghost=False
        for enajenante in self.enajenantes_data:
            multipropietarios = obtener_transferencias_commanpred(
                _construir_com_man_pred(self.comuna, self.manzana, self.predio),
                enajenante['RUNRUT']
            )
            print("existo?",multipropietarios)
            if multipropietarios == None or multipropietarios == ():
                print("encontre un ghost")
                is_ghost = True
                enajenante['porcDerecho'] = 0
                enajenante['fecha_inscripcion'] = None
                enajenante['ano'] = None
                enajenante['numero_inscripcion'] = None

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
                #enajenante['porcDerecho'] = 100
                break
        total_porc_enajenantes = obtener_total_porcentaje(lista_duenos)
        if is_ghost:
            for adquirente in self.form_anterior["adquirentes"]:
                for enajenante in self.enajenantes_data:
                    if(adquirente["RUNRUT"] != enajenante["RUNRUT"]):
                        self.adquirentes_data.append(adquirente)
            total_porc_adquirentes = obtener_total_porcentaje(self.adquirentes_data)
        else:
            total_porc_adquirentes = obtener_total_porcentaje(self.adquirentes_data)

        primer_caso = True if total_porc_adquirentes == 100 else False
        segundo_caso = True if total_porc_adquirentes == 0 else False
        tercer_caso = (len(self.enajenantes_data) == 1) and (len(self.adquirentes_data) == 1)

        if(primer_caso or segundo_caso):
            if(is_ghost):
                total_porc_enajenantes = 100
            else:
                for personas in lista_duenos:
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
            print("SOY EL CUARTO CASO")
            actualizar_transferia_por_vigencia(com_man_pred,  str(int(self.fecha_inscripcion[:4]) - 1))
            #toda la gente con el mismo comapredio
            for personas in datos_temporales_totales:
                if personas not in self.enajenantes_data and personas not in self.adquirentes_data:
                    self.enajenantes_data.append(personas)
            
            for dueno in lista_duenos:
                for index, enajenante in enumerate(self.enajenantes_data[:]):
                    if dueno["RUNRUT"] == enajenante["RUNRUT"]:
                        if is_ghost:
                            dueno["porcDerecho"] -= float(enajenante["porcDerecho"])
                            print("deja de cumearlo",enajenante["porcDerecho"])
                            if float(dueno["porcDerecho"]) < 0:
                                self.enajenantes_data[index]["porcDerecho"] = str(dueno["porcDerecho"])
                            else:
                                self.enajenantes_data[index]["porcDerecho"] = 0
                            break

                        else:
                            dueno["porcDerecho"] -= float(enajenante["porcDerecho"])
                            if dueno["porcDerecho"] <= 0:
                                self.enajenantes_data.remove(enajenante)
                            self.enajenantes_data[index]["porcDerecho"] = str(dueno["porcDerecho"])
                            break

        print(self.enajenantes_data)
        if(is_ghost):
            print("es ghost")
            #para el caso dos debo tener en cuenta la totalidad del
            #formulario y multiplicar el porcentaje que se suma 
            # con todos los adquirientes totales tanto del 99(dueños antiguos)
            #como los recien ingresados y dividirlo 
            

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
            elif(total_porc_adquirentes<100):
                for multipropietario in lista_personas:
                    multipropietario["porcDerecho"] = (diferencia/(len(lista_personas)))

    def _procesar_escenario_regularizacion_patrimonio(self):
        print("Procesando escenario de regularización de patrimonio")
        
        com_man_pred = _construir_com_man_pred(self.comuna, self.manzana, self.predio)
        transferencias_existentes = obtener_transferencias_por_com_man_pred(com_man_pred)

        if not transferencias_existentes:
            return True
        else:
            ultimo_ano_inicial_transferencias = _obtener_ultimo_ano_inicial(self.comuna, self.manzana, self.predio)
            ano_inscripcion_actual = obtener_ano_inscripcion(self.fecha_inscripcion)
            if ano_inscripcion_actual > ultimo_ano_inicial_transferencias:
                self.procesar_escenario_2(com_man_pred)
            elif ano_inscripcion_actual < ultimo_ano_inicial_transferencias:
                self.procesar_escenario_3(com_man_pred, ano_inscripcion_actual, ultimo_ano_inicial_transferencias)
            else:
                self.procesar_escenario_4(com_man_pred, ano_inscripcion_actual)
            return False

    def procesar_escenario_2(self, com_man_pred):
        print("Procesando Escenario 2: Llega un formulario posterior")    
        self._acotar_registros_previos(com_man_pred)

    def procesar_escenario_3(self, com_man_pred, ano_inscripcion_actual, ultimo_ano_inicial_transferencias):
        print("Procesando Escenario 3: Llega un formulario previo")
        
        # 1. Guardar los formularios existentes que serán eliminados
        formularios_existentes = obtener_formularios_por_com_man_pred(com_man_pred)
        formularios_a_reprocesar = [f for f in formularios_existentes if obtener_ano_inscripcion(str(f['fechaInscripcion'])) >= ano_inscripcion_actual]
        
        # 2. Eliminar registros posteriores al nuevo
        self._eliminar_registros_posteriores(com_man_pred, ano_inscripcion_actual)
        
        # 3. Insertar el nuevo registro
        formulario_actual = (self.cne, self.comuna, self.manzana, self.predio, self.fecha_inscripcion)
        if formulario_actual not in self.formularios_procesados:
            self._insertar_nuevo_registro(com_man_pred)
            self.formularios_procesados.add(formulario_actual)
    
        
        # 4. Reprocesar formularios en orden cronológico
        self._reprocesar_formularios(formularios_a_reprocesar)

    def procesar_escenario_4(self, com_man_pred, transferencias_existentes):
        print("Procesando Escenario 4: Llega un formulario para el mismo año")
        
        # ano_inscripcion_actual = obtener_ano_inscripcion()
        # self._eliminar_registros_mismo_ano(com_man_pred, ano_inscripcion_actual)
        # self._insertar_nuevo_registro(com_man_pred)
        # self._ajustar_transferencias_existentes(com_man_pred, ano_inscripcion_actual, transferencias_existentes, es_escenario_4=True)


    def _acotar_registros_previos(self, com_man_pred):
        ano_vigencia_final = obtener_ano_inscripcion(self.fecha_inscripcion) - 1
        actualizar_transferia_por_vigencia(com_man_pred, ano_vigencia_final)

    def _ajustar_transferencias_existentes(self, com_man_pred, ano_inscripcion_actual, transferencias_existentes, es_escenario_4=False):
        for transferencia in transferencias_existentes:
            ano_inscripcion_transferencia = obtener_ano_inscripcion(transferencia['fechaInscripcion'])
            
            if ano_inscripcion_transferencia == ano_inscripcion_actual:
                if not es_escenario_4:
                    # Para el escenario 3, actualizamos la vigencia inicial
                    actualizar_transferia_por_vigencia(
                        com_man_pred, 
                        ano_vigencia_inicial=ano_inscripcion_actual + 1,
                        ano_vigencia_final=transferencia['Ano_vigencia_final'],
                        id_transferencia=transferencia['id']
                    )
                # Para el escenario 4, no hacemos nada aquí porque ya hemos eliminado los registros del mismo año
            elif ano_inscripcion_transferencia < ano_inscripcion_actual:
                # Si la transferencia es anterior, actualizamos su vigencia final si es necesario
                if transferencia['Ano_vigencia_final'] is None or transferencia['Ano_vigencia_final'] >= ano_inscripcion_actual:
                    actualizar_transferia_por_vigencia(
                        com_man_pred,
                        ano_vigencia_inicial=transferencia['Ano_vigencia_inicial'],
                        ano_vigencia_final=ano_inscripcion_actual - 1,
                        id_transferencia=transferencia['id']
                    )
            elif ano_inscripcion_transferencia > ano_inscripcion_actual:
                # Si la transferencia es posterior, no necesitamos hacer nada
                pass

    def _guardar_formularios_existentes(self, com_man_pred, ano_inscripcion_actual):
        formularios = obtener_formularios_por_com_man_pred(com_man_pred)
        return [f for f in formularios if obtener_ano_inscripcion(f['fechaInscripcion']) >= ano_inscripcion_actual]

    def _eliminar_registros_posteriores(self, com_man_pred, ano_inscripcion_actual):
        delete_transferencias_antiguos(ano_inscripcion_actual, com_man_pred)

    def _insertar_nuevo_registro(self, com_man_pred):
        for adquirente in self.adquirentes_data:
            self._insertar_adquirente_en_transferencias(com_man_pred, adquirente)

    def _reprocesar_formularios(self, formularios):
        formularios_ordenados = sorted(formularios, key=lambda x: x['fechaInscripcion'])
        for formulario in formularios_ordenados:
            formulario_id = (formulario['CNE'], formulario['bienRaiz']['comuna'], 
                            formulario['bienRaiz']['manzana'], formulario['bienRaiz']['predio'], 
                            formulario['fechaInscripcion'])
            
            if formulario_id not in self.formularios_procesados:
                print("Reprocesando formulario:")
                print(f"  CNE: {formulario['CNE']}")
                print(f"  Bien Raíz: {formulario['bienRaiz']}")
                print(f"  Fecha Inscripción: {formulario['fechaInscripcion']}")
                print(f"  Enajenantes: {formulario['enajenantes']}")
                print(f"  Adquirentes: {formulario['adquirentes']}")
                
                self.formularios_procesados.add(formulario_id)
                form_solver(formulario, self.connection).determinar_y_procesar_escenario()
            else:
                print(f"Formulario ya procesado: {formulario_id}")


    def _eliminar_registros_mismo_ano(self, com_man_pred, ano):
        delete_transferencias_antiguos(ano, com_man_pred)
    
    def _insertar_nuevo_registro(self, com_man_pred):
        for adquirente in self.adquirentes_data:
            self._insertar_adquirente_en_transferencias(com_man_pred, adquirente)

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
