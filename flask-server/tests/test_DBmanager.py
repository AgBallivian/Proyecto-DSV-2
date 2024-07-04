import pytest
from unittest.mock import patch, MagicMock
from DBmanager import (
    obtener_conexion_db,
    obtener_numero_de_atencion,
    agregar_formulario,
    agregar_enajenante,
    agregar_adquirente,
    _obtener_siguiente_id_transferencias,
    eliminar_multipropietarios_desde_ano,
    eliminar_multipropietarios_igual_ano,
    aplicar_filtros,
    _insert_enajenantes_to_transferencias,
    actualizar_multipropietarios_por_vigencia,
    obtener_multipropietarios_filtrados,
    obtener_multipropietarios_commanpred,
    obtener_multipropietarios_vigentes,
    obtener_formularios_por_com_man_pred,
    obtener_formulario_por_numero_inscripcion
)

@pytest.fixture
def mock_conexion():
    with patch('DBmanager.obtener_conexion_db') as mock:
        yield mock

def test_obtener_conexion_db(mock_conexion):
    conexion = obtener_conexion_db()
    assert conexion is not None

@patch('DBmanager._ejecutar_query')
def test_ejecutar_query(mock_ejecutar):
    mock_ejecutar.return_value = [{'resultado': 'test'}]
    resultado = mock_ejecutar("SELECT * FROM test")
    assert resultado == [{'resultado': 'test'}]
    mock_ejecutar.assert_called_once_with("SELECT * FROM test")

@patch('DBmanager.obtener_conexion_db')
def test_obtener_numero_de_atencion(mock_conexion):
    mock_cursor = MagicMock()
    mock_conexion.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}, {'id': 3}]

    resultado = obtener_numero_de_atencion()
    assert resultado == 3

@patch('DBmanager.obtener_conexion_db')
def test_agregar_formulario(mock_conexion):
    mock_cursor = MagicMock()
    mock_conexion.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    resultado = agregar_formulario('cne', 'comuna', 'manzana', 'predio', 'fojas', '2023-01-01', '123')
    assert resultado == 3

@patch('DBmanager.obtener_conexion_db')
def test_agregar_enajenante(mock_conexion):
    mock_cursor = MagicMock()
    mock_conexion.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    resultado = agregar_enajenante(3, '12345678-9', 50)
    assert resultado == "Ingreso el enajenante"

@patch('DBmanager.obtener_conexion_db')
def test_agregar_adquirente(mock_conexion):
    mock_cursor = MagicMock()
    mock_conexion.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    resultado = agregar_adquirente(3, '98765432-1', 50)
    assert resultado == "Ingreso el Adquirente"

@patch('DBmanager.obtener_conexion_db')
def test_obtener_siguiente_id_transferencias(mock_conexion):
    mock_cursor = MagicMock()
    mock_conexion.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 5}]

    resultado = _obtener_siguiente_id_transferencias()
    assert resultado == 6

@patch('DBmanager._ejecutar_query')
def test_eliminar_multipropietarios_desde_ano(mock_ejecutar):
    eliminar_multipropietarios_desde_ano(2020, '001-002-003')
    mock_ejecutar.assert_called_once()

@patch('DBmanager._ejecutar_query')
def test_eliminar_multipropietarios_igual_ano(mock_ejecutar):
    eliminar_multipropietarios_igual_ano(2020, '001-002-003')
    mock_ejecutar.assert_called_once()

def test_aplicar_filtros():
    filtros = aplicar_filtros(1, '001', '002', '003', 2023)
    assert len(filtros) == 5

@patch('DBmanager._ejecutar_query')
def test_insert_enajenantes_to_transferencias(mock_ejecutar):
    enajenante = {'RUNRUT': '12345678-9', 'porcDerecho': 50}
    _insert_enajenantes_to_transferencias(1, '001-002-003', enajenante, 'fojas', '2023-01-01', '123')
    mock_ejecutar.assert_called_once()

@patch('DBmanager.obtener_conexion_db')
def test_obtener_multipropietarios_filtrados(mock_conexion):
    mock_cursor = MagicMock()
    mock_conexion.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]

    resultado = obtener_multipropietarios_filtrados(1, '001', '002', '003', 2023)
    assert len(resultado) == 2

@patch('DBmanager._ejecutar_query')
def test_obtener_multipropietarios_commanpred(mock_ejecutar):
    mock_ejecutar.return_value = [{'id': 1}, {'id': 2}]
    resultado = obtener_multipropietarios_commanpred('001-002-003')
    assert len(resultado) == 2

@patch('DBmanager._ejecutar_query')
def test_obtener_multipropietarios_vigentes(mock_ejecutar):
    mock_ejecutar.return_value = [{'id': 1}, {'id': 2}]
    resultado = obtener_multipropietarios_vigentes('001-002-003')
    assert len(resultado) == 2

@patch('DBmanager._ejecutar_query')
@patch('DBmanager.obtener_enajenantes_por_formulario')
@patch('DBmanager.obtener_adquirentes_por_formulario')
def test_obtener_formularios_por_com_man_pred(mock_adquirentes, mock_enajenantes, mock_ejecutar):
    mock_ejecutar.return_value = [{
        'CNE': 1, 'Comuna': '001', 'Manzana': '002', 'Predio': '003',
        'Fojas': 'fojas', 'Fecha_de_inscripcion': MagicMock(strftime=lambda x: '2023-01-01'),
        'Numero_de_insripcion': '123', 'Numero_de_atencion': 1
    }]
    mock_enajenantes.return_value = [{'RUNRUT': '12345678-9', 'porcDerecho': 50.0}]
    mock_adquirentes.return_value = [{'RUNRUT': '98765432-1', 'porcDerecho': 50.0}]

    resultado = obtener_formularios_por_com_man_pred('001-002-003')
    assert len(resultado) == 1
    assert resultado[0]['CNE'] == 1
    assert resultado[0]['bienRaiz']['comuna'] == '001'

@patch('DBmanager._ejecutar_query')
@patch('DBmanager.obtener_enajenantes_por_formulario')
@patch('DBmanager.obtener_adquirentes_por_formulario')
def test_obtener_formulario_por_numero_inscripcion(mock_adquirentes, mock_enajenantes, mock_ejecutar):
    mock_ejecutar.return_value = [{
        'CNE': 1, 'Comuna': '001', 'Manzana': '002', 'Predio': '003',
        'Fojas': 'fojas', 'Fecha_de_inscripcion': MagicMock(strftime=lambda x: '2023-01-01'),
        'Numero_de_insripcion': '123', 'Numero_de_atencion': 1
    }]
    mock_enajenantes.return_value = [{'RUNRUT': '12345678-9', 'porcDerecho': 50.0}]
    mock_adquirentes.return_value = [{'RUNRUT': '98765432-1', 'porcDerecho': 50.0}]

    resultado = obtener_formulario_por_numero_inscripcion('123')
    assert resultado['CNE'] == 1
    assert resultado['bienRaiz']['comuna'] == '001'

if __name__ == '__main__':
    pytest.main()