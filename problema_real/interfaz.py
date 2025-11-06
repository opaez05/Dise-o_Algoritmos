# interfaz.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from logica import cargar_datos, ejecutar_algoritmo_genetico
from config import NUM_VEHICULOS, COLOR_FONDO, COLOR_BOTON, COLOR_TEXTO
from logica import cargar_datos, ejecutar_algoritmo_genetico

class AppCVRPTW:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Rutas - CVRPTW")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLOR_FONDO)

        self.almacen = None
        self.clientes = None
        self.rutas = None

        self.crear_interfaz()

    def crear_interfaz(self):
        # === Frame superior: botones ===
        frame_botones = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_botones.pack(pady=10)

        btn_cargar = tk.Button(frame_botones, text="Cargar Datos", command=self.cargar_datos_ui,
                               bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"), width=15)
        btn_cargar.grid(row=0, column=0, padx=5)

        btn_ejecutar = tk.Button(frame_botones, text="Ejecutar Algoritmo", command=self.ejecutar,
                                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=18)
        btn_ejecutar.grid(row=0, column=1, padx=5)

        # === Frame medio: estadísticas ===
        frame_stats = tk.LabelFrame(self.root, text=" Estadísticas ", font=("Arial", 11, "bold"), bg=COLOR_FONDO)
        frame_stats.pack(pady=10, padx=20, fill="x")

        self.lbl_costo = tk.Label(frame_stats, text="Costo total: -", bg=COLOR_FONDO, font=("Arial", 10))
        self.lbl_costo.pack(side="left", padx=20)
        self.lbl_ahorro = tk.Label(frame_stats, text="Ahorro: -", bg=COLOR_FONDO, font=("Arial", 10))
        self.lbl_ahorro.pack(side="left", padx=20)

        # === Frame inferior: rutas ===
        frame_rutas = tk.LabelFrame(self.root, text=" Rutas Optimizadas ", font=("Arial", 11, "bold"), bg=COLOR_FONDO)
        frame_rutas.pack(pady=10, padx=20, fill="both", expand=True)

        cols = ("Furgoneta", "Ruta", "Tiempo", "Carga")
        self.tree = ttk.Treeview(frame_rutas, columns=cols, show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_rutas, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def cargar_datos_ui(self):
        self.almacen, self.clientes = cargar_datos()
        messagebox.showinfo("Éxito", f"¡Datos cargados!\n200 clientes + 1 almacén listos.")

    def ejecutar(self):
        if not self.clientes:
            messagebox.showwarning("Error", "Primero carga los datos.")
            return

        self.rutas, costo_total, ahorro = ejecutar_algoritmo_genetico(self.almacen, self.clientes)

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Llenar tabla
        for i, ruta in enumerate(self.rutas):
            ruta_str = " → ".join(map(str, ruta))
            tiempo = round(400 + i*20, 1)  # simulado
            carga = len(ruta) - 2  # sin almacén
            self.tree.insert("", "end", values=(f"Furgoneta {i+1}", ruta_str, f"{tiempo} min", f"{carga}/{40}"))

        # Actualizar stats
        self.lbl_costo.config(text=f"Costo total: {costo_total} min")
        self.lbl_ahorro.config(text=f"Ahorro estimado: {ahorro}%")

# === Ejecutar app ===
if __name__ == "__main__":
    root = tk.Tk()
    app = AppCVRPTW(root)
    root.mainloop()