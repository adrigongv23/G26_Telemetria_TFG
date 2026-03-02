import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from collections import deque
import time 
import numpy as np
from datetime import datetime              

# --- CONFIGURACIÓN ---
UDP_IP = "0.0.0.0"  # Escuchamos en Todas las interfaces posibles (WiFi, Ethernet...)
UDP_PORT = 4210     # Mismo puerto que usamos para la ESP32
TIMEOUT_SEG = 1.5   # Para ver si existe desconexión

# --- CONFIGURACIÓN VISUAL ---
MAX_PUNTOS = 200    # Vamos a mostrar en la gráfica los últimos 200 datos
MAX_RPM = 15000     # Límite máximo del velocímetro
MIN_BATT = 0.0      # Mínimo voltaje para la gráfica
MAX_BATT = 17.0     # Máximo voltaje para la gráfica

# Cola de datos
data_ect = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)
# Para controlar si existe una desconexión de envio de paquetes
ultimo_tiempo_dato = time.time()

# Configuración del socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# --- DISEÑO DEL DASHBOARD ---
plt.style.use('dark_background')
fig = plt.figure(figsize=(12, 8))

# Título principal + RELOJ
fig.canvas.manager.set_window_title('G26 Telemetry - Monitor de Temperatura')
fig.suptitle('GADES TELEMETRY SYSTEM', fontsize=16, fontweight='bold', color='white')

# Reloj en la esquina superior derecha
txt_reloj = fig.text(0.85, 0.95, '--:--:--', fontsize=12, color='white', fontweight='bold')

# Sistema de Grid (2 filas, 2 columnas)
gs = GridSpec(2, 2, height_ratios=[1, 1])

# --- 1. GRÁFICA DE TEMPERATURA  ---
ax_ect = fig.add_subplot(gs[0, :])
line_ect, = ax_ect.plot([], [], color='white', lw=3)
ax_ect.set_ylabel('Temperatura (°C)', fontsize=14)
ax_ect.set_ylim(0, 130) # Rango de temperatura (0 a 130 grados)
ax_ect.grid(True, alpha=0.3, linestyle='--')

# Caja de texto con el valor actual
props = dict(boxstyle='round', facecolor='black', alpha=0.8, edgecolor='white')
txt_ect = ax_ect.text(0.02, 0.85, 'ESPERANDO...', transform=ax_ect.transAxes, 
                   fontsize=16, color='white', fontweight='bold', bbox=props)

# FUNCIÓN PARA EL COLOR DE LA TEMPERATURA
def get_color(temp):
    if temp > 105:
        return '#ff3333' # ROJO (Peligro)
    elif temp >= 95:
        return '#ffff33' # AMARILLO (Precaución)
    elif temp >= 65:
        return '#33ff33' # VERDE (Ok)
    else:
        return '#33ffff' # AZUL (Frío)

# --- 2. VELOCÍMETRO RPM (Fila inferior, Izquierda) ---
ax_rpm = fig.add_subplot(gs[1, 0], projection='polar')
ax_rpm.set_thetamin(0)
ax_rpm.set_thetamax(180)
ax_rpm.set_theta_zero_location("W") # El 0 empieza a la izquierda
ax_rpm.set_theta_direction(-1)      # Gira en sentido horario
ax_rpm.set_xticklabels([])          # Quitar números del borde
ax_rpm.set_yticklabels([])
ax_rpm.grid(False)

# Arco gris de fondo
theta_bg = np.linspace(0, np.pi, 100)
ax_rpm.plot(theta_bg, np.ones_like(theta_bg), color='#444444', lw=8)

# Arco rojo de límite (12000 a 15000 RPM)
theta_red = np.linspace((12000/MAX_RPM)*np.pi, np.pi, 50)
ax_rpm.plot(theta_red, np.ones_like(theta_red), color='red', lw=8)

# Aguja y texto RPM
needle, = ax_rpm.plot([0, 0], [0, 0.9], color='white', lw=4)
txt_rpm = ax_rpm.text(0.5, 0.1, 'RPM: --', transform=ax_rpm.transAxes, ha='center', fontsize=20, fontweight='bold')

