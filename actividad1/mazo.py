import random

# Programa para ordenar una baraja de cartas
# Se define el primer tipo de ordenamiento
valores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
palos = ['corazones', 'diamantes', 'tréboles', 'picas']

# creamos nuestro mazo que es una lista vacia
mazo = []

# Llenamos el mazo recorriendo las listas
for palo in palos:
    for valor in valores:
        if palo == 'corazones' or palo == 'diamantes':
            color = 'rojo'
        else:
            color = 'negro'
        # creamos la carta en tupla
        carta = (palo, valor, color)
        # metemos la carta a el mazo
        mazo.append(carta)

# usamos una libreria externa para revolver el mazo
random.shuffle(mazo)

# mostramos las cartas
print("52 cartas")
for c in mazo[:52]:
    print(c)

def ordenar_carta(mazo):
    n = len(mazo)
    for i in range(n):
        # El algoritmo de burbuja se optimiza al reducir la comparación con cada pasada.
        for j in range(0, n - i - 1):
            # Extraemos el valor de la carta actual y la siguiente.
            # Los valores de las cartas están en el índice 1 de la tupla.
            valor_actual = mazo[j][1]
            valor_siguiente = mazo[j + 1][1]

            # Comparamos primero el valor numérico.
            if valor_actual > valor_siguiente:
                mazo[j], mazo[j + 1] = mazo[j + 1], mazo[j]
            # Si los valores son iguales, comparamos por el palo (índice 0).
            # Para comparar los palos, necesitamos un orden definido.
            # Creamos un diccionario para asignar un valor numérico a cada palo.
            palo_orden = {'corazones': 1, 'diamantes': 2, 'tréboles': 3, 'picas': 4}
            
            palo_actual = mazo[j][0]
            palo_siguiente = mazo[j+1][0]
            
            if valor_actual == valor_siguiente and palo_orden[palo_actual] > palo_orden[palo_siguiente]:
                 mazo[j], mazo[j+1] = mazo[j+1], mazo[j]

    return mazo

print("\nCartas ordenadas")
for c in ordenar_carta(mazo):
    print(c)