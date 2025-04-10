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
                bgcolor=ft.colors.BLUE_GREY_100 if es_hoy else ft.colors.TRANSPARENT,
                border=ft.border.all(1, ft.colors.BLACK12) if es_hoy else None,
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
    hoy = datetime.date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    nombre_empresa_input = ft.TextField(label="Nombre de la Empresa")
    administrador_input = ft.TextField(label="Administrador Solicitante")
    tecnico_input = ft.TextField(label="Técnico a Cargo")
    frecuencia_input = ft.TextField(label="Frecuencia (en meses)", keyboard_type=ft.KeyboardType.NUMBER)
    fecha_ultima_input = ft.TextField(label="Fecha Última Mantención (YYYY-MM-DD)")
    notas_input = ft.TextField(label="Notas", multiline=True)
    ancho_celda = 60
    alto_encabezado = 30
    calendario_widget = CalendarioMantenciones(anio_actual, mes_actual, [], ancho_celda, alto_encabezado)
    mes_anio_text = ft.Text(f"{calendar.month_name[mes_actual]} {anio_actual}", weight=ft.FontWeight.BOLD)
    
    # Función para cargar las mantenciones desde la base de datos
    def cargar_mantenciones():
        nonlocal anio_actual, mes_actual
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
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al conectar a la base de datos MySQL."), open=True)
            page.update()
    
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
    
    guardar_button = ft.ElevatedButton(text="Guardar Mantención", on_click=guardar)
    
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
    boton_anterior = ft.IconButton(ft.icons.ARROW_LEFT, on_click=lambda _: navegar_mes(-1))
    boton_siguiente = ft.IconButton(ft.icons.ARROW_RIGHT, on_click=lambda _: navegar_mes(1))

    # Cargamos las mantenciones y el calendario al iniciar la aplicación
    page.on_load = cargar_mantenciones
    
    # Agregar los controles a la página
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
                ]
            )
        )
# Punto de entrada de la aplicación
if __name__ == "__main__":
    ft.app(target=main)
