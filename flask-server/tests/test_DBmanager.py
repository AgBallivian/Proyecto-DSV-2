import pytest
import pymysql
from unittest.mock import patch, MagicMock
from DBmanager import (
    obtener_conexion_db,
    _ejecutar_query,
    obtener_numer_de_atencion,
    add_formulario,
    add_enajenante,
    add_adquirente,
    _obtener_siguiente_id_Transferencias,
    _obtener_ano_final,
    delete_Transferencias_antiguos,
    obtener_Transferencias,
    obtener_Transferencias_filtrados,
    _insert_enajenantes_to_Transferencias,
    _insert_adquirientes_to_Transferencias,
    _obtener_ultimo_ano_inicial,
    obtener_multipropietario,
    _actualizar_multipropietarios_por_vigencia
)

@pytest.fixture
def mock_connection():
    with patch('DBmanager.obtener_conexion_db') as mock:
        yield mock

def test_obtener_conexion_db(mock_connection):
    mock_connection.return_value = MagicMock()
    connection = obtener_conexion_db()
    assert connection is not None

def test_ejecutar_query(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'result': 'test'}]

    result = _ejecutar_query("SELECT * FROM test")
    assert result == [{'result': 'test'}]

def test_obtener_numer_de_atencion(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}, {'id': 3}]

    result = obtener_numer_de_atencion()
    assert result == 3

def test_add_formulario(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    result = add_formulario('cne', 'comuna', 'manzana', 'predio', 'fojas', '2023-01-01', '123')
    assert result == 3

def test_add_enajenante(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    result = add_enajenante(3, '12345678-9', 50)
    assert result == "Ingreso el enajenante"

def test_add_adquirente(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    result = add_adquirente(3, '98765432-1', 50)
    assert result == "Ingreso el Adquirente"

def test_obtener_siguiente_id_Transferencias(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 5}]

    result = _obtener_siguiente_id_Transferencias()
    assert result == 6

def test_obtener_ano_final():
    result = _obtener_ano_final('2023-01-01')
    assert result == 2022

@patch('DBmanager._ejecutar_query')
def test_delete_Transferencias_antiguos(mock_ejecutar_query):
    delete_Transferencias_antiguos(2020, '001', '002', '003')
    mock_ejecutar_query.assert_called_once()

@patch('DBmanager._ejecutar_query')
def test_obtener_Transferencias(mock_ejecutar_query):
    mock_ejecutar_query.return_value = [{'COUNT(*)': 5}]
    result = obtener_Transferencias('001', '002', '003')
    assert result == 5

@patch('DBmanager.obtener_conexion_db')
def test_obtener_Transferencias_filtrados(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    result = obtener_Transferencias_filtrados(1, '001', '002', '003', 2023)
    assert len(result) == 2

@patch('DBmanager._ejecutar_query')
def test_insert_enajenantes_to_Transferencias(mock_ejecutar_query):
    enajenante = {'RUNRUT': '12345678-9', 'porcDerecho': 50}
    _insert_enajenantes_to_Transferencias(1, '001-002-003', enajenante, 'fojas', '2023-01-01', '123')
    mock_ejecutar_query.assert_called_once()

@patch('DBmanager._ejecutar_query')
def test_insert_adquirientes_to_Transferencias(mock_ejecutar_query):
    adquirente = {'RUNRUT': '98765432-1', 'porcDerecho': 50}
    _insert_adquirientes_to_Transferencias(1, '001-002-003', adquirente, 'fojas', '2023-01-01', '123')
    mock_ejecutar_query.assert_called_once()

@patch('DBmanager._ejecutar_query')
def test_obtener_ultimo_ano_inicial(mock_ejecutar_query):
    mock_ejecutar_query.return_value = [{'Ano': 2020}]
    result = _obtener_ultimo_ano_inicial('001', '002', '003')
    assert result == 2020

@patch('DBmanager._ejecutar_query')
def test_obtener_multipropietario(mock_ejecutar_query, mock_connection):
    mock_cursor = MagicMock()
    mock_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}, {'id': 3}]

    result = obtener_multipropietario(2)
    assert result == {'id': 2}
@patch('DBmanager._ejecutar_query')
@patch('DBmanager._construir_query_actualizar_multipropietarios')
@patch('DBmanager._ejecutar_query_actualizar_multipropietarios')
def test_actualizar_multipropietarios_por_vigencia(mock_ejecutar_actualizar, mock_construir_query, mock_ejecutar_query, mock_connection):
    mock_construir_query.return_value = "UPDATE query"
    result = _actualizar_multipropietarios_por_vigencia(2020, '001', '002', '003', '2023-01-01')
    assert result == True
    mock_ejecutar_actualizar.assert_called_once_with("UPDATE query")

if __name__ == '__main__':
    pytest.main()