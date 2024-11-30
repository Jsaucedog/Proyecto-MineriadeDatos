import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from sklearn.linear_model import LinearRegression
from decimal import Decimal
import calendar
import numpy as np

def conectar_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Saucedojesg1_",
            database="MINERIADEDATOSPROYECTO"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {err}")
        return None

def configurar_treeview(parent, columnas):
    tree = ttk.Treeview(parent, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill='both', pady=10)
    return tree

def cargar_datos(tree, tabla_sql):
    for item in tree.get_children():
        tree.delete(item)

    db = conectar_db()
    if db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {tabla_sql}")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        db.close()

def ejecutar_query(query, valores=None, tree=None, tabla_sql=None):
    db = conectar_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute(query, valores)
            db.commit()
            if tree and tabla_sql:
                cargar_datos(tree, tabla_sql)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Operación fallida: {err}")
        finally:
            db.close()
def agregar_empleado_a_db(nombre, telefono):
    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO empleado (emp_nombre, emp_telefono)
            VALUES (%s, %s)
        """, (nombre, telefono))
        db.commit()
        db.close()
        return True
    except mysql.connector.IntegrityError as e:
        if "uni_telefono" in str(e):
            messagebox.showerror("Error", "El teléfono ingresado ya está registrado.")
        else:
            messagebox.showerror("Error", "Error al agregar empleado.")
        return False
    except Exception as e:
        print("Error al agregar empleado:", e)
        return False

def obtener_empleados_db():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT emp_id, emp_nombre, emp_telefono FROM empleado")
    empleados = cursor.fetchall()
    db.close()
    return empleados

def agregar_empleado_a_db(nombre, telefono):
    db = conectar_db()
    cursor = db.cursor()
    query = "INSERT INTO empleado (emp_nombre, emp_telefono) VALUES (%s, %s)"
    cursor.execute(query, (nombre, telefono))
    db.commit()
    db.close()
    return True

def eliminar_empleado_db(empleado_id):
    db = conectar_db()
    cursor = db.cursor()
    query = "DELETE FROM empleado WHERE emp_id = %s"
    cursor.execute(query, (empleado_id,))
    db.commit()
    db.close()
    return True

def crear_tab_agregar_empleado(): 
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Empleados")
    frame = ttk.Frame(tab)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    campos = {
        "Nombre": tk.Entry(frame, width=30),
        "Teléfono": tk.Entry(frame, width=30),
    }

    for label, entry in campos.items():
        ttk.Label(frame, text=label).pack(anchor="w", pady=2)
        entry.pack(pady=2)

    def guardar_empleado():
        nombre = campos["Nombre"].get().strip()
        telefono = campos["Teléfono"].get().strip()

        if not nombre or not telefono:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios.")
            return

        if not telefono.isdigit() or len(telefono) != 10:
            messagebox.showerror("Error en teléfono", "El teléfono debe ser un número de 10 dígitos.")
            return

        if agregar_empleado_a_db(nombre, telefono):
            messagebox.showinfo("Éxito", "Empleado agregado correctamente.")
            for entry in campos.values():
                entry.delete(0, tk.END)
            actualizar_tabla_empleados()

    def eliminar_empleado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Por favor, selecciona un empleado para eliminar.")
            return
        
        empleado_id = tabla.item(seleccion, "values")[0]

        if eliminar_empleado_db(empleado_id):
            messagebox.showinfo("Éxito", "Empleado eliminado correctamente.")
            actualizar_tabla_empleados()

    ttk.Button(frame, text="Agregar", command=guardar_empleado).pack(pady=10)
    ttk.Button(frame, text="Eliminar", command=eliminar_empleado).pack(pady=10)

    tabla_frame = ttk.Frame(tab)
    tabla_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    columnas = ("ID", "Nombre", "Teléfono")
    tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor="center")

    tabla.pack(fill=tk.BOTH, expand=True)

    def actualizar_tabla_empleados():
        for row in tabla.get_children():
            tabla.delete(row)

        empleados = obtener_empleados_db()
        
        for empleado in empleados:
            tabla.insert("", "end", values=empleado)

    actualizar_tabla_empleados()

def crear_tab_con_filtro_por_nombre_y_letra(tabla_sql, columnas, id_campo, nombres_campos):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tabla_sql.capitalize())
    filtro_frame = tk.Frame(tab)
    filtro_frame.pack(pady=10)

    filtro_label_letra = tk.Label(filtro_frame, text="Filtrar por letra: ")
    filtro_label_letra.pack(side=tk.LEFT, padx=5)

    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    filtro_letra = ttk.Combobox(filtro_frame, values=[""] + list(letras), width=5)
    filtro_letra.set("")
    filtro_letra.pack(side=tk.LEFT, padx=5)

    filtro_label_nombre = tk.Label(filtro_frame, text="Filtrar por nombre: ")
    filtro_label_nombre.pack(side=tk.LEFT, padx=5)

    filtro_nombre = tk.Entry(filtro_frame, width=15)
    filtro_nombre.pack(side=tk.LEFT, padx=5)

    def aplicar_filtro():
        letra = filtro_letra.get()
        nombre = filtro_nombre.get().strip()

        for item in tree.get_children():
            tree.delete(item)

        db = conectar_db()
        if db:
            cursor = db.cursor()
            try:
                if letra and nombre:
                    query = f"SELECT * FROM {tabla_sql} WHERE cli_nombre LIKE %s AND cli_nombre LIKE %s"
                    cursor.execute(query, (letra + '%', '%' + nombre + '%'))
                elif letra:
                    query = f"SELECT * FROM {tabla_sql} WHERE cli_nombre LIKE %s"
                    cursor.execute(query, (letra + '%',))
                elif nombre:
                    query = f"SELECT * FROM {tabla_sql} WHERE cli_nombre LIKE %s"
                    cursor.execute(query, ('%' + nombre + '%',))
                else:
                    cargar_datos(tree, tabla_sql)
                    return

                for row in cursor.fetchall():
                    tree.insert("", tk.END, values=row)
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo filtrar: {err}")
            finally:
                db.close()

    def borrar_filtro():
        filtro_letra.set("")
        filtro_nombre.delete(0, tk.END)
        cargar_datos(tree, tabla_sql)

    # Botones de filtro
    filtro_btn = ttk.Button(filtro_frame, text="Aplicar Filtro", command=aplicar_filtro)
    filtro_btn.pack(side=tk.LEFT, padx=5)

    borrar_btn = ttk.Button(filtro_frame, text="Borrar Filtro", command=borrar_filtro)
    borrar_btn.pack(side=tk.LEFT, padx=5)

    frm = tk.Frame(tab)
    frm.pack(pady=10)

    entradas = []
    for i, nombre in enumerate(nombres_campos):
        tk.Label(frm, text=nombre).grid(row=i, column=0, pady=5, padx=5)
        entrada = tk.Entry(frm)
        entrada.grid(row=i, column=1, pady=5, padx=5)
        entradas.append(entrada)

    tree = configurar_treeview(tab, columnas)
    cargar_datos(tree, tabla_sql)

    ttk.Button(frm, text="Agregar", command=lambda: agregar_registro(tabla_sql, entradas, tree)).grid(row=len(nombres_campos), column=0, pady=10)
    ttk.Button(frm, text="Eliminar", command=lambda: borrar_registro(tabla_sql, id_campo, tree)).grid(row=len(nombres_campos), column=2, pady=10)

    def seleccionar_registro(event):
        seleccionado = tree.focus()
        valores = tree.item(seleccionado, "values")
        if valores:
            for entrada, valor in zip(entradas, valores[1:]):
                entrada.delete(0, tk.END)
                entrada.insert(0, valor)

    tree.bind("<<TreeviewSelect>>", seleccionar_registro)


def agregar_registro(tabla_sql, entradas, tree):
    valores = [entrada.get() for entrada in entradas]
    placeholders = ", ".join(["%s"] * len(valores))
    query = f"INSERT INTO {tabla_sql} VALUES (NULL, {placeholders})"
    ejecutar_query(query, valores, tree, tabla_sql)

def modificar_registro(tabla_sql, entradas, id_campo, tree):
    valores = [entrada.get() for entrada in entradas]
    item_id = tree.item(tree.selection())['values'][0]
    set_clause = ", ".join([f"{col} = %s" for col in valores])
    query = f"UPDATE {tabla_sql} SET {set_clause} WHERE {id_campo} = %s"
    ejecutar_query(query, valores + [item_id], tree, tabla_sql)

def borrar_registro(tabla_sql, id_campo, tree):
    item_id = tree.item(tree.selection())['values'][0]
    query = f"DELETE FROM {tabla_sql} WHERE {id_campo} = %s"
    ejecutar_query(query, (item_id,), tree, tabla_sql)

def crear_tab_con_filtro_por_mes_y_cliente(tabla_sql, columnas, id_campo, nombres_campos):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tabla_sql.capitalize())
    
    # Frame para filtros
    filtro_frame = tk.Frame(tab)
    filtro_frame.pack(pady=10)

    # Filtro por mes
    filtro_label = tk.Label(filtro_frame, text="Filtrar por mes: ")
    filtro_label.pack(side=tk.LEFT, padx=5)
    meses = [calendar.month_name[i] for i in range(1, 13)]
    filtro_mes = ttk.Combobox(filtro_frame, values=meses, width=10)
    filtro_mes.set("")
    filtro_mes.pack(side=tk.LEFT, padx=5)

    # Filtro por cliente
    cliente_label = tk.Label(filtro_frame, text="Filtrar por cliente: ")
    cliente_label.pack(side=tk.LEFT, padx=5)
    filtro_cliente = tk.Entry(filtro_frame, width=20)
    filtro_cliente.pack(side=tk.LEFT, padx=5)

    def aplicar_filtro():
        mes = filtro_mes.get()
        cliente = filtro_cliente.get()
        if mes or cliente:
            filtrar_por_mes_y_cliente(tree, tabla_sql, mes, cliente)
        else:
            cargar_datos(tree, tabla_sql)

    def borrar_filtro():
        filtro_mes.set("")
        filtro_cliente.delete(0, tk.END)
        cargar_datos(tree, tabla_sql)

    filtro_btn = ttk.Button(filtro_frame, text="Aplicar Filtro", command=aplicar_filtro)
    filtro_btn.pack(side=tk.LEFT, padx=5)
    borrar_filtro_btn = ttk.Button(filtro_frame, text="Borrar Filtro", command=borrar_filtro)
    borrar_filtro_btn.pack(side=tk.LEFT, padx=5)

    # Frame para formularios y botones
    frm = tk.Frame(tab)
    frm.pack(pady=10)
    entradas = []
    for i, nombre in enumerate(nombres_campos):
        tk.Label(frm, text=nombre).grid(row=i, column=0, pady=5, padx=5)
        entrada = tk.Entry(frm)
        entrada.grid(row=i, column=1, pady=5, padx=5)
        entradas.append(entrada)

    tree = configurar_treeview(tab, columnas)
    cargar_datos(tree, tabla_sql)

    ttk.Button(frm, text="Agregar", command=lambda: agregar_registro(tabla_sql, entradas, tree)).grid(row=len(nombres_campos), column=0, pady=10)
    ttk.Button(frm, text="Eliminar", command=lambda: borrar_registro(tabla_sql, id_campo, tree)).grid(row=len(nombres_campos), column=2, pady=10)

    def seleccionar_registro(event):
        seleccionado = tree.focus()
        valores = tree.item(seleccionado, "values")
        if valores:
            for entrada, valor in zip(entradas, valores[1:]):
                entrada.delete(0, tk.END)
                entrada.insert(0, valor)

    tree.bind("<<TreeviewSelect>>", seleccionar_registro)

def filtrar_por_mes_y_cliente(tree, tabla_sql, mes, cliente):
    for item in tree.get_children():
        tree.delete(item)

    db = conectar_db()
    if db:
        cursor = db.cursor()
        try:
            mes_condicion = ""
            cliente_condicion = ""
            parametros = []

            if mes:
                mes_numero = list(calendar.month_name).index(mes)
                mes_condicion = "MONTH(e.eve_fecha) = %s"
                parametros.append(mes_numero)

            if cliente:
                cliente_condicion = "c.cli_nombre LIKE %s"
                parametros.append(f"%{cliente}%")

            # Construir la consulta dinámica según los filtros aplicados
            condiciones = " AND ".join(filter(None, [mes_condicion, cliente_condicion]))
            query = f"""
            SELECT e.eve_id, e.eve_fecha, e.eve_numero_personas, e.eve_lugar, 
                   e.eve_preciototal, e.eve_tipo, e.eve_pago, e.eve_tipodepago, 
                   c.cli_nombre
            FROM evento e
            LEFT JOIN cliente c ON e.eve_cli_id = c.cli_id
            """
            if condiciones:
                query += f" WHERE {condiciones}"

            cursor.execute(query, tuple(parametros))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo filtrar: {err}")
        finally:
            db.close()


def cargar_datos(tree, tabla_sql):
    for item in tree.get_children():
        tree.delete(item)

    db = conectar_db()
    if db:
        cursor = db.cursor()
        try:
            # Ajustar la consulta para obtener el nombre del cliente
            if tabla_sql == "evento":
                query = """
                SELECT e.eve_id, e.eve_fecha, e.eve_numero_personas, e.eve_lugar, 
                       e.eve_preciototal, e.eve_tipo, e.eve_pago, e.eve_tipodepago, 
                       c.cli_nombre  -- Seleccionamos el nombre del cliente
                FROM evento e
                LEFT JOIN cliente c ON e.eve_cli_id = c.cli_id  -- Hacemos el JOIN
                """
                cursor.execute(query)
            else:
                cursor.execute(f"SELECT * FROM {tabla_sql}")
            
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {err}")
        finally:
            db.close()

def obtener_clientes_segmentados():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            c.cli_nombre,
            DATEDIFF(CURDATE(), MAX(e.eve_fecha)) AS recency,
            COUNT(e.eve_id) AS frequency,
            SUM(e.eve_preciototal) AS monetary
        FROM cliente c
        JOIN evento e ON c.cli_id = e.eve_cli_id
        GROUP BY c.cli_id
    """)
    datos = cursor.fetchall()
    db.close()

    clientes_segmentados = []
    for nombre, recency, frequency, monetary in datos:
        if recency <= 30 and frequency >= 5 and monetary >= 1000:
            segmento = "Cliente Leal"
        elif recency <= 60 and frequency >= 3:
            segmento = "Cliente Frecuente"
        elif recency <= 90:
            segmento = "Cliente Ocasional"
        else:
            segmento = "Cliente Inactivo"

        clientes_segmentados.append((nombre, recency, frequency, monetary, segmento))

    return clientes_segmentados


