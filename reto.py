#importamos la libreria que vamos a utilizar
import requests
#Hacemos una solicitud GET a el sitio web 
url_api = "https://restcountries.com/v3.1/region/europe"
#Realizamos la solicitud GET 
response = requests.get(url_api)

if response.status_code == 200:
    print("La solicitud fue exitosa")
else:
    print("La solicitud falló")
#guardamos los datos en un archivo json
paises = response.json()
#transformamos los datos a una lista mas simple
lista_paises = []
for pais in paises:
    nombre = pais['name']['common']
    url_mapa = pais['maps']['googleMaps']
    lista_paises.append((nombre.lower(),url_mapa))

#se usa el algoritmo de ordenamiento burbuja
def bubble_sort(lista):
    n = len(lista)
    for i in range(n):
        for j in range(0, n-i-1):
            if lista[j][0] >lista[j+1][0]: #se compara por el nombre 
                lista[j], lista[j+1] = lista[j+1], lista[j]
    return lista
    
#ordenamos la lista 
lista_paises = bubble_sort(lista_paises)
print(lista_paises)

#Se hace la busqueda lineal
def busqueda_lineal(lista, objetivo):
    objetivo = objetivo.lower()
    for nombre, url in lista:
        if nombre == objetivo:
            return nombre, url
    return None
#Se hace la busqueda binaria
def busqueda_binaria(Lista, objetivo):
    izquierda = 0
    derecha = len(Lista) - 1
    objetivo = objetivo.lower()
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        nombre, url = Lista[medio]
        if nombre == objetivo:
            return nombre, url
        elif nombre < objetivo:
            izquierda = medio + 1  
        else:
            derecha = medio - 1    
    return None

try:
    #menu de seleccion
    print("Seleccione el método de búsqueda:")
    print("1. Búsqueda Lineal")
    print("2. Búsqueda Binaria")
    opcion = int(input("Ingrese el número de la opción deseada (1 o 2): ") )
except:
    print("Ocurrió un error al seleccionar el método de búsqueda.")
else:
    try:
        pais_buscado = input("Ingrese el nombre del país que desea buscar: ")
    except:
        print("Ocurrió un error al ingresar el nombre del país.")
    else:
        if opcion == 1:
            resultado = busqueda_lineal(lista_paises, pais_buscado)
        elif opcion == 2:
            resultado = busqueda_binaria(lista_paises, pais_buscado)
        else:
            resultado = None

        if resultado:
            print(f"País encontrado: {resultado[0].title()}")
            print(f"URL del mapa: {resultado[1]}")
        else:
            print("País no encontrado")