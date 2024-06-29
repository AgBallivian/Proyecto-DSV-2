import pymysql

def _construir_com_man_pred(comuna, manzana, predio):
    return f"{comuna}-{manzana}-{predio}"

def _deconstruir_com_man_pred(com_man_pred):
    comuna, manzana, predio = com_man_pred.split("-")
    return comuna, manzana, predio

def _obtener_ano_desde_query(query_result):
    return query_result[0]['Ano']

def obtener_ano_inscripcion(fecha_inscripcion):
    return int(fecha_inscripcion.split("-")[0])

def obtener_total_porcentaje(transactions):
    total = 0
    for transaction in transactions:
        total += float(transaction['porcDerecho'])
    return total