def mostrar_tabla_clientes(tabla):
    datos = obtener_clientes_segmentados()
    tabla["columns"] = ("Cliente", "Recency", "Frequency", "Monetary", "Segmento")
    tabla.heading("Cliente", text="Cliente")
    tabla.heading("Recency", text="Recencia (días)")
    tabla.heading("Frequency", text="Frecuencia (compras)")
    tabla.heading("Monetary", text="Monetario ($)")
    tabla.heading("Segmento", text="Segmento")

    for cliente, recency, frequency, monetary, segmento in datos:
        tabla.insert("", "end", values=(cliente, recency, frequency, monetary, segmento))


def mostrar_grafico_clientes(frame):
    datos = obtener_clientes_segmentados()
    segmentos = [fila[4] for fila in datos]

    from collections import Counter
    conteo_segmentos = Counter(segmentos)

    segmentos = list(conteo_segmentos.keys())
    cantidades = list(conteo_segmentos.values())

    for widget in frame.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    fig, ax = plt.subplots()
    ax.bar(segmentos, cantidades, color="blue")
    ax.set_title("Distribución de Clientes por Segmento")
    ax.set_xlabel("Segmento")
    ax.set_ylabel("Cantidad de Clientes")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def obtener_top_clientes():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.cli_nombre, SUM(e.eve_preciototal) AS consumo_total
        FROM cliente c
        JOIN evento e ON c.cli_id = e.eve_cli_id
        GROUP BY c.cli_id
        ORDER BY consumo_total DESC
        LIMIT 5
    """)
    datos = cursor.fetchall()
    db.close()
    return datos


def mostrar_tabla_top_clientes(tabla):
    datos = obtener_top_clientes()
    tabla["columns"] = ("Cliente", "Consumo Total")
    tabla.heading("Cliente", text="Cliente")
    tabla.heading("Consumo Total", text="Consumo Total ($)")

    for cliente, consumo in datos:
        tabla.insert("", "end", values=(cliente, consumo))


def crear_tab_clientes_segmentados():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Segmentación de Clientes")
    frame = ttk.Frame(tab)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(frame, text="Segmentación de Clientes (RFM)", font=("Arial", 14)).pack(pady=10)

    ttk.Label(frame, text="Clasificación por Modelo RFM", font=("Arial", 12)).pack(pady=5)
    tabla_clientes_rfm = ttk.Treeview(frame, show="headings")
    tabla_clientes_rfm.pack(fill=tk.BOTH, expand=True, pady=5)

    scroll_rfm = ttk.Scrollbar(frame, orient="vertical", command=tabla_clientes_rfm.yview)
    tabla_clientes_rfm.configure(yscrollcommand=scroll_rfm.set)
    scroll_rfm.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    mostrar_tabla_clientes(tabla_clientes_rfm)

    ttk.Label(frame, text="Top 5 Clientes con Mayor Consumo", font=("Arial", 12)).pack(pady=5)
    tabla_top_clientes = ttk.Treeview(frame, show="headings")
    tabla_top_clientes.pack(fill=tk.BOTH, expand=True, pady=5)

    scroll_top = ttk.Scrollbar(frame, orient="vertical", command=tabla_top_clientes.yview)
    tabla_top_clientes.configure(yscrollcommand=scroll_top.set)
    scroll_top.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    mostrar_tabla_top_clientes(tabla_top_clientes)

    ttk.Button(frame, text="Gráfico por Segmentos", command=lambda: mostrar_grafico_clientes(frame)).pack(pady=10)

def crear_tab_ventas_por_mes():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Análisis Mensual")

    frame = ttk.Frame(tab)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(frame, text="Ventas por Mes", font=("Arial", 14)).pack(pady=10)

    tabla_ventas = ttk.Treeview(frame, columns=("Mes", "Ventas"), show="headings")
    tabla_ventas.heading("Mes", text="Mes")
    tabla_ventas.heading("Ventas", text="Total Ventas")
    tabla_ventas.pack(fill=tk.BOTH, expand=True)

    scroll_ventas = ttk.Scrollbar(frame, orient="vertical", command=tabla_ventas.yview)
    tabla_ventas.configure(yscrollcommand=scroll_ventas.set)
    scroll_ventas.pack(side=tk.RIGHT, fill=tk.Y)

    mostrar_tabla_ventas(tabla_ventas)

    ttk.Button(frame, text="Gráfico Ventas por Mes", command=lambda: mostrar_grafico_ventas(frame)).pack(pady=10)


def obtener_ventas_por_mes():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT MONTH(eve_fecha), SUM(eve_preciototal) 
        FROM evento 
        GROUP BY MONTH(eve_fecha) 
        ORDER BY MONTH(eve_fecha)
    """)
    datos = cursor.fetchall()
    db.close()
    return datos


