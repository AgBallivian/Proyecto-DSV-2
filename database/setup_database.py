import pymysql
import csv
import os

# MYSQL_HOST = 'localhost'
# MYSQL_ROOT_USER = 'root'
MYSQL_HOST = 'localhost'
MYSQL_ROOT_USER = 'admin'
MYSQL_ROOT_PASSWORD = 'admin'
MYSQL_USER = 'admin'
MYSQL_PASSWORD = 'admin'
MYSQL_DB = 'proyectodsv'

def create_database():
    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_ROOT_USER,
                                 password=MYSQL_ROOT_PASSWORD)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s", (MYSQL_DB,))
            result = cursor.fetchone()

            if result:
                print(f"Database '{MYSQL_DB}' already exists.")
                cursor.execute(f"DROP DATABASE {MYSQL_DB}")
                print(f"Database '{MYSQL_DB}' dropped successfully.")
                cursor.execute(f"CREATE DATABASE {MYSQL_DB}")
                print(f"Database '{MYSQL_DB}' created successfully.")
            else:
                cursor.execute(f"CREATE DATABASE {MYSQL_DB}")
                print(f"Database '{MYSQL_DB}' created successfully.")

        connection.commit()

    finally:
        connection.close()

def create_tables():
    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_ROOT_USER,
                                 password=MYSQL_ROOT_PASSWORD,
                                 db=MYSQL_DB)

    try:
        with connection.cursor() as cursor:
            # Crear tabla 'formulario'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS formulario (
                    Numero_de_atencion INT,
                    CNE INT,
                    Comuna INT,
                    Manzana INT,
                    Predio INT,
                    Fojas INT,
                    Fecha_de_inscripcion TIMESTAMP,
                    Numero_de_insripcion INT,
                    PRIMARY KEY (Numero_de_atencion)
                )
            """)

            # Crear tabla 'Adquirentes'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Adquirentes (
                    id INT,
                    Adquirente_id INT,
                    RUNRUT VARCHAR(100),
                    porcDerecho FLOAT,
                    FOREIGN KEY (Adquirente_id) REFERENCES formulario(Numero_de_atencion)
                )
            """)

            # Crear tabla 'Enajenantes'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Enajenantes (
                    id INT,
                    enajenante_id INT,
                    RUNRUT VARCHAR(100),
                    porcDerecho FLOAT,
                    FOREIGN KEY (enajenante_id) REFERENCES formulario(Numero_de_atencion)
                )
            """)

            # Crear tabla 'Transacciones'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Transferencias (
                    id INT,
                    com_man_pred VARCHAR(100),
                    RUNRUT VARCHAR(100),
                    porcDerecho FLOAT,
                    Fojas INT,
                    Ano_inscripcion INT,
                    Numero_inscripcion INT,
                    Fecha_de_inscripcion TIMESTAMP,
                    Ano_vigencia_inicial INT,
                    Ano_vigencia_final INT,
                    Tipo VARCHAR(100),
                    PRIMARY KEY (id)
                )
            """)

            # Crear tabla 'regiones'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regiones (
                    id_region INT PRIMARY KEY,
                    descripcion VARCHAR(100)
                )
            """)

            # Crear tabla 'comunas'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comunas (
                    id_comuna INT PRIMARY KEY,
                    descripcion VARCHAR(100),
                    id_region INT,
                    FOREIGN KEY (id_region) REFERENCES regiones(id_region)
                )
            """)

            # Crear tabla 'Multipropietarios'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Multipropietarios (
                    id INT,
                    com_man_pred VARCHAR(100),
                    RUNRUT VARCHAR(100),
                    porcDerecho FLOAT,
                    Fojas INT,
                    Ano_inscripcion INT,
                    Numero_inscripcion INT,
                    Fecha_de_inscripcion TIMESTAMP,
                    Ano_vigencia_inicial INT,
                    Ano_vigencia_final INT,
                    PRIMARY KEY (id)
                )
            """)

        connection.commit()
        print("Tables created/replaced successfully.")

    finally:
        connection.close()

def insert_default_data():
    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_ROOT_USER,
                                 password=MYSQL_ROOT_PASSWORD,
                                 db=MYSQL_DB)

    try:
        with connection.cursor() as cursor:
            # Eliminar datos existentes
            cursor.execute("DELETE FROM Transferencias")

            # Insertar datos challa en la tabla 'multipropietario'
            transferencia_data = [
                (1, '394-514-23', "123456789", 50.00, 1, 2021, 1, '2021-01-01', 2021, None, "Enjante"),
                (2, '8-54-456', "987654321", 75.50, 2, 2022, 2, '2022-02-15', 2022, None, "Adquirente"),
                (3, '7-22-22', "456789012", 100.00, 3, 2023, 3, '2023-03-30', 2023, None, "Adquirente")
            ]

            sql = """
                INSERT INTO Transferencias (id, com_man_pred, RUNRUT, porcDerecho,
                                              Fojas, Ano_inscripcion, Numero_inscripcion, Fecha_de_inscripcion,
                                              Ano_vigencia_inicial, Ano_vigencia_final, Tipo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(sql, transferencia_data)

        connection.commit()    
        with connection.cursor() as cursor:
            # Eliminar datos existentes de la tabla 'formulario'
            cursor.execute("DELETE FROM formulario")
            formulario_data = [
                (1, 8, 13101, 514, 23, 100, '2023-06-01', 1),
                (2, 99, 11214, 54, 456, 200, '2023-06-02', 2),
                (3, 8, 11111, 22, 22, 300, '2023-06-03', 3)
            ]

            formulario_sql = """
                INSERT INTO formulario (
                    Numero_de_atencion, CNE, Comuna, Manzana, Predio,
                    Fojas, Fecha_de_inscripcion, Numero_de_insripcion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(formulario_sql, formulario_data)

            connection.commit()
            print("Default data inserted successfully.")

        with connection.cursor() as cursor:
            # Eliminar datos existentes
            cursor.execute("DELETE FROM Enajenantes")
            enajenantes_data = [
                (1, 1, "123456789", 50),
                (2, 1, "125212885", 25),
                (3, 1, "268957861", 25),
                (4, 2, "462980732", 50),
                (5, 2, "884129301", 50),
                (6, 3, "386083174", 5),
                (7, 3, "804611919", 95)
            ]

            sql = """
                INSERT INTO Enajenantes (id, enajenante_id, 
                                        RUNRUT, porcDerecho)
                VALUES (%s, %s, %s, %s)
            """
            cursor.executemany(sql, enajenantes_data)

        connection.commit()

        with connection.cursor() as cursor:
            # Eliminar datos existentes
            cursor.execute("DELETE FROM Adquirentes")
            adquirentes_data = [
                (1, 1, "552405920", 100),
                (2, 1, "621975923", 75),
                (3, 2, "625157514", 25),
                (4, 3, "549855557", 100)
            ]

            sql = """
                INSERT INTO Adquirentes (id, Adquirente_id,
                                        RUNRUT, porcDerecho)
                VALUES (%s, %s, %s, %s)
            """
            cursor.executemany(sql, adquirentes_data)

        connection.commit()

    finally:
        connection.close()


def cargar_datos_desde_csv():
    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_ROOT_USER,
                                 password=MYSQL_ROOT_PASSWORD,
                                 db=MYSQL_DB)

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM regiones")
            cursor.execute("DELETE FROM comunas")

            with open(os.path.join(os.path.dirname(__file__), 'csv', 'regiones.csv'), 'r', encoding='utf-8-sig') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=';')
                next(csvreader)
                regiones_data = [(int(fila[0]), fila[1]) for fila in csvreader]

                sql = "INSERT INTO regiones (id_region, descripcion) VALUES (%s, %s)"
                cursor.executemany(sql, regiones_data)

            # Cargar datos desde comunas.csv
            with open(os.path.join(os.path.dirname(__file__), 'csv', 'comunas.csv'), 'r', encoding='utf-8-sig') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=';')
                next(csvreader)  # Omitir el encabezado

                comunas_data = [(int(fila[0]), fila[1], int(fila[2])) for fila in csvreader]

                sql = "INSERT INTO comunas (id_comuna, descripcion, id_region) VALUES (%s, %s, %s)"
                cursor.executemany(sql, comunas_data)

        connection.commit()
        print("Datos cargados desde CSV correctamente.")

    finally:
        connection.close()

if __name__ == '__main__':
    create_database()
    create_tables()
    insert_default_data()
    cargar_datos_desde_csv()
    