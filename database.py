import mysql.connector

# Configuración de la conexión a la base de datos MySQL
DB_CONFIG = {
    'host': 'localhost',  # Dirección del servidor MySQL
    'user': 'root',       # Usuario de la base de datos
    'password': 'password.',  # Contraseña del usuario
    'database': 'gestion_mantenciones'  # Nombre de la base de datos
}

# Función para crear la base de datos si no existe
def crear_base_de_datos():
    try:
        conexion = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conexion.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Base de datos '{DB_CONFIG['database']}' creada o ya existente.")
    except mysql.connector.Error as err:
        print(f"Error al crear la base de datos: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función para conectar a la base de datos
def conectar_db():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

# Función para cerrar la conexión a la base de datos
def cerrar_db(conexion):
    if conexion and conexion.is_connected():
        conexion.close()
        print("Conexión a MySQL cerrada.")

# Función para crear la tabla 'mantenciones' si no existe
def crear_tabla_mantenciones():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mantenciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_empresa VARCHAR(255) NOT NULL,
                    administrador VARCHAR(255),
                    tecnico VARCHAR(255),
                    frecuencia INT NOT NULL,
                    ultima_mantencion DATE NOT NULL,
                    notas TEXT
                )
            """)
            conexion.commit()
            print("Tabla 'mantenciones' creada o ya existente en MySQL.")
        except mysql.connector.Error as err:
            print(f"Error al crear la tabla 'mantenciones' en MySQL: {err}")
        finally:
            cerrar_db(conexion)

# Función para guardar una nueva mantención en la base de datos
def guardar_mantencion(conexion, nombre_empresa, administrador, tecnico, frecuencia, ultima_mantencion, notas):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO mantenciones (nombre_empresa, administrador, tecnico, frecuencia, ultima_mantencion, notas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre_empresa, administrador, tecnico, frecuencia, ultima_mantencion, notas))
        conexion.commit()
        print(f"Mantención para '{nombre_empresa}' guardada en MySQL.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al guardar la mantención en MySQL: {err}")
        return False

# Función para obtener todas las mantenciones de la base de datos
def obtener_mantenciones(conexion):
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT * FROM mantenciones")
        mantenciones = cursor.fetchall()
        return mantenciones
    except mysql.connector.Error as err:
        print(f"Error al obtener las mantenciones de MySQL: {err}")
        return []

# Bloque principal para ejecutar funciones de prueba si se ejecuta este archivo directamente
if __name__ == "__main__":
    crear_tabla_mantenciones()
