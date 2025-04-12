import mysql.connector

# Configuración de la conexión a la base de datos MySQL
DB_CONFIG = {
    'host': 'localhost',   # Dirección del servidor MySQL
    'port': 3306,          # Puerto del servidor MySQL (por defecto es 3306)	
    'user': 'user',       # Usuario de la base de datos
    'password': 'pasword',   # Contraseña del usuario
    'database': 'gestion_mantenciones'   # Nombre de la base de datos
}
#agregar esta funcion a main en la funcion page, solo si se usa en servidor local, en caso de ser servidor externo no funciona, se debe crear la tabla de forma manual.
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

# Función para obtener una mantención por su ID
def obtener_mantencion_por_id(conexion, mantencion_id):
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT id, nombre_empresa, administrador, tecnico, frecuencia, ultima_mantencion, notas FROM mantenciones WHERE id = %s", (mantencion_id,))
        resultado = cursor.fetchone()
        if resultado:
            return {
                'id': resultado[0],
                'empresa': resultado[1],
                'administrador': resultado[2],
                'tecnico': resultado[3],
                'frecuencia': resultado[4],
                'ultima_mantencion': str(resultado[5]),
                'notas': resultado[6]
            }
        return None
    except mysql.connector.Error as err:
        print(f"Error al obtener la mantención con ID {mantencion_id} de MySQL: {err}")
        return None

# Función para actualizar una mantención existente
def actualizar_mantencion_db(conexion, mantencion_id, nombre_empresa, administrador, tecnico, frecuencia, ultima_mantencion, notas):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            UPDATE mantenciones
            SET nombre_empresa = %s,
                administrador = %s,
                tecnico = %s,
                frecuencia = %s,
                ultima_mantencion = %s,
                notas = %s
            WHERE id = %s
        """, (nombre_empresa, administrador, tecnico, frecuencia, ultima_mantencion, notas, mantencion_id))
        conexion.commit()
        print(f"Mantención con ID {mantencion_id} actualizada en MySQL.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar la mantención con ID {mantencion_id} en MySQL: {err}")
        return False

# Función para eliminar una mantención por su ID
def eliminar_mantencion_db(conexion, mantencion_id):
    print(f"Función eliminar_mantencion_db llamada con ID: {mantencion_id}")
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM mantenciones WHERE id = %s", (mantencion_id,))
        conexion.commit()
        print(f"Mantención con ID {mantencion_id} eliminada de MySQL.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar la mantención con ID {mantencion_id} de MySQL: {err}")
        return False

# Bloque principal para ejecutar funciones de prueba si se ejecuta este archivo directamente
if __name__ == "__main__":
    crear_tabla_mantenciones()
