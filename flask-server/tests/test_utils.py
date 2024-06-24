import pytest
from utils import (
    _construir_com_man_pred,
    _obtener_count_Transferencias,
    _obtener_ano_desde_query,
    obtener_ano_inscripcion,
    _obtener_ano_final,
    obtener_total_porcentaje
)

def test_construir_com_man_pred():
    assert _construir_com_man_pred("001", "002", "003") == "001-002-003"
    assert _construir_com_man_pred("100", "200", "300") == "100-200-300"

def test_obtener_count_Transferencias():
    Transferencias = [{"COUNT(*)": 5}]
    assert _obtener_count_Transferencias(Transferencias) == 5

def test_obtener_ano_desde_query():
    query_result = [{"Ano": 2022}]
    assert _obtener_ano_desde_query(query_result) == 2022

def test_obtener_ano_inscripcion():
    assert obtener_ano_inscripcion("2022-01-01") == 2022
    assert obtener_ano_inscripcion("1995-12-31") == 1995

def test_obtener_ano_final():
    assert _obtener_ano_final("2022-01-01") == 2021
    assert _obtener_ano_final("1995-12-31") == 1994

def test_obtener_total_porcentaje():
    transactions = [
        {"porcDerecho": "50"},
        {"porcDerecho": "30"},
        {"porcDerecho": "20"}
    ]
    assert obtener_total_porcentaje(transactions) == 100

if __name__ == '__main__':
    pytest.main()