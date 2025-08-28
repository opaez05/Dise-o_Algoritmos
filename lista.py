numeros = [1,2,3,4,5,6,7,8,9,10]
try:   
    usuario = int(input("DIGITE UN NUMERO DEL 1-10: "))
except:
    print("ERROR  NO SEA BRUTO ES UN NUMERO")
else:
    for i in range(len(numeros)):
        if usuario == numeros[i]:
            print("NUMERO ENCONTRADO")
        else:
            print("NUMERO NO ENCONTRADO")
