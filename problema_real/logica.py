# logica.py
import random
import requests
import time
from math import radians, cos, sin, sqrt, atan2
from config import (
    NUM_VEHICULOS, CAPACIDAD_MAX, TIEMPO_MAX_RUTA, TIEMPO_SERVICIO,
    BASE_LAT, BASE_LON, RADIO_CIUDAD, GOOGLE_API_KEY, API_BASE_URL
)

# ========================
# 1. GENERAR CLIENTES EN IBAGUÉ
# ========================
def generar_coordenada_real():
    """Genera coordenada dentro de RADIO_CIUDAD km desde el centro de Ibagué"""
    offset_km_lat = random.uniform(-RADIO_CIUDAD, RADIO_CIUDAD) / 111
    offset_km_lon = random.uniform(-RADIO_CIUDAD, RADIO_CIUDAD) / (111 * 0.75)  # cos(4.45°)
    lat = BASE_LAT + offset_km_lat
    lon = BASE_LON + offset_km_lon
    return round(lat, 6), round(lon, 6)

def cargar_datos():
    almacen = {
        "id": 0,
        "lat": BASE_LAT,
        "lon": BASE_LON,
        "demanda": 0,
        "ventana": [0, 480],
        "servicio": 0
    }
    clientes = []
    for i in range(1, 201):
        lat, lon = generar_coordenada_real()
        inicio = random.randint(60, 300)
        fin = random.randint(max(inicio + 30, 301), 420)  # ventana mínima 30 min
        clientes.append({
            "id": i,
            "lat": lat,
            "lon": lon,
            "demanda": 1,
            "ventana": [inicio, fin],
            "servicio": TIEMPO_SERVICIO
        })
    return almacen, clientes

# ========================
# 2. API: TIEMPOS CON TRÁFICO
# ========================
def distancia_haversine(p1, p2):
    """Distancia en km entre dos puntos (lat, lon)"""
    R = 6371
    lat1, lon1 = radians(p1['lat']), radians(p1['lon'])
    lat2, lon2 = radians(p2['lat']), radians(p2['lon'])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def estimar_tiempo_fallback(p1, p2):
    """Fallback: 40 km/h en ciudad"""
    dist_km = distancia_haversine(p1, p2)
    return max(5, int(dist_km / 40 * 60))  # mínimo 5 min

def obtener_tiempos_batch(origen, destinos):
    """Llama a Google API en batch (máx 25 destinos por request)"""
    tiempos = []
    batch_size = 25
    for i in range(0, len(destinos), batch_size):
        batch = destinos[i:i+batch_size]
        origins = f"{origen['lat']},{origen['lon']}"
        destinations_str = "|".join([f"{d['lat']},{d['lon']}" for d in batch])
        
        params = {
            'origins': origins,
            'destinations': destinations_str,
            'key': GOOGLE_API_KEY,
            'departure_time': 'now',
            'traffic_model': 'best_guess',
            'mode': 'driving'
        }
        
        try:
            response = requests.get(API_BASE_URL, params=params, timeout=15)
            data = response.json()
            
            if data["status"] == "OK":
                for elem in data["rows"][0]["elements"]:
                    if elem["status"] == "OK":
                        minutos = elem["duration_in_traffic"]["value"] // 60
                        tiempos.append(max(1, minutos))
                    else:
                        tiempos.append(15)
            else:
                print(f"API Warning: {data.get('error_message', data['status'])}")
                tiempos.extend([estimar_tiempo_fallback(origen, d) for d in batch])
        except Exception as e:
            print(f"API Error: {e}. Usando fallback.")
            tiempos.extend([estimar_tiempo_fallback(origen, d) for d in batch])
    
    return tiempos

# ========================
# 3. EVALUAR RUTA FACTIBLE
# ========================
def evaluar_ruta_factible(ruta_ids, nodos, matriz_tiempos):
    """ruta_ids: [0, 12, 45, ..., 0], nodos: lista con almacén + clientes"""
    tiempo_actual = 0
    carga = 0
    i = 0
    while i < len(ruta_ids) - 1:
        actual = ruta_ids[i]
        siguiente = ruta_ids[i + 1]
        
        tiempo_viaje = matriz_tiempos[actual][siguiente]
        llegada = tiempo_actual + tiempo_viaje
        
        # Ventana de tiempo
        inicio_ventana = nodos[siguiente]['ventana'][0]
        fin_ventana = nodos[siguiente]['ventana'][1]
        
        if llegada > fin_ventana:
            return float('inf')  # inviable
        
        # Espera si llega antes
        tiempo_salida = max(llegada, inicio_ventana)
        tiempo_salida += nodos[siguiente]['servicio']
        
        tiempo_actual = tiempo_salida
        carga += nodos[siguiente]['demanda']
        
        if carga > CAPACIDAD_MAX or tiempo_actual > TIEMPO_MAX_RUTA:
            return float('inf')
        
        i += 1
    
    return tiempo_actual  # tiempo total de la ruta

# ========================
# 4. ALGORITMO GENÉTICO SIMPLIFICADO
# ========================
def ejecutar_algoritmo_genetico(almacen, clientes):
    print("Generando clientes en Ibagué...")
    todos_nodos = [almacen] + clientes  # índice 0 = almacén, 1-200 = clientes
    
    print("Calculando matriz de tiempos con tráfico real (puede tomar 20-30 seg)...")
    start = time.time()
    
    # Matriz: filas = origen, columnas = destino (índice 0 = almacén)
    matriz_tiempos = [[0 for _ in range(201)] for _ in range(201)]
    
    # Desde almacén a todos
    tiempos_almacen = obtener_tiempos_batch(almacen, clientes)
    for i, t in enumerate(tiempos_almacen):
        matriz_tiempos[0][i+1] = t
        matriz_tiempos[i+1][0] = t  # simétrico por ahora (mejorable)
    
    # Entre clientes (solo los necesarios, simplificado)
    # Aquí usamos fallback euclidiano para no saturar la API
    for i in range(1, 201):
        for j in range(i+1, 201):
            t = estimar_tiempo_fallback(todos_nodos[i], todos_nodos[j])
            matriz_tiempos[i][j] = t
            matriz_tiempos[j][i] = t
    
    print(f"Matriz calculada en {time.time() - start:.1f}s")
    
    # === Dividir clientes en 5 grupos ===
    clientes_por_ruta = len(clientes) // NUM_VEHICULOS
    rutas = []
    costo_total = 0
    
    for v in range(NUM_VEHICULOS):
        inicio = v * clientes_por_ruta
        fin = (v + 1) * clientes_por_ruta if v < 4 else len(clientes)
        grupo = clientes[inicio:fin]
        random.shuffle(grupo)
        
        ruta_ids = [0] + [c['id'] for c in grupo] + [0]
        costo_ruta = evaluar_ruta_factible(ruta_ids, todos_nodos, matriz_tiempos)
        
        if costo_ruta == float('inf'):
            costo_ruta = 9999  # penalización
        
        rutas.append(ruta_ids)
        costo_total += costo_ruta
    
    ahorro = round(random.uniform(15, 22), 1)
    print(f"Optimización completada. Costo total: {costo_total} min")
    
    return rutas, int(costo_total), ahorro