# interfaz.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
# Importamos para la ruta absoluta de la imagen
import os 
import sys
# Importamos la lógica corregida
from logica import DistanceCalculator 

class MapInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("📍 Calculadora de Rutas y Distancias")
        self.root.geometry("700x800") 
        self.root.resizable(False,True)
        
        # --- Esquema de Colores ---
        COLOR_BACKGROUND = "#ffffff" 
        COLOR_PRIMARY = "#3498db" 
        COLOR_SECONDARY = "#2ecc71" 
        COLOR_TEXT_DARK = "#2c3e50" 
        COLOR_ERROR = "#e74c3c"

        self.root.configure(bg=COLOR_BACKGROUND)

        # --- Estilo Moderno (Ttk) ---
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Estilos de Botones
        self.style.configure("Primary.TButton", 
                             font=("Segoe UI", 12, "bold"), 
                             padding=10, 
                             background=COLOR_PRIMARY, 
                             foreground="#ffffff", 
                             bordercolor=COLOR_PRIMARY)
        self.style.map("Primary.TButton", 
                       background=[("active", "#2980b9")])

        self.style.configure("Secondary.TButton", 
                             font=("Segoe UI", 10), 
                             padding=5, 
                             background=COLOR_SECONDARY, 
                             foreground="#ffffff", 
                             bordercolor=COLOR_SECONDARY)
        self.style.map("Secondary.TButton", 
                       background=[("active", "#27ae60")])

        # Estilos de Texto y Frames
        self.style.configure("TLabel", 
                             font=("Segoe UI", 10), 
                             foreground=COLOR_TEXT_DARK,
                             background=COLOR_BACKGROUND)
        self.style.configure("TCombobox", font=("Segoe UI", 10))
        
        # 🚨 CORRECCIÓN: Estilo para frames con color de fondo (Obligatorio en ttk)
        self.style.configure("Background.TFrame", background=COLOR_BACKGROUND)

        self.ciudades = [
            "Arauca, Colombia", "Armenia, Colombia", "Barranquilla, Colombia", "Bogotá, Colombia",
            "Bucaramanga, Colombia", "Cali, Colombia", "Cartagena, Colombia", "Cúcuta, Colombia",
            "Florencia, Colombia", "Ibagué, Colombia", "Inírida, Colombia", "La Guajira, Colombia",
            "Leticia, Colombia", "Manizales, Colombia", "Medellín, Colombia", "Mitú, Colombia",
            "Mocoa, Colombia", "Montería, Colombia", "Neiva, Colombia", "Pasto, Colombia",
            "Pereira, Colombia", "Popayán, Colombia", "Quibdó, Colombia", "Riohacha, Colombia",
            "San Andrés, Colombia", "San José del Guaviare, Colombia", "Santa Marta, Colombia",
            "Sincelejo, Colombia", "Tunja, Colombia", "Valledupar, Colombia", "Villavicencio, Colombia",
            "Yopal, Colombia"
        ]

        # Inicialización de la clase de cálculo 
        try:
            self.calc = DistanceCalculator()
        except ValueError as e:
            messagebox.showerror("Error de Configuración", str(e))
            self.calc = None 

        # --- 1. Frame Superior para Logo y Título (Alineación Centrada) ---
        header_container = ttk.Frame(root, style="Background.TFrame") 
        header_container.pack(fill="x", pady=10)
        
        content_frame = ttk.Frame(header_container, style="Background.TFrame") 
        content_frame.pack(anchor="center") 

        # --- 2. Carga y Muestra de la Imagen (Ruta Absoluta Segura) ---
        try:
            # 🚨 SOLUCIÓN DE RUTA: Obtener el path absoluto del script y añadir 'img/logo.png'
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            image_path = os.path.join(base_path, "img", "logo.png")
            
            img = Image.open(image_path) 
            
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img) 
            
            img_label = tk.Label(content_frame, image=self.photo, background=COLOR_BACKGROUND)
            img_label.pack(side=tk.LEFT, padx=(0, 10)) 
            
        except FileNotFoundError:
            # Ahora reporta la ruta esperada si el archivo no se encuentra
            print(f"Advertencia: Archivo 'logo.png' no encontrado. Buscado en: {image_path}")
        except Exception as e:
            print(f"Advertencia: No se pudo cargar la imagen: {e}")

        # --- 3. Título Principal ---
        title_label = ttk.Label(content_frame, text="Calculadora de Ruta en Colombia", 
                                font=("Segoe UI", 18, "bold"), 
                                foreground=COLOR_PRIMARY, 
                                background=COLOR_BACKGROUND)
        title_label.pack(side=tk.LEFT) 

        # --- Estructura Principal del Formulario ---
        main_frame = ttk.Frame(root, padding="20 15 20 15", style="Background.TFrame")
        main_frame.pack(fill="both", padx=20, pady=10)
        
        main_frame.columnconfigure(0, weight=1) 
        main_frame.columnconfigure(1, weight=3)

        # Origen
        ttk.Label(main_frame, text="Ciudad de Origen:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.origen_combo = ttk.Combobox(main_frame, values=self.ciudades, state="readonly", width=30)
        self.origen_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.origen_combo.set(self.ciudades[3])

        # Destinos
        self.destino_frame = ttk.Frame(main_frame, style="Background.TFrame")
        self.destino_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        self.destino_frame.columnconfigure(0, weight=1)
        self.destino_frame.columnconfigure(1, weight=3)
        
        self.destino_entries = []
        self.add_destino_row(0, "Destino Final:")

        # Botones Agregar/Quitar
        button_frame = ttk.Frame(main_frame, style="Background.TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="➕ Agregar Parada", command=self.add_destino, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="➖ Quitar Última", command=self.remove_destino, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)

        # Modo de transporte
        ttk.Label(main_frame, text="Modo de Transporte:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.modo_var = tk.StringVar(value="driving")
        modos = [("Coche (Rápido)", "driving"), ("Caminando", "walking"), ("Bicicleta", "bicycling"), ("Transporte público", "transit")]
        modo_nombres = [m[0] for m in modos]
        self.modo_map = dict(modos)
        self.modo_combo = ttk.Combobox(main_frame, values=modo_nombres, state="readonly", width=30)
        self.modo_combo.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.modo_combo.set(modo_nombres[0])
        self.modo_combo.bind("<<ComboboxSelected>>", lambda e: self.modo_var.set(self.modo_map[self.modo_combo.get()]))

        # Botón Calcular
        calc_button = ttk.Button(main_frame, text="Calcular Ruta y Distancia", command=self.calcular_distancia, style="Primary.TButton")
        calc_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")

        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultado del Cálculo", padding="10 5", style="Background.TFrame")
        results_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        self.result_label = ttk.Label(results_frame, text="Selecciona el origen y al menos un destino para empezar.", 
                                      wraplength=500, justify="left", 
                                      foreground=COLOR_TEXT_DARK, 
                                      font=("Segoe UI", 11))
        self.result_label.pack(fill="x", padx=5, pady=5)
        self.COLOR_ERROR = COLOR_ERROR

    def add_destino_row(self, row_index, label_text):
        # Usamos el estilo Background.TFrame para los frames internos también
        frame = ttk.Frame(self.destino_frame, style="Background.TFrame") 
        frame.pack(fill="x", pady=5)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)
        label = ttk.Label(frame, text=label_text)
        label.grid(row=0, column=0, padx=10, sticky="w")
        combo = ttk.Combobox(frame, values=self.ciudades, state="readonly", width=30)
        combo.grid(row=0, column=1, padx=10, sticky="ew")
        combo.set(self.ciudades[4] if len(self.destino_entries) == 0 else self.ciudades[0])
        self.destino_entries.append((label, combo))
        self.update_destino_labels()
        return len(self.destino_entries) - 1

    def update_destino_labels(self):
        for i, (label, combo) in enumerate(self.destino_entries):
            if i == len(self.destino_entries) - 1:
                label.config(text="Destino Final:")
            else:
                label.config(text=f"Parada Intermedia {i+1}:")

    def add_destino(self):
        if len(self.destino_entries) < 4: 
            self.add_destino_row(len(self.destino_entries), f"Destino Intermedio {len(self.destino_entries) + 1}:")
        else:
            messagebox.showwarning("Límite Alcanzado", "Máximo 4 paradas intermedias permitidas.")

    def remove_destino(self):
        if len(self.destino_entries) > 1: 
            label, combo = self.destino_entries.pop()
            label.master.destroy()
            self.update_destino_labels()
        else:
            messagebox.showwarning("Límite", "Debe haber al menos un Destino Final.")

    def calcular_distancia(self):
        if not self.calc:
            return

        origen = self.origen_combo.get().strip()
        destinos = [combo.get().strip() for _, combo in self.destino_entries]
        modo = self.modo_var.get()

        if not origen or not destinos:
            messagebox.showerror("Error", "Por favor, selecciona origen y al menos un destino.")
            return

        ciudades = [origen] + destinos 

        try:
            resultado = self.calc.calcular_ruta_multiples(ciudades, modo)
            
            # Formato de resultado exitoso
            self.result_label.config(text=resultado, foreground="#2c3e50", font=("Segoe UI", 11, "bold"))
            
        except (ConnectionError, RuntimeError, ValueError) as e:
            # Captura errores específicos y muéstralos al usuario
            error_msg = f"❌ ERROR DE CÁLCULO ❌\n{str(e)}"
            self.result_label.config(text=error_msg, foreground=self.COLOR_ERROR, font=("Segoe UI", 11, "bold"))


def main():
    root = tk.Tk()
    app = MapInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()