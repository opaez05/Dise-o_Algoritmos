import random
#Programa para ordenar una baraja de cartas
#Se define el primer tipo de ordenamiento 
valores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
palos = ['corazones', 'diamantes', 'tréboles', 'picas']

#creamos nuestro mazo que es una lista vacia
mazo = []

#Llenamos el mazo recorriendo las listas
for palo in palos:
    for valor in valores:
        if palo == 'corazones' or palo == 'diamantes':
            color = 'rojo'
        else:
            color = 'negro'
        #creamos la carta en tupla
        carta = (palo, valor, color)
        #metemos la carta a el mazo
        mazo.append(carta)

#usamos una libreria externa para revolver el mazo 
random.shuffle(mazo)

#mostramos las cartas 
print("52 cartas")
for c in mazo[:52]:
    print(c)