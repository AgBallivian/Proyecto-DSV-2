import pytest
from unittest.mock import patch, MagicMock
from algoritmo import form_solver, COMPRAVENTA, REGULARIZACION_DE_PATRIMONIO

@pytest.fixture
def formulario_compraventa():
    return {
        'CNE': COMPRAVENTA,
        'bienRaiz': {'comuna': '1', 'manzana': '2', 'predio': '3'},
        'fojas': '100',
        'fechaInscripcion': '2023-01-01',
        'nroInscripcion': '123',
        'enajenantes': [{'RUNRUT': '12345678-9', 'porcDerecho': '50'}],
        'adquirentes': [{'RUNRUT': '98765432-1', 'porcDerecho': '50'}]
    }

@pytest.fixture
def formulario_regularizacion():
    return {
        'CNE': REGULARIZACION_DE_PATRIMONIO,
        'bienRaiz': {'comuna': '1', 'manzana': '2', 'predio': '3'},
        'fojas': '100',
        'fechaInscripcion': '2023-01-01',
        'nroInscripcion': '123',
        'adquirentes': [{'RUNRUT': '98765432-1', 'porcDerecho': '100'}]
    }

@patch('algoritmo._obtener_siguiente_id_transferencias')
@patch('algoritmo._insert_enajenantes_to_transferencias')
@patch('algoritmo._insert_adquirientes_to_transferencias')
@patch('algoritmo.agregar_adquirente')
@patch('algoritmo.agregar_enajenante')
@patch('algoritmo.obtener_numero_de_atencion')
def test_form_solver_init(mock_obtener_numero, mock_agregar_enajenante, mock_agregar_adquirente, 
                          mock_insert_adquirientes, mock_insert_enajenantes, mock_obtener_id, 
                          formulario_compraventa):
    mock_obtener_id.return_value = 1
    mock_obtener_numero.return_value = 1
    
    solver = form_solver(formulario_compraventa, MagicMock())
    
    assert solver.cne == COMPRAVENTA
    assert solver.comuna == 1
    assert solver.manzana == 2
    assert solver.predio == 3
    assert len(solver.enajenantes_data) == 1
    assert len(solver.adquirentes_data) == 1
    
    mock_insert_enajenantes.assert_called_once()
    mock_insert_adquirientes.assert_called_once()
    mock_agregar_adquirente.assert_called_once()
    mock_agregar_enajenante.assert_called_once()

@patch('algoritmo.obtener_multipropietarios_vigentes')
@patch('algoritmo.actualizar_multipropietarios_por_vigencia')
def test_procesar_escenario_compraventa(mock_actualizar, mock_obtener_vigentes, formulario_compraventa):
    mock_obtener_vigentes.return_value = [{'RUNRUT': '12345678-9', 'porcDerecho': 50}]
    
    solver = form_solver(formulario_compraventa, MagicMock())
    solver.procesar_escenario_compraventa()
    
    mock_obtener_vigentes.assert_called_once()
    mock_actualizar.assert_called_once()

@patch('algoritmo.obtener_multipropietarios_commanpred')
@patch('algoritmo._obtener_ultimo_ano_inscripcion_exclusivo')
@patch('algoritmo.obtener_ano_inscripcion')
def test_procesar_escenario_regularizacion_patrimonio(mock_obtener_ano, mock_obtener_ultimo_ano, mock_obtener_multipropietarios, formulario_regularizacion):
    mock_obtener_multipropietarios.return_value = None
    mock_obtener_ano.return_value = 2023
    mock_obtener_ultimo_ano.return_value = 2022
    
    solver = form_solver(formulario_regularizacion, MagicMock())
    solver._procesar_escenario_regularizacion_patrimonio()
    
    mock_obtener_multipropietarios.assert_called_once()
    mock_obtener_ultimo_ano.assert_not_called()

@patch('algoritmo._obtener_siguiente_id_multipropietarios')
@patch('algoritmo._insert_enajenantes_to_multipropietarios')
@patch('algoritmo._insert_adquirientes_to_multipropietarios')
def test_agregar_multipropietarios(mock_insert_adquirientes, mock_insert_enajenantes, mock_obtener_id, formulario_compraventa):
    mock_obtener_id.return_value = 1
    
    solver = form_solver(formulario_compraventa, MagicMock())
    solver.agregar_multipropietarios()
    
    mock_insert_enajenantes.assert_called_once()
    mock_insert_adquirientes.assert_called_once()

@patch('algoritmo.obtener_ano_inscripcion')
@patch('algoritmo.actualizar_multipropietarios_por_vigencia')
def test_acotar_registros_previos(mock_actualizar, mock_obtener_ano, formulario_compraventa):
    mock_obtener_ano.return_value = 2023
    
    solver = form_solver(formulario_compraventa, MagicMock())
    solver._acotar_registros_previos('1-2-3')
    
    mock_actualizar.assert_called_once_with('1-2-3', 2022, solver.numero_inscripcion)

def test_ajustar_porcentajes_adquirentes(formulario_compraventa):
    solver = form_solver(formulario_compraventa, MagicMock())
    solver.enajenantes_data = [{'RUNRUT': '12345678-9', 'porcDerecho': '75'}]
    solver.adquirentes_data = [{'RUNRUT': '98765432-1', 'porcDerecho': '100'}]
    
    solver.ajustar_porcentajes_adquirentes()
    
    assert float(solver.adquirentes_data[0]['porcDerecho']) == 75

@patch('algoritmo.obtener_multipropietarios_vigentes')
def test_identificar_fantasmas(mock_obtener_vigentes, formulario_compraventa):
    mock_obtener_vigentes.return_value = [
        {'RUNRUT': '12345678-9', 'porcDerecho': 50},
        {'RUNRUT': '98765432-1', 'porcDerecho': 50}
    ]
    
    solver = form_solver(formulario_compraventa, MagicMock())
    is_ghost, lista_duenos_enajenantes = solver.identificar_fantasmas(mock_obtener_vigentes.return_value)
    
    assert not is_ghost
    assert len(lista_duenos_enajenantes) == 1
    assert lista_duenos_enajenantes[0]['RUNRUT'] == '12345678-9'

def test_marcar_como_fantasma(formulario_compraventa):
    solver = form_solver(formulario_compraventa, MagicMock())
    enajenante = {'RUNRUT': '12345678-9', 'porcDerecho': '50'}
    
    solver.marcar_como_fantasma(enajenante)
    
    assert enajenante['porcDerecho'] == 0
    assert enajenante['fecha_inscripcion'] is None
    assert enajenante['ano'] is None
    assert enajenante['numero_inscripcion'] is None

def test_obtener_lista_duenos_adquirientes(formulario_compraventa):
    solver = form_solver(formulario_compraventa, MagicMock())
    multipropietarios = [
        {'RUNRUT': '98765432-1', 'porcDerecho': 50},
        {'RUNRUT': '11111111-1', 'porcDerecho': 50}
    ]
    
    lista_duenos_adquirientes = solver.obtener_lista_duenos_adquirientes(multipropietarios)
    
    assert len(lista_duenos_adquirientes) == 1
    assert lista_duenos_adquirientes[0]['RUNRUT'] == '98765432-1'

if __name__ == '__main__':
    pytest.main()