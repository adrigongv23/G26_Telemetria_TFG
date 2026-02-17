import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime              

# --- CONFIGURACIÓN ---
UDP_IP = "0.0.0.0"  # Escuchamos en Todas las interfaces posibles (WiFi, Ethernet...)
UDP_PORT = 4210     # Mismo puerto que usamos para la ESP32
MAX_PUNTOS = 200    # Vamos a mostrar en la gráfica los últimos 200 datos

# Cola de datos
data_ect = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)

#Ocultamos estos valores ya que por el momento únicamente vamos a trabajar con la temperatura
#data_rpm = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)
#data_bat = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)

# Configuración del socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# --- DISEÑO GRÁFICO ---
plt.style.use('dark_background')
fig, ax1 = plt.subplots(figsize=(10, 6)) # Usaremos una única ventana grande

# Título principal + RELOJ
fig.canvas.manager.set_window_title('G26 Telemetry - Monitor de Temperatura')
fig.suptitle('GADES TELEMETRY SYSTEM', fontsize=16, fontweight='bold', color='white')

# Reloj en la esquina superior derecha
txt_reloj = fig.text(0.85, 0.95, '--:--:--', fontsize=12, color='white', fontweight='bold')

# Configuración de la línea (empieza en blanco pero cambiará)
line_ect, = ax1.plot([], [], color='white', lw=3)
ax1.set_ylabel('Temperatura (°C)', fontsize=14)
ax1.set_ylim(0, 130) # Rango de temperatura (0 a 130 grados)
ax1.grid(True, alpha=0.3, linestyle='--')

# Caja de texto con el valor actual
props = dict(boxstyle='round', facecolor='black', alpha=0.8, edgecolor='white')
txt_ect = ax1.text(0.02, 0.90, 'ESPERANDO...', transform=ax1.transAxes, 
                   fontsize=16, color='white', fontweight='bold', bbox=props)

def get_color(temp):
    if temp > 105:
        return '#ff3333' # ROJO (Peligro)
    elif temp >= 95:
        return '#ffff33' # AMARILLO (Precaución)
    elif temp >= 65:
        return '#33ff33' # VERDE (Ok)
    else:
        return '#33ffff' # AZUL (Frío)

def update(frame):
    # 1. Actualizar el Reloj con la hora del PC
    ahora = datetime.now().strftime("%H:%M:%S")
    txt_reloj.set_text(f"HORA: {ahora}")
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode('utf-8')
            # partes = msg.split('|') 
            
            try: 
                val_ect = float(msg) # Convertimos texto a número 

                data_ect.append(val_ect) # Guardamos el dato
                color_actual = get_color(val_ect) # Para que el valor cambie de color segun la temepratura

                txt_ect.set_text(f"TEMP: {val_ect: .1f} °C")
                txt_ect.set_color(color_actual)
            
            except ValueError: 
                print(f"Error de formato: {msg}")

    except BlockingIOError:
        pass
    except Exception as e:
        print(f"Error: {e}")

    # Actualizamos la línea gráfica
    x_range = range(len(data_ect))
    line_ect.set_data(x_range, data_ect)
    ax1.set_xlim(0, max(len(data_ect), 1))
    
    return line_ect, txt_ect, txt_reloj

ani = animation.FuncAnimation(fig, update, interval=20, blit=False, cache_frame_data=False)
plt.show()