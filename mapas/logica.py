# logica.py

import requests
import json
from datetime import timedelta
# Se asume que config.py está en la misma carpeta
from config import API_KEY 

API_BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'

class DistanceCalculator:
    def __init__(self, api_key=None):
        """Constructor que inicializa la clave API."""
        self.api_key = api_key if api_key else API_KEY 
        if not self.api_key or self.api_key == "TU_CLAVE_API_AQUI":
             # Lanza una excepción si la clave no está configurada
            raise ValueError("La clave API no está configurada en config.py.")

    def obtener_distancias_multiples(self, origenes, destinos, modo='driving'):
        """Obtiene las distancias y duraciones para múltiples orígenes y destinos."""
        
        origenes_str = '|'.join(origenes)
        destinos_str = '|'.join(destinos)
        
        params = {
            'origins': origenes_str,
            'destinations': destinos_str,
            'mode': modo,
            'units': 'metric',
            'key': self.api_key
        }
        
        try:
            # Petición robusta con timeout
            response = requests.get(API_BASE_URL, params=params, timeout=10)
            response.raise_for_status() # Lanza HTTPError para 4xx/5xx
            data = response.json()
            
        except requests.exceptions.RequestException as e:
            # 🚨 Captura el error de conexión/DNS/Timeout 🚨
            error_msg = f"Error de Conexión: Verifica tu Internet, Firewall o DNS. Detalle: {e}"
            raise ConnectionError(error_msg)

        # Comprobación del estado de la API (Cuota, Clave Inválida, etc.)
        api_status = data.get('status')
        if api_status != 'OK':
            error_message = data.get('error_message', f"Estado de la API: {api_status}")
            if 'OVER_QUERY_LIMIT' in api_status:
                error_message += ". Has excedido tu cuota API."
            elif 'INVALID_REQUEST' in api_status:
                 error_message += ". Revisa tu clave API."
            
            raise RuntimeError(f"Error en la API de Google Maps: {error_message}")
        
        return data

    def calcular_ruta_multiples(self, ciudades, modo='driving'):
        """Calcula la ruta secuencial: Ciudad1 -> Ciudad2, Ciudad2 -> Ciudad3, ..."""
        
        if len(ciudades) < 2:
            return "Necesitas al menos dos ciudades para definir una ruta."
        
        resultados_segmentos = []
        total_segundos = 0
        
        # El try/except grande se elimina aquí y se mueve a interfaz.py
        for i in range(len(ciudades) - 1):
            origen = [ciudades[i]]
            destino = [ciudades[i + 1]]
            
            # La función obtener_distancias_multiples lanzará la excepción si hay un problema.
            data = self.obtener_distancias_multiples(origen, destino, modo)
            element = data['rows'][0]['elements'][0]
            
            if element['status'] == 'OK':
                distancia = element['distance']['text']
                duracion_text = element['duration']['text']
                duracion_seg = element['duration']['value'] 
                
                segmento_resultado = f"Segmento {i+1} ({origen[0]} → {destino[0]}): Distancia: {distancia}, Duración: {duracion_text}"
                resultados_segmentos.append(segmento_resultado)
                total_segundos += duracion_seg
            else:
                # Si un segmento falla, lo reportamos y lanzamos un error para detener el cálculo.
                status_seg = element['status']
                error_msg = f"No se pudo calcular la ruta entre {origen[0]} y {destino[0]}. Estado: {status_seg}"
                raise ValueError(error_msg)
        
        total_tiempo_fmt = self._formatear_tiempo(total_segundos)
        
        informe = "\n".join(resultados_segmentos)
        informe += f"\n\n\n✅ **Ruta Total Calculada:**\n"
        informe += f"Ruta: {ciudades[0]} → ... → {ciudades[-1]}\n"
        informe += f"Duración Total Estimada: {total_tiempo_fmt}"

        return informe

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