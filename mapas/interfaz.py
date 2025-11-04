# interfaz.py (Con Estructura de Vistas)

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os 
import sys
import io 
import requests

# Se asume que logica.py está en la misma carpeta
from logica import DistanceCalculator 

# --- CONFIGURACIÓN DE ESTILOS Y DATOS ---
COLOR_BACKGROUND = "#f4f7f8" 
COLOR_PRIMARY = "#3498db" 
COLOR_TEXT_DARK = "#2c3e50" 
COLOR_ERROR = "#e74c3c"
CIUDADES_COLOMBIA = [
    "Arauca, Colombia", "Armenia, Colombia", "Barranquilla, Colombia", "Bogotá, Colombia",
    "Bucaramanga, Colombia", "Cali, Colombia", "Cartagena, Colombia", "Cúcuta, Colombia",
    "Ibagué, Colombia", "Manizales, Colombia", "Medellín, Colombia", "Montería, Colombia",
    "Neiva, Colombia", "Pasto, Colombia", "Pereira, Colombia", "Santa Marta, Colombia",
    "Villavicencio, Colombia", "Yopal, Colombia"
]
MODOS_TRANSPORTE = [
    ("Coche (Rápido)", "driving"), 
    ("Caminando", "walking"), 
    ("Bicicleta", "bicycling"), 
    ("Transporte público", "transit")
]
MODOS_MAP = dict(MODOS_TRANSPORTE)


