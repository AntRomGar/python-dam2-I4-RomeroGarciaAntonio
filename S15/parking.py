import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import uuid

# Clases y lógica (igual a tu código original, con pequeñas adaptaciones)

class Plaza:
    def __init__(self, numero, tipo):
        self.numero = numero
        self.tipo = tipo
        self.estado = "libre"

    def reservar(self):
        if self.estado == "libre":
            self.estado = "reservada"
            return True
        return False

    def liberar(self):
        self.estado = "libre"

    def ocupar(self):
        if self.estado in ["libre", "reservada"]:
            self.estado = "ocupada"
            return True
        return False

    def __str__(self):
        return f"Plaza {self.numero:02d} [{self.tipo.upper():&lt;6}] -&gt; {self.estado.upper()}"

class Vehiculo:
    def __init__(self, matricula, tipo):
        self.matricula = matricula.upper()
        self.tipo = tipo

class Ticket:
    def __init__(self, vehiculo):
        self.codigo = str(uuid.uuid4())[:8]
        self.vehiculo = vehiculo
        self.hora_entrada = datetime.now()
        self.hora_salida = None

    def registrar_salida(self):
        self.hora_salida = datetime.now()

    def calcular_tiempo(self):
        fin = self.hora_salida if self.hora_salida else datetime.now()
        return fin - self.hora_entrada

class Parking:
    def __init__(self):
        self.plazas = []
        self.tarifas = {"coche": 2.50, "moto": 1.50}

    def agregar_plaza(self, plaza):
        self.plazas.append(plaza)

    def reservar_y_generar_ticket(self, vehiculo):
        for plaza in self.plazas:
            if plaza.tipo == vehiculo.tipo and plaza.estado == "libre":
                plaza.ocupar()
                ticket = Ticket(vehiculo)
                return ticket, plaza
        return None, None

    def procesar_salida(self, ticket, plaza):
        # Simulación: restamos 90 min para ver el cobro
        ticket.hora_entrada -= timedelta(minutes=90)
        ticket.registrar_salida()

        tiempo = ticket.calcular_tiempo()
        horas = tiempo.total_seconds() / 3600
        total = round(horas * self.tarifas.get(ticket.vehiculo.tipo, 2.0), 2)

        return {
            "codigo": ticket.codigo,
            "matricula": ticket.vehiculo.matricula,
            "tiempo_horas": int(horas),
            "tiempo_minutos": int((horas % 1) * 60),
            "total": total
        }


# Interfaz gráfica con Tkinter

