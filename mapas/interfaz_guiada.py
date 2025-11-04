import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os 
import sys
import io 
import requests
import csv 
from logica import DistanceCalculator 

# --- CONFIGURACIÓN DE ESTILOS Y DATOS ---
COLOR_BACKGROUND = "#f4f7f8" 
COLOR_PRIMARY = "#3498db" 
COLOR_TEXT_DARK = "#2c3e50" 
COLOR_ERROR = "#e74c3c"
MODOS_TRANSPORTE = [
    ("Coche (Rápido)", "driving"), 
    ("Caminando", "walking"), 
]
MODOS_MAP = dict(MODOS_TRANSPORTE)
RUTA_ABSOLUTA_CSV = r"C:\Users\oscar\Documents\sexto\diseño\mapas\destinos.csv"


def load_geografia(file_path): 
    geografia = {}
    full_path = file_path # La ruta es el argumento
    
    # Verificar
    if not os.path.exists(full_path):
        print(f"ADVERTENCIA: Archivo CSV no encontrado en: {full_path}. Usando datos mínimos.")
        # Fallback si no encuentra el archivo
        return {
            "Antioquia": ["Medellín", "Rionegro"],
            "Cundinamarca": ["Bogotá", "Soacha"]
        }
        
    try:
        # Usar la ruta absoluta
        with open(full_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Omitir la fila del encabezado
            next(reader) 
            for row in reader:
                if len(row) < 5: continue
                departamento = row[2].strip().title()
                municipio = row[4].strip().title()
                if departamento and municipio:
                    if departamento not in geografia:
                        geografia[departamento] = []
                    if municipio not in geografia[departamento]:
                        geografia[departamento].append(municipio)
        for depto in geografia:
            geografia[depto].sort()
    except Exception as e:
        messagebox.showerror("Error de Datos", f"Falló la lectura del archivo CSV: {e}. Usando datos mínimos.")
        return {
            "Antioquia": ["Medellín", "Rionegro"],
            "Cundinamarca": ["Bogotá", "Soacha"]
        }
        
    print(f"Se cargaron {len(geografia)}.")
    return geografia

GEOGRAFIA_COLOMBIA = load_geografia(file_path=RUTA_ABSOLUTA_CSV)
DEPARTAMENTOS = sorted(list(GEOGRAFIA_COLOMBIA.keys()))

# Panel de Control
class ControlPanelGuiada(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Background.TFrame")
        self.controller = controller
        # Configuración de 4 columnas para el formulario
        self.columnconfigure(0, weight=1) 
        self.columnconfigure(1, weight=1) 
        self.columnconfigure(2, weight=1) 
        self.columnconfigure(3, weight=1) 
        self.destino_entries = []
        self._create_widgets()

    def _create_widgets(self):
        # Origen - Departamento
        ttk.Label(self, text="Origen (Depto):").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.origen_depto_combo = ttk.Combobox(self, values=DEPARTAMENTOS, state="readonly", width=15)
        self.origen_depto_combo.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        self.origen_depto_combo.bind("<<ComboboxSelected>>", lambda e: self._update_municipios(self.origen_depto_combo, self.origen_muni_combo))
        
        # Origen - Municipio
        ttk.Label(self, text="Origen (Municipio):").grid(row=0, column=2, padx=5, pady=8, sticky="w")
        self.origen_muni_combo = ttk.Combobox(self, values=[], width=15, state="readonly")
        self.origen_muni_combo.grid(row=0, column=3, padx=5, pady=8, sticky="ew")

        # Separador de Destinos
        self.destino_frame = ttk.Frame(self, style="Background.TFrame")
        self.destino_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")
        self.destino_frame.columnconfigure(0, weight=1)
        self.destino_frame.columnconfigure(1, weight=1)
        self.destino_frame.columnconfigure(2, weight=1)
        self.destino_frame.columnconfigure(3, weight=1)

        self.add_destino_row("Destino Final:", 0)

        # Botones Agregar/Quitar
        button_frame = ttk.Frame(self, style="Background.TFrame")
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="➕ Agregar Parada", command=self.add_destino, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="➖ Quitar Última", command=self.remove_destino, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)

        # Modo de transporte (Fila 3)
        ttk.Label(self, text="Modo de Transporte:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.modo_var = tk.StringVar(value=MODOS_TRANSPORTE[0][1])
        modo_nombres = [m[0] for m in MODOS_TRANSPORTE]
        self.modo_combo = ttk.Combobox(self, values=modo_nombres, state="readonly", width=30)
        self.modo_combo.grid(row=3, column=1, columnspan=3, padx=10, pady=8, sticky="ew")
        self.modo_combo.set(modo_nombres[0])
        self.modo_combo.bind("<<ComboboxSelected>>", lambda e: self.modo_var.set(MODOS_MAP[self.modo_combo.get()]))

        # Botón Calcular (Fila 4)
        calc_button = ttk.Button(self, text="Calcular Ruta y Distancia", 
                                command=self.controller.calcular_ruta, 
                                style="Primary.TButton")
        calc_button.grid(row=4, column=0, columnspan=4, pady=20, sticky="ew")

    def _update_municipios(self, depto_combo, muni_combo):
        departamento = depto_combo.get()
        municipios = GEOGRAFIA_COLOMBIA.get(departamento, [])
        muni_combo['values'] = municipios
        muni_combo['state'] = 'readonly' if municipios else 'disabled'
        if municipios:
            muni_combo.set(municipios[0]) 
        else:
            muni_combo.set("Selecciona Depto") 

    def add_destino_row(self, label_text, row_index):
        # Etiqueta de Destino (Columna 0)
        label = ttk.Label(self.destino_frame, text=label_text)
        label.grid(row=row_index, column=0, padx=5, sticky="w")
        # Departamento (Columna 1)
        depto_combo = ttk.Combobox(self.destino_frame, values=DEPARTAMENTOS, state="readonly", width=15)
        depto_combo.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")
        # Municipio (Columna 2 y 3)
        muni_combo = ttk.Combobox(self.destino_frame, values=[], width=15, state="disabled")
        muni_combo.grid(row=row_index, column=3, padx=5, pady=5, sticky="ew")
        # Lógica de cascada
        depto_combo.bind("<<ComboboxSelected>>", lambda e, d=depto_combo, m=muni_combo: self._update_municipios(d, m))
        # Inicialización de valores por defecto
        if DEPARTAMENTOS:
            depto_combo.set("Cundinamarca" if "Cundinamarca" in DEPARTAMENTOS else DEPARTAMENTOS[0])
            self._update_municipios(depto_combo, muni_combo)
            if "Bogotá" in muni_combo['values']:
                muni_combo.set("Bogotá")
        
        self.destino_entries.append((depto_combo, muni_combo))
        self.update_destino_labels()

    def update_destino_labels(self):
        # Actualiza las etiquetas
        for i, (depto_combo, muni_combo) in enumerate(self.destino_entries):
            # Se busca el Label en la misma fila del grid
            row_widgets = depto_combo.master.grid_slaves(row=depto_combo.grid_info()['row'])
            label_widget = next((w for w in row_widgets if isinstance(w, ttk.Label)), None)

            if label_widget:
                if i == len(self.destino_entries) - 1:
                    label_widget.config(text="Destino Final:")
                else:
                    label_widget.config(text=f"Parada {i+1}:")

    def add_destino(self):
        if len(self.destino_entries) < 5: 
            new_row_index = len(self.destino_entries) 
            self.add_destino_row(f"Parada {new_row_index + 1}:", new_row_index)
        else:
            messagebox.showwarning("Límite Alcanzado", "Máximo 5 paradas intermedias permitidas.")

    def remove_destino(self):
        if len(self.destino_entries) > 1: 
            depto_combo, muni_combo = self.destino_entries.pop()
            depto_combo.master.destroy() 
            self.update_destino_labels()
        else:
            messagebox.showwarning("Límite", "Debe haber al menos un Destino Final.")

    def get_input_data(self):
        origen_depto = self.origen_depto_combo.get()
        origen_muni = self.origen_muni_combo.get()
        if not origen_depto or not origen_muni or origen_muni == "Selecciona Depto":
            raise ValueError("Por favor, selecciona el Origen completo (Departamento y Municipio).")

        # Concatenar para la API de Google: "Municipio, Departamento, Colombia"
        ciudades = [f"{origen_muni}, {origen_depto}, Colombia"] 

        for depto_combo, muni_combo in self.destino_entries:
            destino_depto = depto_combo.get()
            destino_muni = muni_combo.get()
            if not destino_depto or not destino_muni or destino_muni == "Selecciona Depto":
                raise ValueError("Por favor, selecciona todos los Destinos/Paradas completos.")
            ciudades.append(f"{destino_muni}, {destino_depto}, Colombia")
        modo = self.modo_var.get()
        return ciudades, modo
    

# Panel de Resultados 
class ResultsView(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style="Background.TFrame", padding="10 0 10 0")
        self.columnconfigure(0, weight=1) 
        self.columnconfigure(1, weight=1) 
        self.rowconfigure(0, weight=1)
        self.photo = None 
        self._create_widgets()

    def _create_widgets(self):
        # Contenedor Izquierdo: Mapa
        map_frame = ttk.LabelFrame(self, text="Mapa de la Ruta (Static API)", padding="10 5", style="Background.TFrame")
        map_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.map_label = tk.Label(map_frame, background=COLOR_BACKGROUND) 
        self.map_label.pack(fill="both", expand=True)

        # Contenedor Derecho: Información del Viaje
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
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() 
            image_data = io.BytesIO(response.content)
            img = Image.open(image_data)
            # Redimensionar la imagen para que encaje
            img = img.resize((550, 350), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.map_label.config(image=self.photo)   
        except requests.exceptions.RequestException as e:
            self.display_error(f"Error de red al descargar el mapa: {e}")
        except Exception as e:
            self.display_error(f"Error al procesar la imagen del mapa: {e}")


# CONTROLADOR PRINCIPAL
class MapInterfaceGuiada:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Rutas")
        self.root.state('zoomed') 
        self.root.resizable(True,True)
        self.root.configure(bg=COLOR_BACKGROUND)
        self._configure_styles()
        try:
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
        # Cabecera
        header_container = ttk.Frame(self.root, style="Background.TFrame") 
        header_container.pack(fill="x", pady=10)
        content_frame = ttk.Frame(header_container, style="Background.TFrame") 
        content_frame.pack(anchor="center") 
        self._add_logo(content_frame)
        ttk.Label(content_frame, text="🌎 Calculadora de Ruta en Colombia (Guiada por DANE)", 
                font=("Segoe UI", 18, "bold"), foreground=COLOR_PRIMARY, background=COLOR_BACKGROUND).pack(side=tk.LEFT) 
        main_frame = ttk.Frame(self.root, padding="20 15 20 15", style="Background.TFrame")
        main_frame.pack(fill="both", padx=20, pady=10, expand=True)
        self.control_view = ControlPanelGuiada(main_frame, self)
        self.control_view.pack(fill="x")
        self.results_view = ResultsView(main_frame)
        self.results_view.pack(fill="both", expand=True)
        
    def _add_logo(self, parent_frame):
        # Intentar cargar el logo desde la carpeta 'img' si existe
        try:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            image_path = os.path.join(base_path, "img", "logo.png")
            img = Image.open(image_path) 
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            self.photo_logo = ImageTk.PhotoImage(img) 
            tk.Label(parent_frame, image=self.photo_logo, background=COLOR_BACKGROUND).pack(side=tk.LEFT, padx=(0, 10)) 
        except Exception:
            pass

    def calcular_ruta(self):
        if not self.calc:
            return

        try:
            ciudades, modo = self.control_view.get_input_data()
            informe_texto, mapa_url = self.calc.calcular_y_mapear_ruta(ciudades, modo)
            self.results_view.display_success(informe_texto, mapa_url)
        except ValueError as e:
            messagebox.showerror("Error de Entrada", str(e))
        except (ConnectionError, RuntimeError) as e:
            self.results_view.display_error(str(e))


def main():
    root = tk.Tk()
    app = MapInterfaceGuiada(root) 
    root.mainloop()

if __name__ == "__main__":
    main()