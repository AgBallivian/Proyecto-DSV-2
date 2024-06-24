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
QUERY_ID_MULTIPROPIETARIOS = "SELECT id FROM Multipropietarios ORDER BY id DESC LIMIT 1"
QUERY_UPDATE_MULTIPROPIETARIO_SQL = """
                    UPDATE Multipropietarios
                    SET Ano_vigencia_final={ano_final}
                    WHERE Ano_vigencia_inicial={ano_inicial}
                    AND Ano_vigencia_final IS NULL
                    AND com_man_pred='{com_man_pred}'
                    """
QUERY_DELETE_MULTIPROPIETARIOS = """
DELETE FROM Multipropietarios 
WHERE Ano_vigencia_inicial = {last_initial_year}
AND com_man_pred = {com_man_pred}"""

QUERY_OBTENER_MULTIPROPIETARIOS_SQL = """
SELECT COUNT(*) 
FROM Multipropietarios
WHERE com_man_pred='{com_man_pred}'
"""

QUERY_OBTENER_MULTIPROPIETARIO_SQL = """
SELECT *
FROM Multipropietarios
WHERE com_man_pred={com_man_pred}
"""

QUERY_OBTENER_ULT_ANO_INIT = "SELECT Ano_vigencia_inicial AS Ano FROM Multipropietarios WHERE com_man_pred = {com_man_pred} ORDER BY Ano_vigencia_inicial DESC LIMIT 1"

QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIO_SQL = """
        INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho,
                                    Fojas, Ano_inscripcion, Numero_inscripcion,
                                    Fecha_de_inscripcion, Ano_vigencia_inicial,
                                    Ano_vigencia_final, Tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIO_SQL = """
        INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho,
                                    Fojas, Ano_inscripcion, Numero_inscripcion,
                                    Fecha_de_inscripcion, Ano_vigencia_inicial,
                                    Ano_vigencia_final, Tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

QUERY_CONNECTOR = """ WHERE  AND """