class ParkingApp(tk.Tk):
    def __init__(self, parking):
        super().__init__()
        self.title("Sistema de Gestión de Parking 2026")
        self.geometry("600x700")
        self.parking = parking
        self.tickets_activos = {}  # código_ticket -&gt; (ticket, plaza)

        self.create_widgets()
        self.actualizar_estado()

    def create_widgets(self):
        # Frame para estado de plazas
        frame_estado = ttk.LabelFrame(self, text="Estado de Plazas")
        frame_estado.pack(fill="x", padx=10, pady=10)

        self.tree = ttk.Treeview(frame_estado, columns=("Número", "Tipo", "Estado"), show="headings", height=6)
        self.tree.heading("Número", text="Número")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Estado", text="Estado")
        self.tree.column("Número", width=60, anchor="center")
        self.tree.column("Tipo", width=100, anchor="center")
        self.tree.column("Estado", width=100, anchor="center")
        self.tree.pack(fill="x")

        # Frame para entrada de vehículo
        frame_entrada = ttk.LabelFrame(self, text="Registrar Entrada")
        frame_entrada.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_entrada, text="Matrícula:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_matricula = ttk.Entry(frame_entrada)
        self.entry_matricula.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_entrada, text="Tipo vehículo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_tipo = ttk.Combobox(frame_entrada, values=["coche", "moto"], state="readonly")
        self.combo_tipo.grid(row=1, column=1, padx=5, pady=5)
        self.combo_tipo.current(0)

        btn_entrada = ttk.Button(frame_entrada, text="Registrar Entrada", command=self.registrar_entrada)
        btn_entrada.grid(row=2, column=0, columnspan=2, pady=10)

        # Frame para salida
        frame_salida = ttk.LabelFrame(self, text="Procesar Salida")
        frame_salida.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_salida, text="Código Ticket:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_codigo = ttk.Entry(frame_salida)
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5)

        btn_salida = ttk.Button(frame_salida, text="Procesar Salida y Pago", command=self.procesar_salida)
        btn_salida.grid(row=1, column=0, columnspan=2, pady=10)

        # Área de mensajes / recibo
        self.text_recibo = tk.Text(self, height=8, state="disabled")
        self.text_recibo.pack(fill="both", padx=10, pady=10)

    def actualizar_estado(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        for plaza in self.parking.plazas:
            estado = plaza.estado.capitalize()
            self.tree.insert("", "end",
                             values=(plaza.numero, plaza.tipo.capitalize(), estado),
                             tags=(plaza.estado,))
        # Colores según estado
        self.tree.tag_configure("libre", background="#d4edda")    # verde claro
        self.tree.tag_configure("ocupada", background="#f8d7da")  # rojo claro
        self.tree.tag_configure("reservada", background="#fff3cd")# amarillo claro

    def registrar_entrada(self):
        matricula = self.entry_matricula.get().strip()
        tipo = self.combo_tipo.get()

        if not matricula:
            messagebox.showwarning("Entrada inválida", "Debe ingresar la matrícula del vehículo.")
            return

        vehiculo = Vehiculo(matricula, tipo)
        ticket, plaza = self.parking.reservar_y_generar_ticket(vehiculo)

        if ticket is None:
            messagebox.showerror("Sin plazas", f"No hay plazas disponibles para {tipo}.")
            return

        self.tickets_activos[ticket.codigo] = (ticket, plaza)
        self.actualizar_estado()

        # Mostrar ticket
        self.text_recibo.configure(state="normal")
        self.text_recibo.delete("1.0", tk.END)
        self.text_recibo.insert(tk.END, f"✔ Entrada registrada.\nPlaza asignada: {plaza.numero}\n")
        self.text_recibo.insert(tk.END, f"Código Ticket: {ticket.codigo}\nMatrícula: {matricula}\nTipo: {tipo}\nHora Entrada: {ticket.hora_entrada.strftime('%Y-%m-%d %H:%M:%S')}")
        self.text_recibo.configure(state="disabled")

        # Limpiar campos
        self.entry_matricula.delete(0, tk.END)

    def procesar_salida(self):
        codigo = self.entry_codigo.get().strip()
        if codigo not in self.tickets_activos:
            messagebox.showerror("Código inválido", "No se encontró ningún ticket activo con ese código.")
            return

        ticket, plaza = self.tickets_activos.pop(codigo)
        recibo = self.parking.procesar_salida(ticket, plaza)
        plaza.liberar()
        self.actualizar_estado()

        # Mostrar recibo
        texto = (
            f"RECIBO DE PAGO\n"
            f"Ticket ID: {recibo['codigo']}\n"
            f"Matrícula: {recibo['matricula']}\n"
            f"Tiempo: {recibo['tiempo_horas']}h {recibo['tiempo_minutos']}min\n"
            f"TOTAL: {recibo['total']} €\n"
            f"Plaza {plaza.numero} ahora está LIBRE.\n"
        )
        self.text_recibo.configure(state="normal")
        self.text_recibo.delete("1.0", tk.END)
        self.text_recibo.insert(tk.END, texto)
        self.text_recibo.configure(state="disabled")

        self.entry_codigo.delete(0, tk.END)


if __name__ == "__main__":
    parking = Parking()
    for i in range(1, 4):
        parking.agregar_plaza(Plaza(i, "coche"))
    parking.agregar_plaza(Plaza(4, "moto"))

    app = ParkingApp(parking)
    app.mainloop()