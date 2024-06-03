

const tablaFormularios = document.querySelector('table');
const filtroComuna = document.getElementById('filtroComuna');

function filtrarFormularios() {
const comunaFiltro = filtroComuna.value.toLowerCase();
const filas = tablaFormularios.getElementsByTagName('tr');

for (let i = 1; i < filas.length; i++) {
    const celdaComuna = filas[i].getElementsByTagName('td')[2]; // suponiendo que la columna comuna es la tercera
    const comuna = celdaComuna.textContent.toLowerCase();

    if (comuna.includes(comunaFiltro)) {
    filas[i].style.display = '';
    } else {
    filas[i].style.display = 'none';
    }
}
}

//nose si es input pq debiera ser un drop down por cada parametro epro este es para la comumna, faltaria recorrer el excel
filtroComuna.addEventListener('input', filtrarFormularios);