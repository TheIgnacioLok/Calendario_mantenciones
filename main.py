import flet as ft
from database import crear_base_de_datos, crear_tabla_mantenciones, conectar_db, cerrar_db, guardar_mantencion, obtener_mantenciones
import datetime
import calendar

# Clase personalizada para generar un calendario con mantenciones programadas
class CalendarioMantenciones(ft.Column):
    def __init__(self, anio, mes, mantenciones_programadas, ancho_celda, alto_encabezado, **kwargs):
        # Inicialización de la clase con parámetros como año, mes y mantenciones
        super().__init__(horizontal_alignment=ft.CrossAxisAlignment.STRETCH, **kwargs)
        self.anio = anio
        self.mes = mes
        self.mantenciones_programadas = mantenciones_programadas
        self.ancho_celda = ancho_celda
        self.alto_encabezado = alto_encabezado
        self.controls = self._crear_controles()

    # Método para crear el calendario mensual con mantenciones
    def crear_calendario_mensual(self, year, month, mantenciones_programadas):
        # Obtener el primer día de la semana y el número de días del mes
        first_day_weekday, num_days = calendar.monthrange(year, month)
        primer_dia_ajustado = (first_day_weekday - calendar.MONDAY) % 7
        dias_del_mes = []
        hoy = datetime.date.today()
        # Agregar contenedores vacíos al inicio del mes
        for _ in range(primer_dia_ajustado):
            dias_del_mes.append(ft.Container(width=self.ancho_celda, height=70))
        # Agregar los días del mes
        for day in range(1, num_days + 1):
            fecha_actual = datetime.date(year, month, day)
            es_hoy = (fecha_actual == hoy)
            mantenciones_hoy = []
            for mantencion in mantenciones_programadas:
                for fecha_tentativa in mantencion['fechas_tentativas']:
                    # Convertir fecha_tentativa a datetime.date para la comparación
                    fecha_tentativa_date = datetime.datetime.strptime(fecha_tentativa, "%Y-%m-%d").date()
                    if fecha_actual == fecha_tentativa_date:
                        mantenciones_hoy.append(mantencion)
                        break
            day_number = ft.Text(str(day), size=16)
            content_children = [ft.Container(content=day_number, alignment=ft.alignment.center)]
            tooltip_content = []
            company_names = []
            tiene_mantencion = False
            if mantenciones_hoy:
                tiene_mantencion = True
                company_names_widgets = []
                for mantencion in mantenciones_hoy:
                    tooltip_content.append(f"Empresa: {mantencion['empresa']}\nNotas: {mantencion.get('notas', '')}")
                    company_names_widgets.append(
                        ft.Text(mantencion['empresa'], size=10, selectable=True, text_align=ft.TextAlign.CENTER),
                    )
                content_children.extend(company_names_widgets)

            day_content = ft.Column(
                controls=content_children,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            )

            indicator = None
            if tiene_mantencion:
                indicator = ft.Container(
                    width=8,
                    height=8,
                    bgcolor=ft.colors.RED,
                    border_radius=4,
                    alignment=ft.alignment.bottom_right
                )
            day_container = ft.Container(
                content=ft.Stack(
                    [
                        day_content,
                        indicator if indicator else ft.Container()
                    ],
                    expand=True
                ),
                width=self.ancho_celda,
                height=70,
                alignment=ft.alignment.top_center,
                bgcolor=ft.Colors.BLUE_GREY_100 if es_hoy else ft.Colors.TRANSPARENT,
                border=ft.border.all(1, ft.Colors.BLACK12) if es_hoy else None,
                border_radius=ft.border_radius.all(5) if es_hoy else None,
                tooltip="\n\n".join(tooltip_content) if tooltip_content else None
            )
            dias_del_mes.append(day_container)
        # Agregar contenedores vacíos al final del mes si es necesario
        while len(dias_del_mes) % 7 != 0:
            dias_del_mes.append(ft.Container(width=self.ancho_celda, height=70))
        semanas = [dias_del_mes[i:i + 7] for i in range(0, len(dias_del_mes), 7)]
        return semanas

    # Método para crear los controles del calendario
    def _crear_controles(self):
        controles = []
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        # Crear encabezados para los días de la semana
        encabezados_semana = [
            ft.Container(
                ft.Text(dia, weight=ft.FontWeight.BOLD, size=12),
                alignment=ft.alignment.center,
                width=self.ancho_celda,
                height=self.alto_encabezado
            )
            for dia in dias_semana
        ]
        fila_encabezados = ft.Row(controls=encabezados_semana, alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        controles.append(fila_encabezados)
        semanas = self.crear_calendario_mensual(self.anio, self.mes, self.mantenciones_programadas)
        for semana in semanas:
            # Asegurarse de que cada semana tenga 7 elementos
            while len(semana) < 7:
                semana.append(ft.Container(width=self.ancho_celda, height=70))
            controles.append(ft.Row(controls=semana, alignment=ft.MainAxisAlignment.SPACE_AROUND))
        return controles

    # Método para actualizar el calendario con nuevos datos
    def actualizar(self, anio, mes, mantenciones_programadas):
        self.anio = anio
        self.mes = mes
        self.mantenciones_programadas = mantenciones_programadas
        self.controls = self._crear_controles()
        self.update()

# Función principal de la aplicación

def main(page: ft.Page):
    # Crear la base de datos y la tabla al iniciar la aplicación
    crear_base_de_datos()
    crear_tabla_mantenciones()

    # Configuración inicial de la página
    page.title = "Gestión de Mantenciones"
    #page.padding = ft.padding.all(10)
    hoy = datetime.date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    # --- Definición de Controles de Entrada ---
    nombre_empresa_input = ft.TextField(label="Nombre de la Empresa")
    administrador_input = ft.TextField(label="Administrador Solicitante")
    tecnico_input = ft.TextField(label="Técnico a Cargo")
    frecuencia_input = ft.TextField(label="Frecuencia (en meses)", keyboard_type=ft.KeyboardType.NUMBER)
    fecha_ultima_input = ft.TextField(label="Fecha Última Mantención (YYYY-MM-DD)")
    notas_input = ft.TextField(label="Notas", multiline=True)
    # --- Definición de Widgets del Calendario y Tabla ---
    ancho_celda = 100
    alto_encabezado = 30

    calendario_widget = CalendarioMantenciones(anio_actual, mes_actual, [], ancho_celda, alto_encabezado)
    mes_anio_text = ft.Text(f"{calendar.month_name[mes_actual]} {anio_actual}", weight=ft.FontWeight.BOLD)

    # Contenedor para la tabla de mantenciones (inicialmente vacío)
    tabla_mantenciones_container = ft.Container()

    # Función para navegar entre meses en el calendario
    def navegar_mes(direccion):
        nonlocal mes_actual, anio_actual
        if direccion == -1:
            mes_actual -= 1
            if mes_actual < 1:
                mes_actual = 12
                anio_actual -= 1
        elif direccion == 1:
            mes_actual += 1
            if mes_actual > 12:
                mes_actual = 1
                anio_actual += 1
        cargar_mantenciones()

    # Botones para navegar entre meses
    boton_anterior = ft.IconButton(ft.Icons.ARROW_LEFT, on_click=lambda _: navegar_mes(-1))
    boton_siguiente = ft.IconButton(ft.Icons.ARROW_RIGHT, on_click=lambda _: navegar_mes(1))

    # Función para guardar una nueva mantención en la base de datos
    def guardar(e):
        nombre_empresa = nombre_empresa_input.value
        administrador = administrador_input.value
        tecnico = tecnico_input.value
        try:
            frecuencia = int(frecuencia_input.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("La frecuencia debe ser un número entero."), open=True)
            page.update()
            return
        fecha_ultima = fecha_ultima_input.value
        notas = notas_input.value

        conexion = conectar_db()
        if conexion:
            if guardar_mantencion(
                conexion,
                nombre_empresa,
                administrador,
                tecnico,
                frecuencia,
                fecha_ultima,
                notas,
            ):
                page.snack_bar = ft.SnackBar(ft.Text("Mantención guardada exitosamente."), open=True)
                # Recargamos las mantenciones y el calendario después de guardar
                # Limpiar los campos después de guardar
                nombre_empresa_input.value = ""
                administrador_input.value = ""
                tecnico_input.value = ""
                frecuencia_input.value = ""
                fecha_ultima_input.value = ""
                notas_input.value = ""
                page.update()
                cargar_mantenciones()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al guardar la mantención."), open=True)
            cerrar_db(conexion)
            page.update()

    # Botón para guardar la mantención (DEFINICIÓN MOVIDA AQUÍ)
    guardar_button = ft.ElevatedButton(text="Guardar Mantención", on_click=guardar)

    # Función para cargar las mantenciones desde la base de datos
    def cargar_mantenciones():
        nonlocal anio_actual, mes_actual, calendario_widget, tabla_mantenciones_container, mes_anio_text
        conexion = conectar_db()
        if conexion:
            mantenciones_db = obtener_mantenciones(conexion)
            cerrar_db(conexion)
            mantenciones_programadas = []
            if mantenciones_db:
                for mantencion in mantenciones_db:
                    ultima_mantencion_db = mantencion[5]  # Es un objeto datetime.date
                    ultima_mantencion_str = ultima_mantencion_db.strftime("%Y-%m-%d") if ultima_mantencion_db else None
                    frecuencia = mantencion[4]
                    fechas_tentativas = calcular_fechas_tentativas(ultima_mantencion_str, frecuencia)
                    mantenciones_programadas.append({
                        'id': mantencion[0],
                        'empresa': mantencion[1],
                        'frecuencia': frecuencia,
                        'ultima_mantencion': ultima_mantencion_str,
                        'fechas_tentativas': fechas_tentativas,
                        'notas': mantencion[6]
                    })
            calendario_widget.actualizar(anio_actual, mes_actual, mantenciones_programadas)
            mes_anio_text.value = f"{calendar.month_name[mes_actual]} {anio_actual}"
            mes_anio_row = mes_anio_text.parent
            if mes_anio_row:
                mes_anio_row.update()
            else:
                page.update()

            # Crear o actualizar la tabla de mantenciones
            nueva_tabla = cargar_y_mostrar_mantenciones_tabla(page)
            tabla_mantenciones_container.content = nueva_tabla
            tabla_mantenciones_container.update()

        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al conectar a la base de datos MySQL."), open=True)
            page.update()

    # Llamar a cargar_mantenciones al inicio para que se cargue el calendario y la tabla
    page.on_load = cargar_mantenciones

    page.add(
        ft.Row(controls=[boton_anterior, mes_anio_text, boton_siguiente], alignment=ft.MainAxisAlignment.CENTER),
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                nombre_empresa_input,
                administrador_input,
                tecnico_input,
                frecuencia_input,
                fecha_ultima_input,
                notas_input,
                guardar_button,  
                calendario_widget,
                ft.Divider(),
                tabla_mantenciones_container,
            ]
        )
    )

    # Botón para guardar la mantención (DEFINICIÓN ACTUAL)
    guardar_button = ft.ElevatedButton(text="Guardar Mantención", on_click=guardar)

    page.add(
        ft.Row(controls=[boton_anterior, mes_anio_text, boton_siguiente], alignment=ft.MainAxisAlignment.CENTER),
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                nombre_empresa_input,
                administrador_input,
                tecnico_input,
                frecuencia_input,
                fecha_ultima_input,
                notas_input,
                guardar_button,
                calendario_widget,
                ft.Divider(),  # Separador visual
                tabla_mantenciones_container, # Aquí se mostrará la tabla
            ]
        )
    )

    def cargar_y_mostrar_mantenciones_tabla(page: ft.Page):
        conexion = conectar_db()
        if conexion:
            mantenciones_db = obtener_mantenciones(conexion)
            cerrar_db(conexion)

            if mantenciones_db:
                # Definir las columnas de la tabla
                columnas = [
                    {"label": "ID"},
                    {"label": "Empresa"},
                    {"label": "Admin."},
                    {"label": "Técnico"},
                    {"label": "Frecuencia (meses)"},
                    {"label": "Última Mantención"},
                    {"label": "Notas"}
                ]

                filas = []
                for mantencion in mantenciones_db:
                    filas.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(mantencion[0]))),  # ID
                                ft.DataCell(ft.Text(mantencion[1])),      # Empresa
                                ft.DataCell(ft.Text(mantencion[2])),      # Administrador
                                ft.DataCell(ft.Text(mantencion[3])),      # Técnico
                                ft.DataCell(ft.Text(str(mantencion[4]))),  # Frecuencia
                                ft.DataCell(ft.Text(str(mantencion[5]))),  # Última Mantención
                                ft.DataCell(ft.Text(mantencion[6])),      # Notas
                            ]
                        )
                    )

                tabla_mantenciones = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text(col["label"])) for col in columnas],
                    rows=filas,
                    column_spacing=20,
                    horizontal_lines=ft.BorderSide(1, ft.colors.BLACK12),
                )
                return tabla_mantenciones
            else:
                return ft.Text("No hay mantenciones registradas.", italic=True)
        else:
            return ft.Text("Error al conectar a la base de datos para cargar las mantenciones.", color=ft.colors.RED)

    # Función para calcular las fechas tentativas de mantenciones futuras
    def calcular_fechas_tentativas(ultima_mantencion_str, frecuencia_meses):
        try:
            ultima_mantencion = datetime.datetime.strptime(ultima_mantencion_str, "%Y-%m-%d").date()
            frecuencia = int(frecuencia_meses)
            fechas_tentativas = []
            fecha_actual = ultima_mantencion

            # Generar fechas tentativas mientras la fecha calculada sea razonablemente futura
            # Puedes ajustar la condición del while según tus necesidades.
            # Aquí, generaremos fechas por un año a partir de la última mantención como ejemplo.
            fecha_limite = ultima_mantencion + datetime.timedelta(days=365)

            while fecha_actual <= fecha_limite:
                mes = fecha_actual.month + frecuencia
                anio_incremento = (mes - 1) // 12
                mes_nuevo = (mes - 1) % 12 + 1
                fecha_actual = fecha_actual.replace(year=fecha_actual.year + anio_incremento, month=mes_nuevo)

                # Ajustar la fecha si cae en fin de semana
                fecha_ajustada = fecha_actual
                while fecha_ajustada.weekday() >= 5:
                    fecha_ajustada += datetime.timedelta(days=1)

                if fecha_ajustada not in fechas_tentativas and fecha_ajustada > ultima_mantencion:
                    fechas_tentativas.append(fecha_ajustada.strftime("%Y-%m-%d"))

                # Establecer una fecha límite para evitar un bucle infinito por error
                if len(fechas_tentativas) > 100: # Un número grande de predicciones
                    break

            return fechas_tentativas
        except ValueError:
            print("Error al procesar la fecha o la frecuencia.")
            return []
    # 1. Crear la columna principal SCROLLABLE (igual que antes)
    contenedor_principal = ft.Column(
        expand=True,             # Sigue siendo importante para que llene el View
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        # Opcional: Controlar el ancho si es necesario, aunque suele adaptarse
        # width=800, # Podrías experimentar si el ancho causa problemas
        # horizontal_alignment=ft.CrossAxisAlignment.CENTER # Centrar si width está fijo
    )

    # 2. Añadir todos los controles a esta columna principal (igual que antes)
    contenedor_principal.controls.append(ft.Text("Calendario Mantenciones", style=ft.TextThemeStyle.HEADLINE_SMALL))
    contenedor_principal.controls.append(
        ft.Row(
            controls=[boton_anterior, mes_anio_text, boton_siguiente],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )
    
    contenedor_principal.controls.append(calendario_widget)
    contenedor_principal.controls.append(ft.Divider())
    contenedor_principal.controls.append(ft.Text("Agregar Nueva Mantención", style=ft.TextThemeStyle.HEADLINE_SMALL))
    contenedor_principal.controls.append(nombre_empresa_input)
    # ... (resto de inputs y botón de guardar)
    contenedor_principal.controls.append(ft.Row([frecuencia_input, fecha_ultima_input], alignment=ft.MainAxisAlignment.START,))
    contenedor_principal.controls.append(notas_input)
    contenedor_principal.controls.append(ft.Row([guardar_button], alignment=ft.MainAxisAlignment.CENTER))
    contenedor_principal.controls.append(ft.Divider())
    contenedor_principal.controls.append(ft.Text("Mantenciones Registradas", style=ft.TextThemeStyle.HEADLINE_SMALL))
    contenedor_principal.controls.append(tabla_mantenciones_container)


    # 3. Crear el View y poner el contenedor_principal DENTRO de él
    view = ft.View(
        "/",  # Ruta raíz para la vista (necesaria)
        controls=[contenedor_principal], # La columna scrollable es el único control del View
        padding=ft.padding.all(10), # Añade padding alrededor de todo el contenido
        # Puedes añadir otras propiedades al View si las necesitas
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # 4. Añadir el View a la página (¡ESTE ES EL CAMBIO CLAVE!)
    # En lugar de page.add(contenedor_principal), usamos:
    page.views.append(view)
    page.go("/") # Navega a la vista que acabamos de añadir

    # page.add(view) # Alternativa para apps muy simples sin routing, pero page.views es más estándar

    # 5. Cargar los datos iniciales
    # Asegúrate que la carga ocurra después de que la vista esté en la página
    # page.update() # Puede ser necesario llamar a update después de añadir la vista y antes de cargar
    cargar_mantenciones()
    # page.update() # Y/o un update final aquí si cargar_mantenciones no lo hace

# Punto de entrada de la aplicación
if __name__ == "__main__":
    ft.app(target=main)
# Punto de entrada de la aplicación
if __name__ == "__main__":
    ft.app(target=main)
