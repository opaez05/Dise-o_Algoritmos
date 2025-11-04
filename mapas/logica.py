# logica.py

import requests
import json
from datetime import timedelta
# Se asume que config.py está en la misma carpeta
from config import API_KEY 

API_BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'
DIRECTIONS_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
STATIC_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/staticmap'

class DistanceCalculator:
    def __init__(self, api_key=None):
        """Constructor que inicializa la clave API y valida."""
        self.api_key = api_key if api_key else API_KEY 
        if not self.api_key or self.api_key == "TU_CLAVE_API_AQUI":
            raise ValueError("La clave API no está configurada en config.py.")

    def obtener_ruta_detallada(self, origen, destino, waypoints, modo='driving'):
        """
        Llama a Directions API para obtener la ruta óptima, duración, y polilínea.
        """
        
        # Las paradas intermedias se pasan separadas por el símbolo '|'
        waypoints_str = '|'.join(waypoints)
        
        params = {
            'origin': origen,
            'destination': destino,
            # Añade 'optimize:true' para obtener la secuencia más rápida entre los waypoints
            'waypoints': f"optimize:true|{waypoints_str}" if waypoints else waypoints_str,
            'mode': modo,
            'key': self.api_key
        }
        
        try:
            response = requests.get(DIRECTIONS_API_URL, params=params, timeout=10)
            response.raise_for_status() 
            data = response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de Conexión: Verifica tu Internet, Firewall o DNS (NameResolutionError). Detalle: {e}"
            raise ConnectionError(error_msg)

        if data.get('status') != 'OK' or not data.get('routes'):
            error_message = data.get('error_message', f"Estado de Directions API: {data.get('status')}")
            raise RuntimeError(f"Error al obtener la ruta: {error_message}. Revisa la clave o los puntos de ruta.")
        
        # La ruta más rápida/sugerida es la primera (index 0) debido a 'optimize:true'
        ruta = data['routes'][0]
        
        # Obtener el resumen de distancia y duración de la ruta completa
        distancia_total = sum(leg['distance']['value'] for leg in ruta['legs'])
        duracion_total = sum(leg['duration']['value'] for leg in ruta['legs'])
        
        # Retorna la polilínea y los datos de la ruta
        return {
            'polyline': ruta['overview_polyline']['points'],
            'distance_km': round(distancia_total / 1000, 2),
            'duration_sec': duracion_total,
            'summary_text': f"Ruta óptima sugerida: {ruta['summary']}"
        }

    def generar_mapa_url(self, polyline, size='550x350'):
        """Genera la URL de Maps Static API para obtener la imagen del mapa."""
        
        # Estilo de la ruta: rojo, ancho 5 píxeles, polilínea codificada
        path_style = f"color:0xff0000ff|weight:5|enc:{polyline}"
        
        params = {
            'size': size,
            'path': path_style,
            'key': self.api_key,
            'maptype': 'roadmap',
            'format': 'png'
            # El mapa Static API centrará la vista automáticamente basándose en la polilínea
        }
        
        # Construye la URL final de la imagen
        url = requests.Request('GET', STATIC_MAPS_API_URL, params=params).prepare().url
        return url

    def calcular_y_mapear_ruta(self, ciudades, modo='driving'):
        """Función principal que combina cálculo y mapa."""
        
        origen = ciudades[0]
        destino = ciudades[-1]
        waypoints = ciudades[1:-1] # Paradas intermedias
        
        # 1. Obtener datos de la ruta (incluye la sugerencia más rápida)
        ruta_data = self.obtener_ruta_detallada(origen, destino, waypoints, modo)
        
        # 2. Generar la URL del mapa con esa polilínea
        mapa_url = self.generar_mapa_url(ruta_data['polyline'])
        
        # 3. Formatear el resultado final
        tiempo_fmt = self._formatear_tiempo(ruta_data['duration_sec'])
        
        informe = f"✅ **Ruta Sugerida (Más Rápida):**\n"
        informe += f"Ruta: {origen} → ... → {destino}\n"
        informe += f"{ruta_data['summary_text']}\n"
        informe += f"Distancia Total: **{ruta_data['distance_km']} km**\n"
        informe += f"Duración Total Estimada: **{tiempo_fmt}**"
        
        return informe, mapa_url

    def _formatear_tiempo(self, segundos):
        """Convierte segundos a formato legible (días, horas, minutos) usando timedelta."""
        
        td = timedelta(seconds=segundos)
        dias = td.days
        horas = td.seconds // 3600
        minutos = (td.seconds // 60) % 60
        
        partes = []
        if dias > 0:
            partes.append(f"{dias} día{'s' if dias > 1 else ''}")
        if horas > 0:
            partes.append(f"{horas} hora{'s' if horas > 1 else ''}")
        if minutos > 0:
            partes.append(f"{minutos} minuto{'s' if minutos > 1 else ''}")
            
        return ", ".join(partes) if partes else "0 minutos"