# --- 3. BARRA DE BATERÍA (Fila inferior, Derecha) ---
ax_batt = fig.add_subplot(gs[1, 1])
ax_batt.set_xlim(MIN_BATT, MAX_BATT)
ax_batt.set_ylim(-0.5, 0.5)
ax_batt.set_yticks([]) # Quitar eje Y
ax_batt.set_xlabel('Voltaje (V)', fontsize=12)

# Contorno de la batería
borde = plt.Rectangle((MIN_BATT, -0.3), MAX_BATT-MIN_BATT, 0.6, fill=False, edgecolor='white', lw=2)
ax_batt.add_patch(borde)

# Barra interior SIEMPRE NARANJA
bar_batt = ax_batt.barh(0, 0, left=MIN_BATT, height=0.5, color='orange', align='center')[0]
txt_batt = ax_batt.text(0.5, 0.8, 'BATT: -- V', transform=ax_batt.transAxes, ha='center', fontsize=18, fontweight='bold')


def update(frame):
    global ultimo_tiempo_dato

    # 1. Actualizar el Reloj con la hora del PC
    ahora = datetime.now().strftime("%H:%M:%S")
    txt_reloj.set_text(f"HORA: {ahora}")
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode('utf-8')
            partes = msg.split('|') 
            
            if len(partes) == 3:
                val_ect = float(partes[0])
                val_rpm = float(partes[1])
                val_batt = float(partes[2])
                
                ultimo_tiempo_dato = time.time() # Reiniciar Watchdog

                # 1. Actualizar ECT
                data_ect.append(val_ect)
                txt_ect.set_text(f"ECT: {val_ect:.1f} °C")
                # APLICAMOS LA FUNCIÓN DE COLOR AQUÍ:
                txt_ect.set_color(get_color(val_ect))

                # 2. Actualizar RPM 
                val_rpm = max(0, min(MAX_RPM, val_rpm)) 
                angulo_rad = (val_rpm / MAX_RPM) * np.pi
                needle.set_data([angulo_rad, angulo_rad], [0, 0.9])
                txt_rpm.set_text(f"RPM: {int(val_rpm)}")
                
                if val_rpm > 11000:
                    txt_rpm.set_color('red')
                    needle.set_color('red')
                else:
                    txt_rpm.set_color('white')
                    needle.set_color('white')

                # 3. Actualizar Batería
                ancho = max(0, min(MAX_BATT - MIN_BATT, val_batt - MIN_BATT))
                bar_batt.set_width(ancho)
                
                # Actualizar texto y cambiar su color
                txt_batt.set_text(f"BATT: {val_batt:.1f} V")
                
                # Lógica de colores para el TEXTO de la batería
                if val_batt > 15.0:
                    txt_batt.set_color('green')
                elif val_batt > 12.0:
                    txt_batt.set_color('yellow')
                else:
                    txt_batt.set_color('red')

    except BlockingIOError:
        pass
    except Exception as e:
        pass

    # --- WATCHDOG / TIMEOUT ---
    if (time.time() - ultimo_tiempo_dato) > TIMEOUT_SEG:
        data_ect.append(0)
        txt_ect.set_text("ECT: DESCONECTADO")
        txt_ect.set_color('#555555')
        txt_rpm.set_text("RPM: 0")
        txt_rpm.set_color('#555555')
        needle.set_data([0, 0], [0, 0.9])
        needle.set_color('#555555')
        txt_batt.set_text("BATT: APAGADO")
        txt_batt.set_color('#555555')
        bar_batt.set_width(0)

    # Redibujar gráfica ECT
    line_ect.set_data(range(len(data_ect)), data_ect)
    ax_ect.set_xlim(0, max(len(data_ect), 1))

    return line_ect, txt_ect, needle, txt_rpm, bar_batt, txt_batt

# Iniciar animación
ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.tight_layout()
plt.show()