# ----------------------------------------------------
# VISTA 1: Panel de Control (Inputs y Botón Calcular)
# ----------------------------------------------------
class ControlPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Background.TFrame")
        self.controller = controller
        self.columnconfigure(0, weight=1) 
        self.columnconfigure(1, weight=3)
        self.destino_entries = []
        
        self._create_widgets()

    def _create_widgets(self):
        # Origen
        ttk.Label(self, text="Ciudad/Dirección de Origen:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        # Combobox Editable para aceptar cualquier municipio o dirección
        self.origen_combo = ttk.Combobox(self, values=CIUDADES_COLOMBIA, width=30)
        self.origen_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.origen_combo.set(CIUDADES_COLOMBIA[8]) # Ibagué

        # Destinos Container
        self.destino_frame = ttk.Frame(self, style="Background.TFrame")
        self.destino_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        self.destino_frame.columnconfigure(0, weight=1)
        self.destino_frame.columnconfigure(1, weight=3)
        self.add_destino_row("Destino Final:")

        # Botones Agregar/Quitar
        button_frame = ttk.Frame(self, style="Background.TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="➕ Agregar Parada", command=self.add_destino, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="➖ Quitar Última", command=self.remove_destino, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)

        # Modo de transporte
        ttk.Label(self, text="Modo de Transporte:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.modo_var = tk.StringVar(value=MODOS_TRANSPORTE[0][1])
        modo_nombres = [m[0] for m in MODOS_TRANSPORTE]
        self.modo_combo = ttk.Combobox(self, values=modo_nombres, state="readonly", width=30)
        self.modo_combo.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.modo_combo.set(modo_nombres[0])
        self.modo_combo.bind("<<ComboboxSelected>>", lambda e: self.modo_var.set(MODOS_MAP[self.modo_combo.get()]))

        # Botón Calcular
        calc_button = ttk.Button(self, text="Calcular Ruta y Distancia", 
                                 command=self.controller.calcular_ruta, 
                                 style="Primary.TButton")
        calc_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")

    def add_destino_row(self, label_text):
        frame = ttk.Frame(self.destino_frame, style="Background.TFrame")
        frame.pack(fill="x", pady=5)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)
        label = ttk.Label(frame, text=label_text)
        label.grid(row=0, column=0, padx=10, sticky="w")
        
        # Combobox Editable
        combo = ttk.Combobox(frame, values=CIUDADES_COLOMBIA, width=30)
        combo.grid(row=0, column=1, padx=10, sticky="ew")
        
        # Asigna valores iniciales para la demostración
        initial_sets = [CIUDADES_COLOMBIA[10], CIUDADES_COLOMBIA[3]] # Medellín, Bogotá
        combo.set(initial_sets[len(self.destino_entries) % len(initial_sets)])
        
        self.destino_entries.append((label, combo))
        self.update_destino_labels()

    def update_destino_labels(self):
        for i, (label, combo) in enumerate(self.destino_entries):
            if i == len(self.destino_entries) - 1:
                label.config(text="Destino Final:")
            else:
                label.config(text=f"Parada Intermedia {i+1}:")

    def add_destino(self):
        if len(self.destino_entries) < 5: 
            self.add_destino_row(f"Destino Intermedio {len(self.destino_entries) + 1}:")
        else:
            messagebox.showwarning("Límite Alcanzado", "Máximo 5 paradas intermedias permitidas.")

    def remove_destino(self):
        if len(self.destino_entries) > 1: 
            label, combo = self.destino_entries.pop()
            label.master.destroy()
            self.update_destino_labels()
        else:
            messagebox.showwarning("Límite", "Debe haber al menos un Destino Final.")

    def get_input_data(self):
        """Retorna los datos de entrada del formulario."""
        origen = self.origen_combo.get().strip()
        destinos = [combo.get().strip() for _, combo in self.destino_entries]
        modo = self.modo_var.get()

        if not origen or not destinos:
            raise ValueError("Por favor, selecciona o introduce origen y al menos un destino.")
            
        return [origen] + destinos, modo

# ----------------------------------------------------
# VISTA 2: Panel de Resultados (Mapa y Texto)
# ----------------------------------------------------
class ResultsView(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style="Background.TFrame", padding="10 0 10 0")
        self.columnconfigure(0, weight=1) 
        self.columnconfigure(1, weight=1) 
        self.rowconfigure(0, weight=1)
        self.photo = None # Para mantener la referencia de la imagen
        
        self._create_widgets()

    def _create_widgets(self):
        # A. Contenedor Izquierdo: Mapa
        map_frame = ttk.LabelFrame(self, text="Mapa de la Ruta (Static API)", padding="10 5", style="Background.TFrame")
        map_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.map_label = tk.Label(map_frame, background=COLOR_BACKGROUND) 
        self.map_label.pack(fill="both", expand=True)

        # B. Contenedor Derecho: Información del Viaje
        info_frame = ttk.LabelFrame(self, text="Resumen del Viaje", padding="10 5", style="Background.TFrame")
        info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.result_label = ttk.Label(info_frame, text="Esperando cálculo...", 
                                      wraplength=500, justify="left", 
                                      foreground=COLOR_TEXT_DARK, 
                                      font=("Segoe UI", 11))
        self.result_label.pack(fill="both", expand=True, padx=5, pady=5)

    def display_success(self, informe_texto, mapa_url):
        self.result_label.config(text=informe_texto, foreground=COLOR_TEXT_DARK, font=("Segoe UI", 11, "bold"))
        self._mostrar_mapa(mapa_url)

    def display_error(self, error_msg):
        self.result_label.config(text=f"❌ ERROR DE CÁLCULO ❌\n{error_msg}", 
                                 foreground=COLOR_ERROR, font=("Segoe UI", 11, "bold"))
        self.map_label.config(image='')
        self.photo = None

    def _mostrar_mapa(self, url):
        """Descarga la imagen del mapa Static API y la muestra."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() 
            
            image_data = io.BytesIO(response.content)
            img = Image.open(image_data)
            
            # Redimensionar la imagen para que encaje
            img = img.resize((550, 350), Image.Resampling.LANCZOS) # Tamaño fijo para Static API
            
            self.photo = ImageTk.PhotoImage(img)
            
            self.map_label.config(image=self.photo)
            
        except requests.exceptions.RequestException as e:
            self.display_error(f"Error de red al descargar el mapa: {e}")
        except Exception as e:
            self.display_error(f"Error al procesar la imagen del mapa: {e}")


# ----------------------------------------------------
# CONTROLADOR PRINCIPAL: Une Lógica y Vistas
# ----------------------------------------------------
class MapInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("📍 Calculadora de Rutas y Distancias")
        self.root.geometry("1200x650") 
        self.root.resizable(True,True)
        self.root.configure(bg=COLOR_BACKGROUND)
        self._configure_styles()
        
        try:
            # Inicialización de la lógica (Modelo)
            self.calc = DistanceCalculator()
        except ValueError as e:
            messagebox.showerror("Error de Configuración", str(e))
            self.calc = None 

        self._build_layout()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Primary.TButton", font=("Segoe UI", 12, "bold"), padding=10, 
                        background=COLOR_PRIMARY, foreground="#ffffff", bordercolor=COLOR_PRIMARY)
        style.map("Primary.TButton", background=[("active", "#2980b9")])
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=5, 
                        background="#2ecc71", foreground="#ffffff", bordercolor="#2ecc71")
        style.map("Secondary.TButton", background=[("active", "#27ae60")])
        style.configure("TLabel", font=("Segoe UI", 10), foreground=COLOR_TEXT_DARK, background=COLOR_BACKGROUND)
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("Background.TFrame", background=COLOR_BACKGROUND)
    
    def _build_layout(self):
        # 1. Cabecera (Se mantiene simple, sin ser una vista aparte)
        header_container = ttk.Frame(self.root, style="Background.TFrame") 
        header_container.pack(fill="x", pady=10)
        content_frame = ttk.Frame(header_container, style="Background.TFrame") 
        content_frame.pack(anchor="center") 
        self._add_logo(content_frame)
        ttk.Label(content_frame, text="🌎 Calculadora de Ruta en Colombia", 
                  font=("Segoe UI", 18, "bold"), foreground=COLOR_PRIMARY, background=COLOR_BACKGROUND).pack(side=tk.LEFT) 

        # 2. Contenedor Principal
        main_frame = ttk.Frame(self.root, padding="20 15 20 15", style="Background.TFrame")
        main_frame.pack(fill="both", padx=20, pady=10, expand=True)

        # 3. Vista de Control (Inputs y Botón)
        self.control_view = ControlPanel(main_frame, self)
        self.control_view.pack(fill="x")

        # 4. Vista de Resultados (Mapa y Texto)
        self.results_view = ResultsView(main_frame)
        self.results_view.pack(fill="both", expand=True)
        
    def _add_logo(self, parent_frame):
        try:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            image_path = os.path.join(base_path, "img", "logo.png")
            img = Image.open(image_path) 
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            self.photo_logo = ImageTk.PhotoImage(img) 
            tk.Label(parent_frame, image=self.photo_logo, background=COLOR_BACKGROUND).pack(side=tk.LEFT, padx=(0, 10)) 
        except Exception:
            pass # Ignorar si el logo no está

    # Lógica de conexión centralizada en el controlador
    def calcular_ruta(self):
        if not self.calc:
            return

        try:
            # Obtiene datos de la vista de control
            ciudades, modo = self.control_view.get_input_data()
            
            # Llamada al modelo/lógica
            informe_texto, mapa_url = self.calc.calcular_y_mapear_ruta(ciudades, modo)
            
            # Muestra el resultado en la vista de resultados
            self.results_view.display_success(informe_texto, mapa_url)
            
        except ValueError as e:
            messagebox.showerror("Error de Entrada", str(e))
        except (ConnectionError, RuntimeError) as e:
            # Muestra el error en la vista de resultados
            self.results_view.display_error(str(e))


def main():
    root = tk.Tk()
    app = MapInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()