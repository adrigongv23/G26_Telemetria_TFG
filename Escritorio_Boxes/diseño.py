import socket
import time
import math
import random

# --- CONFIGURACIÓN ---
UDP_IP = "127.0.0.1" 
UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"--- SIMULADOR DE COCHE G26 ---")
print(f"Enviando datos falsos a {UDP_IP}:{UDP_PORT}")

t = 0
while True:
    # Generar una temperatura que sube y baja mucho para probar todos los colores
    # Oscilará entre 40ºC y 120ºC
    ect = 80 + (40 * math.sin(t / 10.0)) + random.uniform(-0.5, 0.5)
    
    # Enviar solo el número
    mensaje = f"{ect:.2f}"
    
    sock.sendto(mensaje.encode(), (UDP_IP, UDP_PORT))
    
    print(f"Simulando: {mensaje} °C") 
    
    t += 0.1
    time.sleep(0.05)