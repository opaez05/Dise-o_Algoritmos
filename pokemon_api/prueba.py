import requests

def construir_grafo(chain, grafo=None):
    if grafo is None:
        grafo = {}
    species_name = chain['species']['name']
    evolves_to = chain['evolves_to']
    grafo[species_name] = [evo['species']['name'] for evo in evolves_to]
    for evo in evolves_to:
        construir_grafo(evo, grafo)
    return grafo

def busqueda_binaria(lista_ordenada, objetivo):
    izquierda = 0
    derecha = len(lista_ordenada) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if lista_ordenada[medio] == objetivo:
            return True
        elif lista_ordenada[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return False

# Fase 1: Consumo de la API y Construcción del Grafo
url = 'https://pokeapi.co/api/v2/evolution-chain/1/'
response = requests.get(url)
data = response.json()
grafo = construir_grafo(data['chain'])

# Fase 2: Implementación de la Búsqueda Binaria
nodos_ordenados = sorted(grafo.keys())

# Prueba de Concepto
print("Grafo construido:", grafo)
print("Nodos ordenados:", nodos_ordenados)
print("Búsqueda de 'ivysaur':", busqueda_binaria(nodos_ordenados, 'ivysaur'))  # Debería ser True
print("Búsqueda de 'charmander':", busqueda_binaria(nodos_ordenados, 'charmander'))  # Debería ser False