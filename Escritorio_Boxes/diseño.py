import socket
import time
import math
import random
from datetime import datetime # <--- IMPORTANTE: Nueva librería

UDP_IP = "127.0.0.1"
UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("TELEMETRÍA SIMULADA - ENVÍO DE DATOS")
print("    Formato: ECT | RPM | BATT | SPEED | HH:MM:SS")

t = 0
while True:
    # Generación de datos (Igual que antes)
    ect = 85 + (5 * math.sin(t / 5.0)) + random.uniform(-0.2, 0.2)
    rpm = 3000 + (1000 * math.sin(t / 2.0))
    batt = 13.8 + random.uniform(-0.1, 0.1)
    speed = 90 + (30 * math.sin(t / 3.0)) 
    
    # --- CAMBIO AQUÍ: OBTENER HORA REAL ---
    # Obtenemos hora actual y la convertimos a texto
    hora_real = datetime.now().strftime("%H:%M:%S.%f")[:-3] # Hora con milisegundos
    
    # Mensaje con la hora legible al final
    mensaje = f"{ect:.2f}|{int(rpm)}|{batt:.2f}|{int(speed)}|{hora_real}"
    
    sock.sendto(mensaje.encode(), (UDP_IP, UDP_PORT))
    
    print(f"TX: {mensaje}") 
    
    t += 0.1
    time.sleep(0.002)