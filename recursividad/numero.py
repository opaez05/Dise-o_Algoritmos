def suma_digitos_recursiva(n):
    #termina cuando el número es 0.
    if n == 0:
        return 0
    else:
        ultimo_digito = n % 10
        numero_restante = n // 10
        
        return ultimo_digito + suma_digitos_recursiva(numero_restante)

while True:
    try:
        numero_ingresado = int(input("Ingrese un numero: "))
        
        if numero_ingresado <0:
            raise ValueError("El numero debe ser positivo.")

    except ValueError as e:
        print("Ingrese solo numeros enteros positivos.")
        print(e)
    else:
        #Se llama la funcion 
        resultado = suma_digitos_recursiva(numero_ingresado)
        print(f"El numero ingresado fue: {numero_ingresado}")
        print(f"La suma fue: {resultado}")
        
        break