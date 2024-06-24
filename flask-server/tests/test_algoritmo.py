import pytest
from unittest.mock import patch, MagicMock
from algoritmo import form_solver, COMPRAVENTA, REGULARIZACION_DE_PATRIMONIO

@pytest.fixture
def sample_formulario():
    return {
        'CNE': '8',
        'bienRaiz': {'comuna': '1', 'manzana': '2', 'predio': '3'},
        'fojas': '100',
        'fechaInscripcion': '2023-01-01',
        'nroInscripcion': '123',
        'enajenantes': [{'RUNRUT': '12345678-9', 'porcDerecho': '50'}],
        'adquirentes': [{'RUNRUT': '98765432-1', 'porcDerecho': '50'}]
    }

def test_form_solver_initialization(sample_formulario):
    solver = form_solver(sample_formulario, MagicMock())
    assert solver.cne == 8
    assert solver.comuna == 1
    assert solver.manzana == 2
    assert solver.predio == 3
    assert solver.fojas == 100
    assert solver.fecha_inscripcion == '2023-01-01'
    assert solver.numero_inscripcion == 123
    assert len(solver.enajenantes_data) == 1
    assert len(solver.adquirentes_data) == 1

@patch('algoritmo._obtener_siguiente_id_Transferencias')
@patch('algoritmo._insert_enajenantes_to_Transferencias')
@patch('algoritmo._insert_adquirientes_to_Transferencias')
def test_add_Transferencias(mock_insert_adquirientes, mock_insert_enajenantes, mock_obtener_id, sample_formulario):
    mock_obtener_id.return_value = 1
    solver = form_solver(sample_formulario, MagicMock())
    solver.add_Transferencias()
    mock_insert_enajenantes.assert_called_once()
    mock_insert_adquirientes.assert_called_once()


if __name__ == '__main__':
    pytest.main()