def mostrar_tabla_ventas(tabla):
    datos = obtener_ventas_por_mes()
    for row in tabla.get_children():
        tabla.delete(row)
    for mes, total in datos:
        tabla.insert("", "end", values=(calendar.month_name[mes], total))


def mostrar_grafico_ventas(frame):
    datos = obtener_ventas_por_mes()
    meses = [calendar.month_name[fila[0]] for fila in datos]
    ventas = [fila[1] for fila in datos]

    for widget in frame.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    fig, ax = plt.subplots()
    ax.bar(meses, ventas, color="blue")
    ax.set_title("Ventas por Mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Total Ventas")
    ax.set_xticklabels(meses, rotation=45, ha="right")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def mostrar_grafico_ventas(frame):
    datos = obtener_ventas_por_mes()
    meses = [calendar.month_name[mes] for mes, _ in datos]
    totales = [total for _, total in datos]

    for widget in frame.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    ax.bar(meses, totales, color="blue")
    ax.set_title("Ventas Totales por Mes")
    ax.set_ylabel("Total Ventas")
    ax.set_xlabel("Mes")
    ax.tick_params(axis="x", rotation=0)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def crear_tab_analisis_geografico():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Análisis Geográfico")

    frame = ttk.Frame(tab)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(frame, text="Análisis Geográfico por Ubicación", font=("Arial", 14)).pack(pady=10)

    tabla_geografica = ttk.Treeview(frame, columns=("Ubicación", "Total Eventos", "Total Ingresos"), show="headings")
    tabla_geografica.heading("Ubicación", text="Ubicación")
    tabla_geografica.heading("Total Eventos", text="Número de Eventos")
    tabla_geografica.heading("Total Ingresos", text="Ingresos Totales")
    tabla_geografica.pack(fill=tk.BOTH, expand=True)

    scroll_geografico = ttk.Scrollbar(frame, orient="vertical", command=tabla_geografica.yview)
    tabla_geografica.configure(yscrollcommand=scroll_geografico.set)
    scroll_geografico.pack(side=tk.RIGHT, fill=tk.Y)

    mostrar_tabla_geografica(tabla_geografica)

    ttk.Button(frame, text="Gráfico Análisis Geográfico",
               command=lambda: mostrar_grafico_geografico(frame)).pack(pady=10)

