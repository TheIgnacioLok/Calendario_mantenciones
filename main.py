import flet as ft   # Importar la biblioteca Flet para crear la interfaz de usuario
from database import crear_base_de_datos, crear_tabla_mantenciones, conectar_db, cerrar_db, guardar_mantencion, obtener_mantenciones, obtener_mantencion_por_id, actualizar_mantencion_db, eliminar_mantencion_db   # Importar funciones de la base de datos
import datetime # Importar el módulo datetime para manejar fechas
import calendar # Importar el módulo calendar para manejar calendarios

# Clase personalizada para generar un calendario con mantenciones programadas
class CalendarioMantenciones(ft.Column):
    def __init__(self, anio, mes, mantenciones_programadas, ancho_celda, alto_encabezado, **kwargs):    # Inicializar la clase
        # Inicialización de la clase con parámetros como año, mes y mantenciones
        super().__init__(horizontal_alignment=ft.CrossAxisAlignment.STRETCH, **kwargs)  # Llamar al constructor de la clase base
        self.anio = anio    # Asignar el año
        self.mes = mes  # Asignar el mes
        self.mantenciones_programadas = mantenciones_programadas  # Asignar las mantenciones programadas
        self.ancho_celda = ancho_celda  # Asignar el ancho de la celda
        self.alto_encabezado = alto_encabezado  # Asignar la altura del encabezado
        self.controls = self._crear_controles() # Crear los controles del calendario al inicializar la clase

    # Método para crear el calendario mensual con mantenciones
    def crear_calendario_mensual(self, year, month, mantenciones_programadas):  # Crear el calendario mensual
        # Obtener el primer día de la semana y el número de días del mes
        first_day_weekday, num_days = calendar.monthrange(year, month)  # Obtener el primer día de la semana y el número de días del mes
        primer_dia_ajustado = (first_day_weekday - calendar.MONDAY) % 7 # Ajustar el primer día de la semana al lunes
        dias_del_mes = []   # Lista para almacenar los días del mes
        hoy = datetime.date.today() # Obtener la fecha actual
        # Agregar contenedores vacíos al inicio del mes
        for _ in range(primer_dia_ajustado):    # Agregar contenedores vacíos al inicio del mes
            dias_del_mes.append(ft.Container(width=self.ancho_celda, height=70))    # Contenedor vacío para el primer día de la semana
        # Agregar los días del mes
        for day in range(1, num_days + 1):  # Iterar sobre los días del mes
            fecha_actual = datetime.date(year, month, day)  # crear un objeto de fecha para el día actual
            es_hoy = (fecha_actual == hoy)  # Verificar si el día actual es hoy
            mantenciones_hoy = []   # Lista para almacenar las mantenciones programadas para hoy
            for mantencion in mantenciones_programadas: # Iterar sobre las mantenciones programadas
                for fecha_tentativa in mantencion['fechas_tentativas']: # Iterar sobre las fechas tentativas
                    # Convertir fecha_tentativa a datetime.date para la comparación
                    fecha_tentativa_date = datetime.datetime.strptime(fecha_tentativa, "%Y-%m-%d").date()   # Convertir la cadena a un objeto de fecha
                    if fecha_actual == fecha_tentativa_date:    # Si la fecha actual es igual a la fecha tentativa
                        mantenciones_hoy.append(mantencion) # Agregar la mantención a la lista de mantenciones hoy
                        break   # Salir del bucle si se encuentra una coincidencia
            day_number = ft.Text(str(day), size=16) # Crear un widget de texto para el número del día
            content_children = [ft.Container(content=day_number, alignment=ft.alignment.center)]    # Contenedor para el número del día
            tooltip_content = []    # Lista para almacenar el contenido del tooltip
            company_names = []  # Lista para almacenar los nombres de las empresas
            tiene_mantencion = False    # Variable para verificar si hay mantenciones hoy
            if mantenciones_hoy:    # Si hay mantenciones hoy
                tiene_mantencion = True   # Cambiar el color del día
                company_names_widgets = []  # Lista para almacenar los widgets de nombres de empresas
                for mantencion in mantenciones_hoy: # iterar sobre las mantenciones
                    tooltip_content.append(f"Empresa: {mantencion['empresa']}\nNotas: {mantencion.get('notas', '')}") # Agregar notas al tooltip
                    company_names_widgets.append(   ## Crear un widget de texto para cada empresa
                        ft.Text(mantencion['empresa'], size=10, selectable=True, text_align=ft.TextAlign.CENTER),   # # Crear un widget de texto para el nombre de la empresa
                    )
                content_children.extend(company_names_widgets) # Agregar los widgets de nombres de empresas al contenido

            day_content = ft.Column(    # Crear un contenedor para el contenido del día
                controls=content_children,  # Agregar los widgets de contenido
                alignment=ft.MainAxisAlignment.CENTER,  # Alinear el contenido al centro
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Alinear el contenido horizontalmente al centro
                spacing=5   # Espaciado entre los widgets
            )

            indicator = None    # Crear un indicador para mostrar si hay mantenciones
            if tiene_mantencion:    # Si hay mantenciones hoy
                indicator = ft.Container(   # Crear un contenedor para el indicador
                    width=8,    # Ancho del indicador
                    height=8,   # Altura del indicador
                    bgcolor=ft.colors.RED,  # Color de fondo del indicador
                    border_radius=4,    # Radio del borde del indicador
                    alignment=ft.alignment.bottom_right # Alinear el indicador a la esquina inferior derecha
                )
            day_container = ft.Container(   # Crear un contenedor para el día
                content=ft.Stack(   # # Crear un contenedor apilado para el día
                    [
                        day_content,    # Contenido del día
                        indicator if indicator else ft.Container()  #
                    ],
                    expand=True # Expandir el contenedor apilado
                ),
                width=self.ancho_celda, # Ancho del contenedor
                height=70,  # Altura del contenedor
                alignment=ft.alignment.top_center,  # Alinear el contenido al centro
                bgcolor=ft.Colors.BLUE_GREY_600 if es_hoy else ft.Colors.TRANSPARENT,   # Color de fondo del contenedor
                border=ft.border.all(1, ft.Colors.BLACK12) if es_hoy else None, # # Borde del contenedor
                border_radius=ft.border_radius.all(5) if es_hoy else None,  # Radio del borde del contenedor
                tooltip="\n\n".join(tooltip_content) if tooltip_content else None   # Tooltip para mostrar información adicional
            )
            dias_del_mes.append(day_container)  # Agregar el contenedor del día a la lista de días del mes
        # Agregar contenedores vacíos al final del mes si es necesario
        while len(dias_del_mes) % 7 != 0:   # Asegurarse de que haya 7 días por semana
            dias_del_mes.append(ft.Container(width=self.ancho_celda, height=70))    # Contenedor vacío para el último día de la semana
        semanas = [dias_del_mes[i:i + 7] for i in range(0, len(dias_del_mes), 7)]   # # Dividir los días del mes en semanas
        return semanas  # Devolver las semanas con los días del mes

    # Método para crear los controles del calendario
    def _crear_controles(self): # Crear los controles del calendario
        controles = []  # Lista para almacenar los controles del calendario
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"] # Lista de días de la semana
        # Crear encabezados para los días de la semana
        encabezados_semana = [  # Crear encabezados para los días de la semana
            ft.Container(   # Crear un contenedor para cada encabezado
                ft.Text(dia, weight=ft.FontWeight.BOLD, size=16),   # Crear un widget de texto para el día de la semana
                alignment=ft.alignment.center,  # Alinear el texto al centro
                width=self.ancho_celda, # Ancho del encabezado
                height=self.alto_encabezado # Altura del encabezado
            )
            for dia in dias_semana  # Iterar sobre los días de la semana
        ]
        fila_encabezados = ft.Row(controls=encabezados_semana, alignment=ft.MainAxisAlignment.SPACE_EVENLY) # Crear una fila para los encabezados
        controles.append(fila_encabezados)  # Agregar la fila de encabezados a los controles
        semanas = self.crear_calendario_mensual(self.anio, self.mes, self.mantenciones_programadas) # Crear el calendario mensual
        for semana in semanas:  # Iterar sobre las semanas del calendario
            # Asegurarse de que cada semana tenga 7 elementos
            while len(semana) < 7:  # si la semana tiene menos de 7 elementos
                semana.append(ft.Container(width=self.ancho_celda, height=70))  # Contenedor vacío para completar la semana 
            controles.append(ft.Row(controls=semana, alignment=ft.MainAxisAlignment.SPACE_EVENLY))  # # Crear una fila para cada semana
        return controles    # Devolver los controles del calendario

    # Método para actualizar el calendario con nuevos datos
    def actualizar(self, anio, mes, mantenciones_programadas):  # Actualizar el calendario
        self.anio = anio    # Asignar el año
        self.mes = mes  # Asignar el mes
        self.mantenciones_programadas = mantenciones_programadas    # Asignar las mantenciones programadas
        self.controls = self._crear_controles() # Crear los controles del calendario
        self.update()   # Actualizar el calendario

