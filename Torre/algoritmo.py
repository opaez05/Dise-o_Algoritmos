import tkinter as tk
from tkinter import messagebox

def hanoi(n, origen, auxiliar, destino, salida):
    if n == 1:
        salida.insert(tk.END, f"Mover disco 1 de {origen} -> {destino}\n")
        return
    hanoi(n - 1, origen, destino, auxiliar, salida)
    salida.insert(tk.END, f"Mover disco {n} de {origen} -> {destino}\n")
    hanoi(n - 1, auxiliar, origen, destino, salida)

def resolver():
    # limpiar la caja de texto
    salida.delete("1.0", tk.END)  
    try:
        discos = int(entry_discos.get())
        if discos <= 0:
            raise ValueError
        hanoi(discos, "A", "B", "C", salida)
    except ValueError:
        messagebox.showerror("Error", "Ingresa un número entero positivo")

# Ventana principal
root = tk.Tk()
root.title("Torre de Hanoi")

tk.Label(root, text="Número de discos:").pack(pady=5)
entry_discos = tk.Entry(root)
entry_discos.pack(pady=5)

btn = tk.Button(root, text="Resolver", command=resolver)
btn.pack(pady=5)

salida = tk.Text(root, width=40, height=15)
salida.pack(padx=10, pady=10)

root.mainloop()
