import socket
import time
import math
import random

# --- CONFIGURACIÓN DE RED ---
UDP_IP = "127.0.0.1"  # Enviamos a nuestro propio PC (Localhost)
UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("--- SIMULADOR G26 INICIADO ---")
print("Formato de envío: ECT | RPM | BATT")
print("Simulando batería bajando de 20V a 0V...")

t = 0
batt = 20.0  # La batería empieza al máximo

while True:
    # 1. Simular Temperatura (ECT) - Oscila entre 80 y 90
    ect = 85 + (5 * math.sin(t / 5.0)) + random.uniform(-0.5, 0.5)
    
    # 2. Simular RPM - Acelerones entre 0 y 15000 RPM
    # Usamos valor absoluto del seno para simular que pisa el acelerador y suelta
    rpm = abs(15000 * math.sin(t / 2.0)) 
    
    # 3. Simular Batería - Baja progresivamente
    batt -= 0.05  # Restamos un poco de voltaje en cada ciclo
    if batt < 0:
        batt = 20.0  # Si llega a 0, reiniciamos a 20V para que el test continúe
        
    # 4. Empaquetar el mensaje (3 datos separados por '|')
    mensaje = f"{ect:.1f}|{int(rpm)}|{batt:.1f}"
    
    # 5. Enviar por UDP
    sock.sendto(mensaje.encode('utf-8'), (UDP_IP, UDP_PORT))
    
    # Imprimir en consola para confirmar visualmente
    print(f"Enviando -> {mensaje}")
    
    t += 0.1
    time.sleep(0.05) # Espera 50 milisegundos (20 veces por segundo)