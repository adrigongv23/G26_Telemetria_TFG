import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- CONFIGURACIÓN ---
UDP_IP = "0.0.0.0"
UDP_PORT = 4210
MAX_PUNTOS = 150 

data_ect = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)
data_rpm = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)
data_bat = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)
data_spd = deque([0]*MAX_PUNTOS, maxlen=MAX_PUNTOS)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# --- DISEÑO GRÁFICO ---
plt.style.use('dark_background')
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, figsize=(8, 10))

# Título principal + RELOJ
fig.suptitle('GADES TELEMETRY SYSTEM', fontsize=16, fontweight='bold', color='white')
# Creamos un texto vacío arriba a la derecha para la hora
texto_reloj = fig.text(0.85, 0.97, "--:--:--", fontsize=12, color='cyan', ha='center', fontweight='bold')

def setup_plot(ax, color, label, y_min, y_max):
    line, = ax.plot([], [], color=color, lw=2)
    ax.set_ylabel(label)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3, linestyle='--')
    props = dict(boxstyle='round', facecolor='black', alpha=0.7, edgecolor=color)
    text = ax.text(0.03, 0.85, '', transform=ax.transAxes, 
                   fontsize=14, color=color, fontweight='bold', bbox=props)
    return line, text

line_ect, txt_ect = setup_plot(ax1, '#ff3333', 'ECT (°C)', 50, 110)
line_rpm, txt_rpm = setup_plot(ax2, '#ffff33', 'RPM', 0, 5000)
line_bat, txt_bat = setup_plot(ax3, '#33ffff', 'BATT (V)', 12, 15)
line_spd, txt_spd = setup_plot(ax4, '#33ff33', 'SPEED', 0, 140)

def update(frame):
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode('utf-8')
            partes = msg.split('|')
            
            # Extraer valores numéricos
            val_ect = float(partes[0])
            val_rpm = float(partes[1])
            val_bat = float(partes[2])
            val_spd = float(partes[3])
            
            # --- EXTRAER LA HORA (Es el elemento 4) ---
            val_time = partes[4] 
            
            # Guardar datos
            data_ect.append(val_ect)
            data_rpm.append(val_rpm)
            data_bat.append(val_bat)
            data_spd.append(val_spd)
            
            # Actualizar textos gráficas
            txt_ect.set_text(f"TEMP: {val_ect:.1f} °C")
            txt_rpm.set_text(f"RPM: {int(val_rpm)}")
            txt_bat.set_text(f"BATT: {val_bat:.2f} V")
            txt_spd.set_text(f"VEL: {int(val_spd)} Km/h")
            
            # --- ACTUALIZAR EL RELOJ DE ARRIBA ---
            texto_reloj.set_text(f"{val_time}")

    except BlockingIOError:
        pass
    except Exception as e:
        print(f"Error: {e}")

    x_range = range(len(data_ect))
    line_ect.set_data(x_range, data_ect)
    line_rpm.set_data(x_range, data_rpm)
    line_bat.set_data(x_range, data_bat)
    line_spd.set_data(x_range, data_spd)
    
    ax1.set_xlim(0, len(data_ect))
    
    return line_ect, line_rpm, line_bat, line_spd, txt_ect, txt_rpm, txt_bat, txt_spd, texto_reloj

plt.tight_layout(rect=[0, 0, 1, 0.96]) # Dejar hueco arriba para el reloj
ani = animation.FuncAnimation(fig, update, interval=20, blit=False, cache_frame_data=False)
plt.show()