# Función principal de la aplicación
def main(page: ft.Page):    
    

    # Configuración inicial de la página
    page.title = "Gestión de Mantenciones"  # Título de la página
    hoy = datetime.date.today() # Obtener la fecha actual
    mes_actual = hoy.month  # Obtener el mes actual
    anio_actual = hoy.year  # Obtener el año actual
    editando_id = None  # Variable para rastrear el ID de la mantención que se está editando

    # --- Definición de Controles de Entrada ---
    nombre_empresa_input = ft.TextField(label="Nombre de la Empresa")   # Campo de texto para el nombre de la empresa
    administrador_input = ft.TextField(label="Administrador Solicitante")   # Campo de texto para el administrador solicitante
    tecnico_input = ft.TextField(label="Técnico a Cargo")   # Campo de texto para el técnico a cargo
    frecuencia_input = ft.TextField(label="Frecuencia (en meses)", keyboard_type=ft.KeyboardType.NUMBER)    # Campo de texto para la frecuencia en meses
    fecha_ultima_input = ft.TextField(label="Fecha Última Mantención (YYYY-MM-DD)") # Campo de texto para la fecha de la última mantención
    notas_input = ft.TextField(label="Notas", multiline=True)   # Campo de texto para notas
    # --- Definición de Widgets del Calendario y Tabla ---
    ancho_celda = 100   # Ancho de cada celda del calendario
    alto_encabezado = 50    # Altura del encabezado del calendario

    calendario_widget = CalendarioMantenciones(anio_actual, mes_actual, [], ancho_celda, alto_encabezado)   # Crear el widget del calendario
    mes_anio_text = ft.Text(f"{calendar.month_name[mes_actual]} {anio_actual}", weight=ft.FontWeight.BOLD)  # Texto para mostrar el mes y año actual

    # Contenedor para la tabla de mantenciones (inicialmente vacío)
    tabla_mantenciones_container = ft.Container()   # Crear un contenedor para la tabla de mantenciones

    # Función para navegar entre meses en el calendario
    def navegar_mes(direccion): # Navegar entre meses
        nonlocal mes_actual, anio_actual    # Obtener el mes y año actual
        if direccion == -1:   # Si la dirección es -1, navegar al mes anterior
            mes_actual -= 1 # Restar 1 al mes actual
            if mes_actual < 1:  # Si el mes actual es menor que 1, ajustar el año
                mes_actual = 12 # Establecer el mes actual a diciembre
                anio_actual -= 1    # Restar 1 al año actual
        elif direccion == 1:    # Si la dirección es 1, navegar al mes siguiente
            mes_actual += 1 # Sumar 1 al mes actual
            if mes_actual > 12: # Si el mes actual es mayor que 12, ajustar el año
                mes_actual = 1  # Establecer el mes actual a enero
                anio_actual += 1    # Sumar 1 al año actual
        cargar_mantenciones()   # Cargar las mantenciones para el nuevo mes

    # Botones para navegar entre meses
    boton_anterior = ft.IconButton(ft.Icons.ARROW_LEFT, on_click=lambda _: navegar_mes(-1)) # Botón para navegar al mes anterior
    boton_siguiente = ft.IconButton(ft.Icons.ARROW_RIGHT, on_click=lambda _: navegar_mes(1))    # Botón para navegar al mes siguiente

    def limpiar_formulario():   # Limpiar el formulario de entrada
        nombre_empresa_input.value = "" # Limpiar el campo de nombre de la empresa
        administrador_input.value = ""  # Limpiar el campo de administrador solicitante
        tecnico_input.value = ""    # Limpiar el campo de técnico a cargo
        frecuencia_input.value = "" # Limpiar el campo de frecuencia
        fecha_ultima_input.value = ""   # Limpiar el campo de fecha de la última mantención
        notas_input.value = ""  # Limpiar el campo de notas
        page.update()   # Actualizar la página

    def cargar_datos_en_formulario(mantencion): # Cargar los datos de la mantención en el formulario
        nonlocal editando_id    # Obtener el ID de la mantención que se está editando
        editando_id = mantencion['id']  # Asignar el ID de la mantención a la variable editando_id
        nombre_empresa_input.value = mantencion['empresa']  # Cargar el nombre de la empresa en el campo de texto
        administrador_input.value = mantencion['administrador'] # Cargar el administrador solicitante en el campo de texto
        tecnico_input.value = mantencion['tecnico'] # Cargar el técnico a cargo en el campo de texto
        frecuencia_input.value = str(mantencion['frecuencia'])      # Cargar la frecuencia en el campo de texto
        fecha_ultima_input.value = mantencion['ultima_mantencion']  # Cargar la fecha de la última mantención en el campo de texto
        notas_input.value = mantencion['notas'] # Cargar las notas en el campo de texto
        guardar_button.text = "Actualizar Mantención"   # Cambiar el texto del botón a "Actualizar Mantención"
        page.update()   # Actualizar la página

    def editar_mantencion(e):   # Función para editar una mantención
        mantencion_id = e.control.data  # Obtener el ID de la mantención desde el botón
        conexion = conectar_db()    # Conectar a la base de datos
        if conexion:    # Si la conexión es exitosa
            mantencion = obtener_mantencion_por_id(conexion, mantencion_id) # Obtener la mantención por ID
            cerrar_db(conexion)   # Cerrar la conexión a la base de datos
            if mantencion:  # Si se encontró la mantención
                cargar_datos_en_formulario(mantencion)  # Cargar los datos de la mantención en el formulario
            else:   # Si no se encontró la mantención
                page.snack_bar = ft.SnackBar(ft.Text(f"No se encontró la mantención con ID: {mantencion_id}"), open=True)   # Mostrar un mensaje de error
                page.update()   # Actualizar la página
        else:   # Si la conexión a la base de datos falló
            page.snack_bar = ft.SnackBar(ft.Text("Error al conectar a la base de datos."), open=True)   # Mostrar un mensaje de error
            page.update()   # Actualizar la página

    def eliminar_mantencion(e): # Función para eliminar una mantención
        print("Función eliminar_mantencion llamada")    # Depuración
        print("Botón eliminar presionado")  # Depuración
        mantencion_id = e.control.data  # Obtener el ID de la mantención desde el botón
        print(f"ID recibido para eliminar: {mantencion_id}")  # Depuración

        conexion = conectar_db()    # Conectar a la base de datos
        if conexion:    # Si la conexión es exitosa
            if eliminar_mantencion_db(conexion, mantencion_id): # Eliminar la mantención por ID
                print(f"Mantención con ID {mantencion_id} eliminada exitosamente.")  # Depuración
                page.snack_bar = ft.SnackBar(ft.Text(f"Mantención con ID {mantencion_id} eliminada exitosamente."), open=True)  # Mostrar un mensaje de éxito   
            else:   # Si no se pudo eliminar la mantención
                print(f"Error al eliminar la mantención con ID {mantencion_id}.")  # Depuración
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar la mantención con ID {mantencion_id}."), open=True)    # Mostrar un mensaje de error
            cerrar_db(conexion) # Cerrar la conexión a la base de datos
            cargar_mantenciones()  # Actualizar tabla
        else:   # Si la conexión a la base de datos falló
            print("Error al conectar a la base de datos.")  # Depuración
            page.snack_bar = ft.SnackBar(ft.Text("Error al conectar a la base de datos."), open=True)   # Mostrar un mensaje de error
        page.update()   # Actualizar la página

    # Función para guardar una nueva mantención o actualizar una existente
    def guardar(e): # Función para guardar una mantención
        nonlocal editando_id    # Obtener el ID de la mantención que se está editando
        nombre_empresa = nombre_empresa_input.value # Obtener el nombre de la empresa desde el campo de texto
        administrador = administrador_input.value   # Obtener el administrador solicitante desde el campo de texto
        tecnico = tecnico_input.value   # Obtener el técnico a cargo desde el campo de texto
        try:    # Intentar convertir la frecuencia a un número entero
            frecuencia = int(frecuencia_input.value)    # Obtener la frecuencia desde el campo de texto
        except ValueError:  # Si la conversión falla
            page.snack_bar = ft.SnackBar(ft.Text("La frecuencia debe ser un número entero."), open=True)    # Mostrar un mensaje de error
            page.update()   # Actualizar la página
            return  # Salir de la función
        fecha_ultima = fecha_ultima_input.value # Obtener la fecha de la última mantención desde el campo de texto
        notas = notas_input.value   # Obtener las notas desde el campo de texto

        conexion = conectar_db()    # Conectar a la base de datos
        if conexion:    # Si la conexión es exitosa
            if editando_id:   # Si se está editando una mantención existente
                # Actualizar mantención existente
                if actualizar_mantencion_db(    # Actualizar la mantención en la base de datos
                    conexion,   # Obtener la conexión a la base de datos
                    editando_id,    # ID de la mantención a editar
                    nombre_empresa, # Nombre de la empresa
                    administrador,  # Administrador solicitante
                    tecnico,    # Técnico a cargo
                    frecuencia,   # Frecuencia en meses
                    fecha_ultima,   # Fecha de la última mantención
                    notas,  # Notas
                ):   # Si la actualización fue exitosa
                    page.snack_bar = ft.SnackBar(ft.Text(f"Mantención con ID {editando_id} actualizada exitosamente."), open=True)  # Mostrar un mensaje de éxito
                else:   # Si la actualización falló 
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar la mantención con ID {editando_id}."), open=True)    # Mostrar un mensaje de error
                guardar_button.text = "Guardar Mantención"  # Cambiar el texto del botón a "Guardar Mantención" 
                editando_id = None  # Reiniciar el ID de edición
            else:   # Si no se está editando una mantención existente
                # Guardar nueva mantención
                if guardar_mantencion(  # Guardar la nueva mantención en la base de datos
                    conexion,   # Obtener la conexión a la base de datos
                    nombre_empresa, 
                    administrador,
                    tecnico,
                    frecuencia,
                    fecha_ultima,
                    notas,
                ):
                    page.snack_bar = ft.SnackBar(ft.Text("Mantención guardada exitosamente."), open=True)   # Mostrar un mensaje de éxito
                else:   # Si la guardado falló
                    page.snack_bar = ft.SnackBar(ft.Text("Error al guardar la mantención."), open=True)   # Mostrar un mensaje de error
            cerrar_db(conexion) # Cerrar la conexión a la base de datos
            limpiar_formulario()    # Limpiar el formulario
            cargar_mantenciones()   # Actualizar la tabla de mantenciones
            page.update()   # Actualizar la página
        else:   # Si la conexión a la base de datos falló
            page.snack_bar = ft.SnackBar(ft.Text("Error al conectar a la base de datos MySQL."), open=True)   # Mostrar un mensaje de error
            page.update()   # Actualizar la página

    # Botón para guardar/actualizar la mantención
    guardar_button = ft.ElevatedButton(text="Guardar Mantención", on_click=guardar) # Crear un botón para guardar la mantención

    # Función para cargar las mantenciones desde la base de datos
    def cargar_mantenciones():  # Cargar las mantenciones desde la base de datos
        nonlocal anio_actual, mes_actual, calendario_widget, tabla_mantenciones_container, mes_anio_text    # Obtener el año y mes actual
        conexion = conectar_db()    # Conectar a la base de datos
        if conexion:    # Si la conexión es exitosa
            mantenciones_db = obtener_mantenciones(conexion)    # Obtener las mantenciones desde la base de datos
            cerrar_db(conexion)   # Cerrar la conexión a la base de datos
            mantenciones_programadas = []   # Lista para almacenar las mantenciones programadas
            if mantenciones_db: # Si hay mantenciones en la base de datos
                for mantencion in mantenciones_db:  # Iterar sobre las mantenciones
                    ultima_mantencion_db = mantencion[5]  # Obtener la fecha de la última mantención
                    ultima_mantencion_str = ultima_mantencion_db.strftime("%Y-%m-%d") if ultima_mantencion_db else None # Convertir la fecha a una cadena
                    frecuencia = mantencion[4]  # Obtener la frecuencia en meses
                    fechas_tentativas = calcular_fechas_tentativas(ultima_mantencion_str, frecuencia)   # Calcular las fechas tentativas de mantenciones futuras
                    mantenciones_programadas.append({   # Agregar la mantención a la lista de mantenciones programadas
                        'id': mantencion[0],    
                        'empresa': mantencion[1],
                        'administrador': mantencion[2],
                        'tecnico': mantencion[3],
                        'frecuencia': frecuencia,
                        'ultima_mantencion': ultima_mantencion_str,
                        'fechas_tentativas': fechas_tentativas,
                        'notas': mantencion[6]
                    })
            calendario_widget.actualizar(anio_actual, mes_actual, mantenciones_programadas) # Actualizar el calendario con las mantenciones programadas
            mes_anio_text.value = f"{calendar.month_name[mes_actual]} {anio_actual}"    # Actualizar el texto del mes y año
            mes_anio_row = mes_anio_text.parent # Obtener el contenedor padre del texto del mes y año
            if mes_anio_row:    # Si el contenedor padre existe
                mes_anio_row.update()   # Actualizar el contenedor padre
            else:   # Si el contenedor padre no existe
                page.update()   # Actualizar la página

            # Crear o actualizar la tabla de mantenciones
            nueva_tabla = cargar_y_mostrar_mantenciones_tabla(page) # Cargar y mostrar la tabla de mantenciones
            tabla_mantenciones_container.content = nueva_tabla  # Actualizar el contenido del contenedor de la tabla
            tabla_mantenciones_container.update()   # Actualizar el contenedor de la tabla

        else:   # Si la conexión a la base de datos falló
            page.snack_bar = ft.SnackBar(ft.Text("Error al conectar a la base de datos MySQL."), open=True)   # Mostrar un mensaje de error
            page.update()   # Actualizar la página

    # Llamar a cargar_mantenciones al inicio para que se cargue el calendario y la tabla
    page.on_load = cargar_mantenciones  # Cargar las mantenciones al cargar la página

    # Función para cargar y mostrar las mantenciones en la tabla
    def cargar_y_mostrar_mantenciones_tabla(page: ft.Page): # Cargar y mostrar las mantenciones en la tabla
        conexion = conectar_db()    # Conectar a la base de datos
        if conexion:    # Si la conexión es exitosa
            mantenciones_db = obtener_mantenciones(conexion)    # Obtener las mantenciones desde la base de datos
            cerrar_db(conexion)  # Cerrar la conexión a la base de datos

            if mantenciones_db: # Si hay mantenciones en la base de datos
                # Definir las columnas de la tabla
                columnas = [    # Definir las columnas de la tabla
                    {"label": "ID"},    
                    {"label": "Empresa"},
                    {"label": "Admin."},
                    {"label": "Técnico"},
                    {"label": "Frecuencia (meses)"},
                    {"label": "Última Mantención"},
                    {"label": "Notas"}, 
                    {"label": "Acciones"}  # Columna para acciones (editar, eliminar)
                ]   
                # Crear las filas de la tabla
                filas = []  # Lista para almacenar las filas de la tabla
                for mantencion in mantenciones_db:  # Iterar sobre las mantenciones
                    fila = ft.DataRow(  # Crear una fila de datos
                        cells=[ # Crear las celdas de la fila
                            ft.DataCell(ft.Text(str(mantencion[0]))),  # ID
                            ft.DataCell(ft.Text(mantencion[1])),  # Empresa
                            ft.DataCell(ft.Text(mantencion[2])),  # Administrador
                            ft.DataCell(ft.Text(mantencion[3])),  # Técnico
                            ft.DataCell(ft.Text(str(mantencion[4]))),  # Frecuencia
                            ft.DataCell(ft.Text(str(mantencion[5]))),  # Última Mantención
                            ft.DataCell(ft.Text(mantencion[6])),  # Notas
                            ft.DataCell(    # Acciones
                                ft.Row(   # Crear una fila para las acciones
                                    [
                                        ft.IconButton(ft.Icons.EDIT, tooltip="Editar", data=mantencion[0], on_click=editar_mantencion), # Botón para editar
                                        ft.IconButton(ft.Icons.DELETE, tooltip="Eliminar", data=mantencion[0], on_click=eliminar_mantencion),   # Botón para eliminar
                                    ],  
                                    alignment=ft.MainAxisAlignment.END  # Alinear las acciones a la derecha
                                )   
                            ),
                        ]
                    )
                    filas.append(fila)  # Agregar la fila a la lista de filas
                # Crear la tabla de datos
                tabla_mantenciones = ft.DataTable(  # Crear la tabla de datos
                    columns=[ft.DataColumn(ft.Text(col["label"])) for col in columnas],     # Crear las columnas de la tabla
                    rows=filas, # Agregar las filas a la tabla
                    column_spacing=20,  # Espaciado entre columnas
                    horizontal_lines=ft.BorderSide(1, ft.colors.BLACK12),   # Líneas horizontales
                )   
                return tabla_mantenciones   # Devolver la tabla de mantenciones
            else:   # Si no hay mantenciones registradas
                return ft.Text("No hay mantenciones registradas.", italic=True) # Mostrar un mensaje indicando que no hay mantenciones
        else:   # Si la conexión a la base de datos falló
            return ft.Text("Error al conectar a la base de datos para cargar las mantenciones.", color=ft.colors.RED)   # Mostrar un mensaje de error

    # Función para calcular las fechas tentativas de mantenciones futuras
    def calcular_fechas_tentativas(ultima_mantencion_str, frecuencia_meses):    # Calcular las fechas tentativas de mantenciones futuras
        try:    # Intentar convertir la fecha de la última mantención a un objeto de fecha
            ultima_mantencion = datetime.datetime.strptime(ultima_mantencion_str, "%Y-%m-%d").date()    # Convertir la cadena a un objeto de fecha
            frecuencia = int(frecuencia_meses)  # Convertir la frecuencia a un número entero
            fechas_tentativas = []  # Lista para almacenar las fechas tentativas
            fecha_actual = ultima_mantencion    # Inicializar la fecha actual con la última mantención

            # Generar fechas tentativas mientras la fecha calculada sea razonablemente futura
            # Puedes ajustar la condición del while según tus necesidades.
            # Aquí, generaremos fechas por un año a partir de la última mantención como ejemplo.
            fecha_limite = ultima_mantencion + datetime.timedelta(days=365) # Establecer una fecha límite para evitar un bucle infinito

            while fecha_actual <= fecha_limite:     # Mientras la fecha actual sea menor o igual a la fecha límite
                mes = fecha_actual.month + frecuencia   # Sumar la frecuencia a la fecha actual
                anio_incremento = (mes - 1) // 12   # Calcular el incremento de año
                mes_nuevo = (mes - 1) % 12 + 1  # Calcular el nuevo mes
                fecha_actual = fecha_actual.replace(year=fecha_actual.year + anio_incremento, month=mes_nuevo)  # Reemplazar la fecha actual con el nuevo año y mes

                # Ajustar la fecha si cae en fin de semana
                fecha_ajustada = fecha_actual   # Inicializar la fecha ajustada
                while fecha_ajustada.weekday() >= 5:    # Si la fecha ajustada es sábado o domingo
                    fecha_ajustada += datetime.timedelta(days=1)    # Ajustar al siguiente día hábil

                if fecha_ajustada not in fechas_tentativas and fecha_ajustada > ultima_mantencion:  # Si la fecha ajustada no está en la lista y es mayor que la última mantención
                    fechas_tentativas.append(fecha_ajustada.strftime("%Y-%m-%d"))   # Agregar la fecha ajustada a la lista de fechas tentativas

                # Establecer una fecha límite para evitar un bucle infinito por error
                if len(fechas_tentativas) > 100: # Si se generan demasiadas fechas, salir del bucle 
                    break           

            return fechas_tentativas    # Devolver las fechas tentativas
        except ValueError:  # Si hay un error al procesar la fecha o la frecuencia
            print("Error al procesar la fecha o la frecuencia.")    # Depuración
            return []   # Devolver una lista vacía si hay un error

    # --- Crear el contenedor principal y agregar los controles ---
    contenedor_principal = ft.Column(   # Crear un contenedor principal
        expand=True,    # Expandir el contenedor
        scroll=ft.ScrollMode.AUTO,  # Habilitar el desplazamiento automático
        spacing=20, # Espaciado entre controles
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH, # Alinear los controles horizontalmente
    )

    # Agregar controles al contenedor principal
    contenedor_principal.controls.append(ft.Text("Calendario Mantenciones", style=ft.TextThemeStyle.HEADLINE_SMALL))    # Título del calendario
    contenedor_principal.controls.append(   ## Crear el calendario
        ft.Row( ## Crear una fila para los controles del calendario
            controls=[boton_anterior, mes_anio_text, boton_siguiente],  # Agregar los controles del calendario
            alignment=ft.MainAxisAlignment.CENTER   # Alinear los controles al centro
        )
    )

    contenedor_principal.controls.append(calendario_widget) # Agregar el widget del calendario al contenedor principal
    contenedor_principal.controls.append(ft.Divider())  # Separador entre el calendario y el formulario de mantenciones
    contenedor_principal.controls.append(ft.Text("Agregar/Editar Mantención", style=ft.TextThemeStyle.HEADLINE_SMALL))  # Título del formulario de mantenciones
    contenedor_principal.controls.append(nombre_empresa_input)  # Campo de texto para el nombre de la empresa
    contenedor_principal.controls.append(administrador_input)   # Campo de texto para el administrador solicitante
    contenedor_principal.controls.append(tecnico_input) # Campo de texto para el técnico a cargo
    contenedor_principal.controls.append(ft.Row([frecuencia_input, fecha_ultima_input], alignment=ft.MainAxisAlignment.START,)) # Fila para la frecuencia y fecha de la última mantención
    contenedor_principal.controls.append(notas_input)   # Campo de texto para notas
    contenedor_principal.controls.append(ft.Row([guardar_button], alignment=ft.MainAxisAlignment.CENTER))   # Botón para guardar la mantención
    contenedor_principal.controls.append(ft.Divider())  # Separador entre el formulario de mantenciones y la tabla de mantenciones
    contenedor_principal.controls.append(ft.Text("Mantenciones Registradas", style=ft.TextThemeStyle.HEADLINE_SMALL))   # Título de la tabla de mantenciones
    tabla_mantenciones_container.min_height = 300   # Altura mínima del contenedor de la tabla
    tabla_mantenciones_container.max_height = 500   # Altura máxima del contenedor de la tabla
    tabla_mantenciones_container.scroll = ft.ScrollMode.AUTO    # Habilitar el desplazamiento automático
    tabla_mantenciones_container.content = ft.Text("Cargando mantenciones...")  # Mensaje de carga inicial
    tabla_mantenciones_container.border = ft.border.all(1, ft.colors.OUTLINE)   # Borde del contenedor de la tabla
    tabla_mantenciones_container.border_radius = ft.border_radius.all(5)    # Radio del borde del contenedor de la tabla
    tabla_mantenciones_container.padding = ft.padding.all(5)    # Relleno del contenedor de la tabla
    contenedor_principal.controls.append(tabla_mantenciones_container)  # Agregar el contenedor de la tabla al contenedor principal

    # --- Crear la vista y agregar el contenedor principal ---
    view = ft.View(   # Crear la vista principal
        "/",    # Ruta de la vista
        controls=[contenedor_principal],    # Agregar el contenedor principal a la vista
        padding=ft.padding.all(10), # Relleno de la vista
        vertical_alignment=ft.MainAxisAlignment.START,  # Alinear el contenido verticalmente al inicio
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH, # Alinear el contenido horizontalmente
    )

    # Agregar la vista a la página
    page.views.append(view) # Agregar la vista a la página
    page.go("/")    # Navegar a la vista principal

    # Cargar las mantenciones al inicio
    cargar_mantenciones()   

    # Punto de entrada de la aplicación
if __name__ == "__main__":
    ft.app(target=main)
