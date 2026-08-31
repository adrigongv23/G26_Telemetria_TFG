import numpy as np
import pandas as pd

COLUMNA_TIEMPO = 'tiempo_s'

# Columnas que no son canales de telemetría (índice, reloj, tiempo ya usado como eje X)
# o sensores que no están instalados en el coche.
COLUMNAS_EXCLUIDAS = {'n_muestra', 'hora', COLUMNA_TIEMPO, 'freno_tra'}

# Etiqueta y unidad por canal conocido. Un canal que no esté aquí se muestra
# igualmente (con su nombre de columna tal cual y sin unidad) para que un CSV
# con canales nuevos no rompa el procesado.
CANALES = {
    'ect': {'label': 'Temperatura motor (ECT)', 'unidad': '°C'},
    'rpm': {'label': 'RPM', 'unidad': 'rpm'},
    'velocidad': {'label': 'Velocidad', 'unidad': 'km/h'},
    'vbatt': {'label': 'Batería', 'unidad': 'V'},
    'tps': {'label': 'Acelerador', 'unidad': '%'},
    'freno_del': {'label': 'Freno', 'unidad': '%'},
    'pcomb': {'label': 'Presión de combustible', 'unidad': 'bar'},
    'taceite': {'label': 'Temperatura de aceite', 'unidad': '°C'},
    'paceite': {'label': 'Presión de aceite', 'unidad': 'bar'},
    'map': {'label': 'Presión Absoluta del Colector (MAP)', 'unidad': 'kPa'},
    'lambda': {'label': 'Lambda (AFR)', 'unidad': 'λ'},
}

# Canales que se combinan en el panel "Pedales" (acelerador + freno, misma escala 0-100%)
# en vez de tener cada uno su propio panel, igual que ya se muestra en Escritorio_Boxes.
GRUPO_PEDALES = ['tps', 'freno_del']

# Orden preferido del resto de paneles individuales.
ORDEN_PANELES = ['ect', 'rpm', 'velocidad', 'vbatt', 'pcomb', 'taceite', 'paceite', 'map', 'lambda']

MAX_PUNTOS_POR_DEFECTO = 5000


def _info_canal(columna):
    return CANALES.get(columna, {'label': columna, 'unidad': ''})


def _sin_nan(valores):
    """NaN no es JSON válido (json_script generaría un 'NaN' literal que
    JSON.parse rechaza en el navegador) — lo convertimos al None de Python,
    que serializa como null y Plotly interpreta como hueco en la línea."""
    return [None if v != v else v for v in valores]


def _downsample_minmax(x, y, max_puntos):
    """x, y: arrays alineados por posición (misma longitud). Reduce la serie
    a como mucho max_puntos, conservando el mínimo y el máximo de cada bloque
    para no perder picos/caídas transitorias (a diferencia de coger 1 de
    cada N filas sin más). Devuelve dos listas."""
    x_vals = np.asarray(x)
    y_vals = np.asarray(y, dtype=float)
    n = len(y_vals)

    if n <= max_puntos:
        return x_vals.tolist(), y_vals.tolist()

    n_bloques = max(1, max_puntos // 2)
    tam_bloque = n / n_bloques
    x_out, y_out = [], []

    for i in range(n_bloques):
        inicio = int(i * tam_bloque)
        fin = int((i + 1) * tam_bloque) if i < n_bloques - 1 else n
        if inicio >= fin:
            continue

        bloque_y = y_vals[inicio:fin]
        if np.all(np.isnan(bloque_y)):
            continue

        pos_min = int(np.nanargmin(bloque_y))
        pos_max = int(np.nanargmax(bloque_y))

        for pos in sorted({pos_min, pos_max}):
            idx = inicio + pos
            x_out.append(float(x_vals[idx]))
            y_out.append(float(y_vals[idx]))

    return x_out, y_out


class TelemetriaCSVError(Exception):
    pass


def procesar_csv(ruta_archivo, max_puntos=MAX_PUNTOS_POR_DEFECTO):
    """Lee un CSV de telemetría y devuelve la estructura lista para pintar
    con Plotly.js: una lista de paneles, cada uno con una o varias series."""
    try:
        df = pd.read_csv(ruta_archivo)
    except Exception as exc:
        raise TelemetriaCSVError(f'No se ha podido leer el archivo CSV: {exc}') from exc

    if df.empty:
        raise TelemetriaCSVError('El archivo CSV no contiene ninguna fila de datos.')

    if COLUMNA_TIEMPO in df.columns:
        tiempo = pd.to_numeric(df[COLUMNA_TIEMPO], errors='coerce')
    else:
        tiempo = pd.Series(range(len(df)), index=df.index)

    canales_disponibles = [c for c in df.columns if c not in COLUMNAS_EXCLUIDAS]

    series_por_canal = {}
    canales_sin_datos = []
    for columna in canales_disponibles:
        valores = pd.to_numeric(df[columna], errors='coerce')
        if valores.notna().sum() == 0:
            canales_sin_datos.append(columna)
            continue
        series_por_canal[columna] = valores

    paneles = []

    canales_pedales = [c for c in GRUPO_PEDALES if c in series_por_canal]
    if canales_pedales:
        series = []
        for columna in canales_pedales:
            x, y = _downsample_minmax(tiempo.tolist(), series_por_canal[columna].tolist(), max_puntos)
            series.append({
                'columna': columna,
                'label': _info_canal(columna)['label'],
                'x': x,
                'y': _sin_nan(y),
            })
        paneles.append({
            'id': 'pedales',
            'titulo': 'Pedales',
            'unidad': '%',
            'series': series,
        })

    resto = [c for c in canales_disponibles if c in series_por_canal and c not in GRUPO_PEDALES]
    resto_ordenado = sorted(resto, key=lambda c: ORDEN_PANELES.index(c) if c in ORDEN_PANELES else len(ORDEN_PANELES))

    for columna in resto_ordenado:
        info = _info_canal(columna)
        x, y = _downsample_minmax(tiempo.tolist(), series_por_canal[columna].tolist(), max_puntos)
        paneles.append({
            'id': columna,
            'titulo': info['label'],
            'unidad': info['unidad'],
            'series': [{'columna': columna, 'label': info['label'], 'x': x, 'y': _sin_nan(y)}],
        })

    return {
        'paneles': paneles,
        'canales_sin_datos': [_info_canal(c)['label'] for c in canales_sin_datos],
        'num_filas': len(df),
        'downsampled': len(df) > max_puntos,
    }


def canales_para_variables(ruta_archivo):
    """Lista simple de (nombre_columna, unidad) con datos reales, para crear
    los registros Variable al subir el CSV."""
    try:
        df = pd.read_csv(ruta_archivo)
    except Exception:
        return []

    resultado = []
    for columna in df.columns:
        if columna in COLUMNAS_EXCLUIDAS:
            continue
        valores = pd.to_numeric(df[columna], errors='coerce')
        if valores.notna().sum() == 0:
            continue
        info = _info_canal(columna)
        resultado.append((columna, info['label'], info['unidad']))

    return resultado