def obtener_datos_geograficos():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.eve_lugar AS ubicacion, COUNT(e.eve_id) AS total_eventos, SUM(e.eve_preciototal) AS total_ingresos
        FROM evento e
        GROUP BY e.eve_lugar
        ORDER BY total_ingresos DESC
        LIMIT 5
    """)
    datos = cursor.fetchall()
    db.close()
    return datos

def mostrar_tabla_geografica(tabla):
    datos = obtener_datos_geograficos()
    for ubicacion, total_eventos, total_ingresos in datos:
        tabla.insert("", "end", values=(ubicacion, total_eventos, total_ingresos))

def mostrar_grafico_geografico(frame):
    datos = obtener_datos_geograficos()
    ubicaciones = [fila[0] for fila in datos]
    ingresos = [fila[2] for fila in datos]

    for widget in frame.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    fig, ax = plt.subplots()
    ax.barh(ubicaciones, ingresos, color="blue")
    ax.set_title("Ingresos Totales por Ubicación")
    ax.set_xlabel("Ingresos Totales")
    ax.set_ylabel("Ubicación")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def obtener_datos_historicos():
    try:
        db = conectar_db()
        if db is None:
            return pd.DataFrame(columns=["mes", "anio", "eventos"])

        with db.cursor() as cursor:
            cursor.execute("""
                SELECT MONTH(eve_fecha) AS mes, YEAR(eve_fecha) AS anio, COUNT(eve_id) AS eventos
                FROM evento
                GROUP BY anio, mes
                ORDER BY anio, mes
            """)
            datos = cursor.fetchall()
        return pd.DataFrame(datos, columns=["mes", "anio", "eventos"])
    except Exception as e:
        return pd.DataFrame(columns=["mes", "anio", "eventos"])


def predecir_demanda_regresion():
    datos = obtener_datos_historicos()
    if datos.empty:
        return pd.DataFrame()

    datos["fecha"] = pd.to_datetime(dict(year=datos["anio"], month=datos["mes"], day=1))
    datos = datos.sort_values("fecha")
    datos["indice"] = range(len(datos))

    modelo = LinearRegression()
    X = datos[["indice"]].values
    y = datos["eventos"].values
    modelo.fit(X, y)

    ult_indice = datos["indice"].iloc[-1]
    futuros_indices = np.arange(ult_indice + 1, ult_indice + 13).reshape(-1, 1)
    predicciones = modelo.predict(futuros_indices)

    fechas_futuras = pd.date_range(start=datos["fecha"].iloc[-1] + pd.offsets.MonthBegin(1), periods=12, freq="MS")
    futuro_df = pd.DataFrame({
        "fecha": fechas_futuras,
        "anio": fechas_futuras.year,
        "mes": fechas_futuras.month,
        "prediccion": predicciones
    })

    return futuro_df

def mostrar_tabla_prediccion(tabla):
    datos_historicos = obtener_datos_historicos()
    datos_prediccion = predecir_demanda_regresion()

    if datos_historicos.empty and datos_prediccion.empty:
        tabla.insert("", "end", values=("Sin datos", "Sin datos", "Sin datos"))
        return

    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", 
             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    for _, fila in datos_historicos.iterrows():
        mes_nombre = meses[int(fila["mes"]) - 1]
        tabla.insert("", "end", values=(mes_nombre, int(fila["anio"]), int(fila["eventos"])))

    for _, fila in datos_prediccion.iterrows():
        mes_nombre = meses[int(fila["mes"]) - 1]
        tabla.insert("", "end", values=(mes_nombre, int(fila["anio"]), round(fila["prediccion"])))


def mostrar_grafico_prediccion(frame, grafico_frame):
    datos_historicos = obtener_datos_historicos()
    datos_prediccion = predecir_demanda_regresion()

    if datos_historicos.empty and datos_prediccion.empty:
        return

    for widget in grafico_frame.winfo_children():
        widget.destroy()

    datos_historicos["tipo"] = "Histórico"
    datos_prediccion["tipo"] = "Predicción"
    datos_prediccion.rename(columns={"prediccion": "eventos"}, inplace=True)
    datos = pd.concat([datos_historicos, datos_prediccion], ignore_index=True)

    datos["fecha"] = pd.to_datetime(dict(year=datos["anio"], month=datos["mes"], day=1))
    datos.set_index("fecha", inplace=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    historicos = datos[datos["tipo"] == "Histórico"]
    predicciones = datos[datos["tipo"] == "Predicción"]

    ax.plot(historicos.index, historicos["eventos"], label="Histórico", marker="o")
    ax.plot(predicciones.index, predicciones["eventos"], label="Predicción", linestyle="--", color="orange")
    ax.set_title("Predicción de Demanda Mensual")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Eventos")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=grafico_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def crear_tab_prediccion_demanda(notebook):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Predicción de Demanda")

    frame = ttk.Frame(tab)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(frame, text="Predicción de Demanda Mensual", font=("Arial", 14)).pack(pady=10)

    tabla_prediccion = ttk.Treeview(frame, columns=("Mes", "Año", "Eventos"), show="headings")
    for col in ["Mes", "Año", "Eventos"]:
        tabla_prediccion.heading(col, text=col)
    tabla_prediccion.pack(fill=tk.BOTH, expand=True)

    scroll_prediccion = ttk.Scrollbar(frame, orient="vertical", command=tabla_prediccion.yview)
    tabla_prediccion.configure(yscrollcommand=scroll_prediccion.set)
    scroll_prediccion.pack(side=tk.RIGHT, fill=tk.Y)

    mostrar_tabla_prediccion(tabla_prediccion)

    grafico_frame = ttk.Frame(frame)
    grafico_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    ttk.Button(frame, text="Gráfico de Predicción", command=lambda: mostrar_grafico_prediccion(frame, grafico_frame)).pack(pady=10)


MESES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
         7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

def obtener_estadisticas_eventos():
    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            MONTH(eve_fecha) AS mes,
            AVG(eve_numero_personas) AS media,
            STD(eve_numero_personas) AS desviacion,
            MIN(eve_numero_personas) AS minimo,
            MAX(eve_numero_personas) AS maximo,
            COUNT(eve_id) AS num_eventos,
            VARIANCE(eve_numero_personas) AS varianza
        FROM evento
        GROUP BY mes
        ORDER BY mes
    """)
    datos_basicos = cursor.fetchall()

    datos_completos = []
    for mes, media, desviacion, minimo, maximo, num_eventos, varianza in datos_basicos:
        cursor.execute(f"""
            SELECT eve_numero_personas
            FROM evento
            WHERE MONTH(eve_fecha) = {mes}
            ORDER BY eve_numero_personas
        """)
        valores = [fila[0] for fila in cursor.fetchall()]

        n = len(valores)
        mediana = (valores[n // 2] + valores[(n - 1) // 2]) / 2 if n % 2 == 0 else valores[n // 2]
        moda = max(set(valores), key=valores.count)

        limite_inferior = Decimal(media) - Decimal(1.96) * Decimal(desviacion)
        limite_superior = Decimal(media) + Decimal(1.96) * Decimal(desviacion)
        datos_completos.append((mes, media, mediana, moda, varianza, desviacion, minimo, maximo, limite_inferior, limite_superior, num_eventos))

    db.close()
    return datos_completos

def crear_tabla_estadisticas(parent):
    tabla = ttk.Treeview(
        parent,
        columns=("Mes", "Media", "Mediana", "Moda", "Varianza", "Desv.Estd", "Mínimo", "Máximo", "Límite Inf", "Límite Sup", "Eventos"),
        show="headings"
    )

    encabezados = [
        ("Mes", "Mes"),
        ("Media", "Media"),
        ("Mediana", "Mediana"),
        ("Moda", "Moda"),
        ("Varianza", "Varianza"),
        ("Desv.Estd", "Desviación Estándar"),
        ("Mínimo", "Mínimo"),
        ("Máximo", "Máximo"),
        ("Límite Inf", "Límite Inferior"),
        ("Límite Sup", "Límite Superior"),
        ("Eventos", "N° de Eventos")
    ]

    for col, text in encabezados:
        tabla.heading(col, text=text)
        tabla.column(col, width=120, anchor="center")

    tabla.pack(fill=tk.BOTH, expand=True)
    scroll_y = ttk.Scrollbar(parent, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll_y.set)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    scroll_x = ttk.Scrollbar(parent, orient="horizontal", command=tabla.xview)
    tabla.configure(xscrollcommand=scroll_x.set)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    return tabla

def mostrar_tabla_estadisticas(tabla):
    datos = obtener_estadisticas_eventos()
    for mes, media, mediana, moda, varianza, desviacion, minimo, maximo, limite_inferior, limite_superior, num_eventos in datos:
        tabla.insert("", "end", values=(
            MESES.get(mes, "Mes Desconocido"),
            f"{media:.2f}",
            f"{mediana:.2f}",
            moda,
            f"{varianza:.2f}",
            f"{desviacion:.2f}",
            minimo,
            maximo,
            f"{limite_inferior:.2f}",
            f"{limite_superior:.2f}",
            num_eventos
        ))

def mostrar_grafico_estadisticas(frame):
    datos = obtener_estadisticas_eventos()
    meses = [MESES.get(fila[0], "Desconocido") for fila in datos]
    medias = [float(fila[1]) for fila in datos]
    valores_por_mes = [list(map(float, fila[1:9])) for fila in datos]

    for widget in frame.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    fig, ax = plt.subplots(2, 1, figsize=(10, 12))

    ax[0].boxplot(valores_por_mes, vert=True, showfliers=False)
    ax[0].set_xticklabels(meses)
    ax[0].set_title("Diagrama de Caja y Bigotes por Mes", fontsize=14)
    ax[0].set_ylabel("Número de Personas", fontsize=12)
    ax[0].set_ylim(0, 200)
    ax[0].set_xlabel("Meses", fontsize=12)

    eventos_por_mes = [fila[10] for fila in datos]
    ax[1].pie(eventos_por_mes, labels=meses, autopct='%1.1f%%', startangle=90)
    ax[1].set_title("Distribución de Eventos por Mes", fontsize=14, y=-0.15)

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

ventana = tk.Tk()
ventana.title("Tacountry")
ventana.geometry("800x600")

notebook = ttk.Notebook(ventana)
notebook.pack(fill=tk.BOTH, expand=True)

crear_tab_agregar_empleado()
crear_tab_con_filtro_por_nombre_y_letra(
    "cliente", 
    ["ID", "Nombre", "Teléfono"], 
    "cli_id", 
    ["Nombre", "Teléfono"]
)
crear_tab_con_filtro_por_mes_y_cliente(
    "evento", 
    ["ID", "Fecha", "N° Personas", "Lugar", "Precio Total", "Tipo", "Pago", "Tipo de pago", "Cliente"], 
    "eve_id", 
    ["Fecha", "N° Personas", "Lugar", "Precio Total", "Tipo", "Pago", "Tipo de pago", "Cliente"] 
)
crear_tab_clientes_segmentados()
crear_tab_ventas_por_mes()
crear_tab_analisis_geografico()
crear_tab_prediccion_demanda(notebook)

frame_estadisticas = tk.Frame(notebook)

tabla = crear_tabla_estadisticas(frame_estadisticas)
mostrar_tabla_estadisticas(tabla)

mostrar_grafico_estadisticas(frame_estadisticas)

notebook.add(frame_estadisticas, text="Estadísticas")

ventana.mainloop()
