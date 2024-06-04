# Proyecto DSV

## Requisitos

- Docker Desktop instalado y en ejecución

## Ejecución

1. Asegúrate de que Docker Desktop esté en ejecución en tu máquina.

2. Abre una terminal y navega hasta el directorio raíz del proyecto.

3. Ejecuta el siguiente comando para construir las imágenes de Docker y levantar los contenedores:

```
docker-compose up --build
```

Este comando descargará las imágenes base necesarias, construirá las imágenes personalizadas para la aplicación Flask y la base de datos MySQL, y levantará los contenedores correspondientes.

4. Una vez que los contenedores estén en ejecución, podrás acceder a la aplicación web en `http://127.0.0.1:8000`.

5. Si deseas detener y eliminar los contenedores, simplemente presiona `Ctrl+C` en la terminal y luego ejecuta el siguiente comando:

```
docker-compose down
```

Esto detendrá y eliminará los contenedores.

Recuerda que la primera vez que ejecutes `docker-compose up --build`, el proceso puede demorar algunos minutos, ya que Docker descargará las imágenes base y construirá las imágenes personalizadas. En ejecuciones posteriores, el proceso será más rápido gracias al caché de imágenes.
