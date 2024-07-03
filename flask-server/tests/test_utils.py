import pytest
from utils import (
    _construir_com_man_pred,
    _deconstruir_com_man_pred,
    _obtener_ano_desde_query,
    obtener_ano_inscripcion,
    obtener_total_porcentaje
)

def test_construir_com_man_pred():
    assert _construir_com_man_pred(1, 2, 3) == "1-2-3"
    assert _construir_com_man_pred(100, 200, 300) == "100-200-300"

def test_deconstruir_com_man_pred():
    assert _deconstruir_com_man_pred("1-2-3") == ("1", "2", "3")
    assert _deconstruir_com_man_pred("100-200-300") == ("100", "200", "300")

def test_obtener_ano_desde_query():
    query_result = [{"Ano": 2022}]
    assert _obtener_ano_desde_query(query_result) == 2022

def test_obtener_ano_inscripcion():
    assert obtener_ano_inscripcion("2022-01-01") == 2022
    assert obtener_ano_inscripcion("1995-12-31") == 1995

def test_obtener_total_porcentaje():
    transacciones = [
        {"porcDerecho": 50.0},
        {"porcDerecho": 30.0},
        {"porcDerecho": 20.0}
    ]
    assert obtener_total_porcentaje(transacciones) == 100

    transacciones_vacias = []
    assert obtener_total_porcentaje(transacciones_vacias) == 0

if __name__ == '__main__':
    pytest.main()