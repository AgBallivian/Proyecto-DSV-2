INTERNAL_SERVER_ERROR = 500
COMPRAVENTA = 8
REGULARIZACION_DE_PATRIMONIO = 99
QUERY_ALL_ENAJENANTES = "SELECT * FROM Enajenantes"
QUERY_ALL_FORMULARIOS = "SELECT * FROM formulario"
QUERY_ALL_ADQUIRENTES = "SELECT * FROM Adquirentes"
QUERY_INSERTAR_FORM = """
                    INSERT INTO formulario (
                        Numero_de_atencion, CNE, Comuna, Manzana, Predio, Fojas, Fecha_de_inscripcion, Numero_de_insripcion
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
QUERY_INSERTAR_ENAJENANTES = """
                        INSERT INTO Enajenantes (id, enajenante_id, RUNRUT, porcDerecho)
                        VALUES ( %s, %s, %s, %s)
                    """
QUERY_INSERTAR_ADQUIRENTES = """
                        INSERT INTO Adquirentes (id, Adquirente_id, RUNRUT, porcDerecho)
                        VALUES (%s, %s, %s, %s)
                    """
QUERY_ID_TRANSFERENCIAS = "SELECT id FROM Transferencias ORDER BY id DESC LIMIT 1"
QUERY_UPDATE_TRANSFERENCIAS_SQL = """
                    UPDATE Transferencias
                    SET Ano_vigencia_final={ano_final}
                    WHERE Ano_vigencia_inicial={ano_inicial}
                    AND Ano_vigencia_final IS NULL
                    AND com_man_pred='{com_man_pred}'
                    """
QUERY_DELETE_TRANSFERENCIAS = """
DELETE FROM Transferencias 
WHERE Ano_vigencia_inicial = {last_initial_year}
AND com_man_pred = {com_man_pred}"""

QUERY_OBTENER_TRANSFERENCIAS_SQL = """
SELECT *
FROM Transferencias
WHERE com_man_pred={com_man_pred}
"""

QUERY_OBTENER_ULT_ANO_INIT = "SELECT Ano_vigencia_inicial AS Ano FROM Transferencias WHERE com_man_pred = {com_man_pred} ORDER BY Ano_vigencia_inicial DESC LIMIT 1"

QUERY_INSERTAR_ENAJENANTES_TRANSFERENCIAS_SQL = """
        INSERT INTO Transferencias (id, com_man_pred, RUNRUT, porcDerecho, Fojas, Ano_inscripcion, Numero_inscripcion, Fecha_de_inscripcion, Ano_vigencia_inicial, Ano_vigencia_final, Tipo)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

QUERY_INSERTAR_ADQUIRENTES_TRANSFERENCIAS_SQL = """
        INSERT INTO Transferencias (id, com_man_pred, RUNRUT, porcDerecho,
                                    Fojas, Ano_inscripcion, Numero_inscripcion,
                                    Fecha_de_inscripcion, Ano_vigencia_inicial,
                                    Ano_vigencia_final, Tipo)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

QUERY_CONNECTOR = """ WHERE  AND """

QUERY_AGREGAR_MULTIPROPIETARIO = """
    INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho,
                                    Fojas, Ano_inscripcion, Numero_inscripcion,
                                    Fecha_de_inscripcion, Ano_vigencia_inicial,
                                    Ano_vigencia_final)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
QUERY_OBTENER_ID_MULTIPROPIETARIOS_SQL = """
SELECT COUNT(*) 
FROM Multipropietarios
WHERE com_man_pred='{com_man_pred}'
"""

QUERY_ACTUALIZAR_MULTIPROPIETARIO = """
                    UPDATE Multipropietario
                    SET Ano_vigencia_final={ano_final}
                    WHERE Ano_vigencia_inicial={ano_inicial}
                    AND Ano_vigencia_final IS NULL
                    AND com_man_pred='{com_man_pred}'
                    """

QUERY_OBTENER_MULTIPROPIETARIOS_TRANSFERENCIAS_SQL = """
SELECT *
FROM Transferencias
WHERE com_man_pred = '{com_man_pred}'
"""

QUERY_OBTENER_MULTIPROPIETARIO_SQL = """
SELECT *
FROM Multipropietarios
WHERE com_man_pred={com_man_pred}
AND RUNRUT={runrut}
AND Ano_vigencia_inicial={Ano_vigencia_inicial}
"""

QUERY_DELETE_MULTIPROPIETARIO = """
DELETE FROM Multipropietario 
WHERE Ano_vigencia_inicial = {last_initial_year}
AND com_man_pred = {com_man_pred}"""