# Gestión de Mantenciones

Este proyecto es una aplicación para gestionar mantenciones programadas de empresas. Utiliza **Flet** para la interfaz gráfica y **MySQL** como base de datos para almacenar la información.

## Características

- **Calendario interactivo**: Visualiza las mantenciones programadas en un calendario mensual.
- **Gestión de datos**: Permite agregar, visualizar y almacenar información de mantenciones.
- **Base de datos MySQL**: Almacena los datos de manera persistente.

## Requisitos

- Python 3.8 o superior.
- MySQL Server instalado y configurado.
- Las siguientes dependencias de Python (ver archivo `requirements.txt`):
  - `flet`
  - `mysql-connector-python`

## Instalación

1. Clona este repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura la base de datos MySQL:
   - Asegúrate de que el servidor MySQL esté en ejecución.
   - Modifica las credenciales en `database.py` si es necesario.

4. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## Uso

1. **Agregar mantenciones**:
   - Completa los campos del formulario con la información de la mantención.
   - Haz clic en el botón "Guardar Mantención".

2. **Visualizar mantenciones**:
   - Las mantenciones programadas aparecerán en el calendario.
   - Los días con mantenciones estarán marcados con un indicador rojo.

3. **Navegar entre meses**:
   - Usa los botones de navegación (< y >) para cambiar de mes.

## Estructura del Proyecto

- `main.py`: Contiene la lógica principal de la aplicación y la interfaz gráfica.
- `database.py`: Maneja la conexión y operaciones con la base de datos MySQL.
- `requirements.txt`: Lista de dependencias necesarias para el proyecto.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para sugerir mejoras o reportar problemas.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
