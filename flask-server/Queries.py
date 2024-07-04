INTERNAL_SERVER_ERROR = 500

QUERY_ALL_MULTIPROPIETARIOS = "SELECT * FROM Multipropietarios"
QUERY_ID_MULTIPROPIETARIOS = "SELECT id FROM Multipropietarios ORDER BY id DESC LIMIT 1"
QUERY_SELECT_MULTIPROPIETARIOS_VIGENTES = """
SELECT * FROM Multipropietarios
WHERE com_man_pred = '{com_man_pred}'
AND Ano_vigencia_final IS NULL
"""
OBTENER_MULTIPROPIETARIO_COMMANPRED_SQL = "SELECT * FROM Multipropietarios WHERE com_man_pred = '{com_man_pred}'"

QUERY_ALL_FORMULARIOS = "SELECT * FROM formulario"
QUERY_FORMULARIO_FILTER_ID = "SELECT * FROM Multipropietarios WHERE id = %s"
QUERY_FORMULARIO_FILTER_NUM_ATENCION =  "SELECT * FROM formulario WHERE Numero_de_atencion = %s"
QUERY_SELECT_FORMULARIO_NUMERO_INSCRIPCION =  "SELECT * FROM formulario WHERE Numero_de_insripcion = {numero_de_inscripcion}"
QUERY_FORMULARIO_COM_MAN_PRED = """
SELECT Numero_de_atencion, CNE, Comuna, Manzana, Predio, Fojas, Fecha_de_inscripcion, Numero_de_insripcion 
FROM formulario 
WHERE Comuna = '{comuna}' AND
Manzana = '{manzana}' AND
Predio = '{predio}'
ORDER BY Fecha_de_inscripcion
"""

QUERY_ENAJENANTES_POR_FORMULARIO = """
SELECT RUNRUT, porcDerecho FROM Enajenantes
WHERE enajenante_id = '{numero_atencion}'
"""

QUERY_ADQUIRENTES_POR_FORMULARIO = """
SELECT RUNRUT, porcDerecho FROM Adquirentes
WHERE Adquirente_id = '{numero_atencion}'
"""
QUERY_INSERTAR_ENAJENANTES_MULTIPROPIETARIOS_SQL = """
        INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho, Fojas, Ano_inscripcion, Numero_inscripcion, Fecha_de_inscripcion, Ano_vigencia_inicial, Ano_vigencia_final)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
QUERY_ALL_ENAJENANTES = "SELECT * FROM Enajenantes"
QUERY_ENAJENANTES_INFO = "SELECT RUNRUT, porcDerecho FROM Enajenantes WHERE enajenante_id = %s"

QUERY_INSERTAR_ADQUIRENTES_MULTIPROPIETARIOS_SQL = """
        INSERT INTO Multipropietarios (id, com_man_pred, RUNRUT, porcDerecho,
                                    Fojas, Ano_inscripcion, Numero_inscripcion,
                                    Fecha_de_inscripcion, Ano_vigencia_inicial,
                                    Ano_vigencia_final)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
QUERY_ALL_ADQUIRENTES = "SELECT * FROM Adquirentes"
QUERY_ADQUIRENTES_INFO = "SELECT RUNRUT, porcDerecho FROM Adquirentes WHERE Adquirente_id = %s"

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

QUERY_OBTENER_ULT_ANO_INSCRIPCION_EXCLUSIVO = """
SELECT Ano_inscripcion AS Ano FROM Transferencias
WHERE com_man_pred = '{com_man_pred}' 
AND Numero_inscripcion != {numero_inscripcion} 
ORDER BY Ano_inscripcion DESC LIMIT 1
"""

QUERY_OBTENER_ULT_ANO_INSCRIPCION = """
SELECT Ano_inscripcion AS Ano FROM Transferencias
WHERE com_man_pred = '{com_man_pred}' 
ORDER BY Ano_inscripcion DESC LIMIT 1
"""

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


QUERY_ACTUALIZAR_MULTIPROPIETARIO = """
                    UPDATE Multipropietarios
                    SET Ano_vigencia_final={ano_final}
                    WHERE Ano_vigencia_inicial={ano_inicial}
                    AND Ano_vigencia_final IS NULL
                    AND com_man_pred='{com_man_pred}'
                    """

QUERY_ACTUALIZAR_TRANSFERENCIAS = """
                UPDATE Transferencias
                    SET Ano_vigencia_final={ano_final}
                    WHERE Ano_vigencia_final IS NULL
                    AND com_man_pred='{com_man_pred}'
                    """


QUERY_OBTENER_TRANFERENCIAS_DESDE_ANO = """
SELECT Numero_inscripcion FROM Transferencias 
WHERE com_man_pred = '{com_man_pred}'
and Ano_inscripcion > {ano_inscripcion} 
ORDER by Ano_inscripcion
"""

QUERY_OBTENER_TRANFERENCIAS_IGUAL_ANO = """
SELECT * FROM Transferencias 
WHERE com_man_pred = '{com_man_pred}'
and Ano_inscripcion = {ano_inscripcion} 
ORDER by id DESC
"""

QUERY_ELIMINAR_FILA_MULTIPROPIETARIOS_DESDE_ANO = """
DELETE FROM Multipropietarios 
WHERE Ano_inscripcion > {ano_inscripcion}
AND com_man_pred = '{com_man_pred}'
"""

QUERY_ELIMINAR_FILA_MULTIPROPIETARIOS_IGUAL_ANO = """
DELETE FROM Multipropietarios 
WHERE Ano_inscripcion = {ano_inscripcion}
AND com_man_pred = '{com_man_pred}'
"""

QUERY_ACTUALIZAR_MULTIPROPIETARIOS_POR_VIGENCIA = """
UPDATE Multipropietarios SET
Ano_vigencia_final={ano_final}
WHERE com_man_pred = '{com_man_pred}' AND
Numero_inscripcion = {numero_inscripcion} AND
id < {id}
"""
QUERY_OBTENER_NUM_MULTIPROPIETARIO_SEGUN_ID = """
SELECT Numero_inscripcion FROM Multipropietarios 
WHERE com_man_pred = '{com_man_pred}' AND
id = {id}-1
"""
QUERY_OBTENER_ID_MULTIPROPIETARIO_SEGUN_NUM = """
SELECT id FROM Multipropietarios 
WHERE com_man_pred = '{com_man_pred}' AND 
Numero_inscripcion = {numero_inscripcion} LIMIT 1
"""