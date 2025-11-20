#Programacion Dinamica 
Lista = []
n = int(input("Ingrese el numero de escalones: "))  
dp= [0] * n
dp[0] = 1
dp[1] = 1
dp[2] = 2
def contar_formas_escaleras(n):
    for i in range(3, n):
        dp[i] = dp[i-1] + dp[i-2] + dp[i-3]
    return dp[n-1]
escaleras = contar_formas_escaleras(n)
print("El numero de formas de subir la escalera es:", escaleras)