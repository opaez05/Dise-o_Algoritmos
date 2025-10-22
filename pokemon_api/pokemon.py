import requests
from typing import Dict, List, Any

def obtener_cadena_evolucion(id_cadena: int = 1) -> Dict[str, Any]:
    """
    Obtiene la cadena de evolución de la PokéAPI.
    """
    url = f"https://pokeapi.co/api/v2/evolution-chain/{id_cadena}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al obtener datos de la API: {e}")
        return {}

def construir_grafo(cadena_evolucion: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Construye el grafo de evolución usando recursión.
    """
    grafo = {}
    
    def recorrer_cadena(chain: Dict[str, Any]):
        # Obtener el nombre del Pokémon actual
        species_url = chain['species']['url']
        pokemon_nombre = species_url.split('/')[-2]  # Extrae el nombre del URL
        
        # Inicializar lista de adyacencia si no existe
        if pokemon_nombre not in grafo:
            grafo[pokemon_nombre] = []
        
        # Procesar evoluciones
        for evoluciona_en in chain.get('evolves_to', []):
            # Obtener nombre del Pokémon al que evoluciona
            siguiente_url = evoluciona_en['species']['url']
            siguiente_pokemon = siguiente_url.split('/')[-2]
            
            # Agregar arista
            grafo[pokemon_nombre].append(siguiente_pokemon)
            
            # Recursión para cadenas más profundas
            recorrer_cadena(evoluciona_en)
    
    # Iniciar recursión desde la cadena principal
    if 'chain' in cadena_evolucion:
        recorrer_cadena(cadena_evolucion['chain'])
    
    return grafo

def busqueda_binaria(lista_ordenada: List[str], objetivo: str) -> bool:
    """
    Implementa búsqueda binaria en una lista ordenada alfabéticamente.
    """
    izquierda, derecha = 0, len(lista_ordenada) - 1
    
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        pokemon_medio = lista_ordenada[medio]
        
        if pokemon_medio == objetivo:
            return True
        elif pokemon_medio < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    
    return False

def main():
    """
    Función principal que ejecuta todo el flujo.
    """
    print("🔍 Consumiendo PokéAPI - Cadena de evolución de Bulbasaur...")
    
    # Fase 1: Consumo de API y construcción del grafo
    datos = obtener_cadena_evolucion(1)
    
    if not datos:
        print("❌ No se pudieron obtener los datos de la API")
        return
    
    grafo = construir_grafo(datos)
    
    print("\n📊 Grafo de Evolución (Lista de Adyacencia):")
    for pokemon, evoluciones in grafo.items():
        evoluciones_str = ', '.join(evoluciones) if evoluciones else 'Sin evoluciones'
        print(f"  {pokemon} → {evoluciones_str}")
    
    # Fase 2: Preparar lista ordenada y búsqueda binaria
    nodos = list(grafo.keys())
    nodos_ordenados = sorted(nodos)
    
    print(f"\n🔤 Nodos ordenados: {nodos_ordenados}")
    
    # Pruebas de búsqueda binaria
    print("\n🧪 Pruebas de Búsqueda Binaria:")
    
    # Prueba 1: Pokémon que SÍ existe
    pokemon_existente = 'ivysaur'
    encontrado = busqueda_binaria(nodos_ordenados, pokemon_existente)
    print(f"  ✓ Buscando '{pokemon_existente}': {'ENCONTRADO' if encontrado else 'NO ENCONTRADO'}")
    
    # Prueba 2: Pokémon que NO existe
    pokemon_inexistente = 'charmander'
    encontrado = busqueda_binaria(nodos_ordenados, pokemon_inexistente)
    print(f"  ✗ Buscando '{pokemon_inexistente}': {'ENCONTRADO' if encontrado else 'NO ENCONTRADO'}")
    
    # Prueba adicional: Bulbasaur (debe existir)
    pokemon_base = 'bulbasaur'
    encontrado = busqueda_binaria(nodos_ordenados, pokemon_base)
    print(f"  ✓ Buscando '{pokemon_base}': {'ENCONTRADO' if encontrado else 'NO ENCONTRADO'}")
    
    # Estadísticas
    print(f"\n📈 Estadísticas:")
    print(f"  Total de Pokémon en la cadena: {len(nodos)}")
    print(f"  Tamaño de la lista ordenada: {len(nodos_ordenados)}")
    print(f"  Complejidad de búsqueda: O(log n) = O(log {len(nodos)})")

if __name__ == "__main__":
    main()