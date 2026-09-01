import io
import math

from django.test import SimpleTestCase

from .telemetry_parser import (
    TelemetriaCSVError,
    _downsample_minmax,
    _sin_nan,
    canales_para_variables,
    procesar_csv,
)

CSV_COMPLETO = """n_muestra,hora,tiempo_s,ect,rpm,tps,freno_del,freno_tra,vbatt,suspension_del,sensor_roto
1,10:00:00,0.0,85,3000,20,0,0,13.8,5.1,NA
2,10:00:01,0.1,86,3200,25,0,0,13.7,5.2,NA
3,10:00:02,0.2,87,3400,30,5,0,13.6,5.3,NA
"""


class SinNanTests(SimpleTestCase):
    def test_convierte_nan_a_none(self):
        self.assertEqual(_sin_nan([1.0, float('nan'), 3.5]), [1.0, None, 3.5])

    def test_no_toca_valores_normales(self):
        self.assertEqual(_sin_nan([0, -1.2, 100]), [0, -1.2, 100])


class DownsampleMinmaxTests(SimpleTestCase):
    def test_por_debajo_del_limite_no_recorta(self):
        x = [0, 1, 2, 3, 4]
        y = [10, 20, 5, 30, 15]
        x_out, y_out = _downsample_minmax(x, y, max_puntos=5000)
        self.assertEqual(x_out, x)
        self.assertEqual(y_out, [float(v) for v in y])

    def test_conserva_minimo_y_maximo_globales(self):
        y = [50.0] * 100
        y[10] = -5.0   # minimo global
        y[73] = 999.0  # maximo global
        x = list(range(100))
        x_out, y_out = _downsample_minmax(x, y, max_puntos=10)
        self.assertLessEqual(len(y_out), 10)
        self.assertIn(-5.0, y_out)
        self.assertIn(999.0, y_out)

    def test_bloque_completamente_nan_no_rompe(self):
        y = [float('nan')] * 4
        x = list(range(4))
        x_out, y_out = _downsample_minmax(x, y, max_puntos=2)
        self.assertEqual(x_out, [])
        self.assertEqual(y_out, [])


class ProcesarCsvTests(SimpleTestCase):
    def setUp(self):
        self.datos = procesar_csv(io.StringIO(CSV_COMPLETO))

    def test_excluye_columnas_no_telemetria(self):
        ids_paneles = {panel['id'] for panel in self.datos['paneles']}
        self.assertNotIn('n_muestra', ids_paneles)
        self.assertNotIn('hora', ids_paneles)
        self.assertNotIn('tiempo_s', ids_paneles)
        self.assertNotIn('freno_tra', ids_paneles)

    def test_agrupa_pedales_en_un_solo_panel(self):
        panel_pedales = next(p for p in self.datos['paneles'] if p['id'] == 'pedales')
        columnas = {serie['columna'] for serie in panel_pedales['series']}
        self.assertEqual(columnas, {'tps', 'freno_del'})

    def test_canal_desconocido_se_muestra_con_su_propio_nombre(self):
        panel = next(p for p in self.datos['paneles'] if p['id'] == 'suspension_del')
        self.assertEqual(panel['titulo'], 'suspension_del')
        self.assertEqual(panel['unidad'], '')

    def test_canal_sin_datos_numericos_se_excluye_y_se_reporta(self):
        ids_paneles = {panel['id'] for panel in self.datos['paneles']}
        self.assertNotIn('sensor_roto', ids_paneles)
        self.assertIn('sensor_roto', self.datos['canales_sin_datos'])

    def test_orden_de_paneles_sigue_orden_preferido(self):
        ids_paneles = [panel['id'] for panel in self.datos['paneles']]
        # pedales primero, luego ect/rpm/vbatt en el orden de ORDEN_PANELES,
        # y el canal desconocido al final.
        self.assertEqual(ids_paneles, ['pedales', 'ect', 'rpm', 'vbatt', 'suspension_del'])

    def test_num_filas_y_downsampled(self):
        self.assertEqual(self.datos['num_filas'], 3)
        self.assertFalse(self.datos['downsampled'])

    def test_downsampled_true_si_supera_max_puntos(self):
        datos = procesar_csv(io.StringIO(CSV_COMPLETO), max_puntos=2)
        self.assertTrue(datos['downsampled'])

    def test_sin_columna_tiempo_usa_indice_de_fila(self):
        csv_sin_tiempo = "n_muestra,ect\n1,85\n2,86\n3,87\n"
        datos = procesar_csv(io.StringIO(csv_sin_tiempo))
        panel_ect = next(p for p in datos['paneles'] if p['id'] == 'ect')
        self.assertEqual(panel_ect['series'][0]['x'], [0, 1, 2])

    def test_csv_vacio_lanza_error(self):
        csv_vacio = "n_muestra,ect\n"
        with self.assertRaises(TelemetriaCSVError):
            procesar_csv(io.StringIO(csv_vacio))

    def test_archivo_ilegible_lanza_error(self):
        with self.assertRaises(TelemetriaCSVError):
            procesar_csv('/ruta/que/no/existe/telemetria.csv')


class CanalesParaVariablesTests(SimpleTestCase):
    def test_incluye_solo_canales_con_datos_y_no_excluidos(self):
        resultado = canales_para_variables(io.StringIO(CSV_COMPLETO))
        columnas = {fila[0] for fila in resultado}

        self.assertIn('ect', columnas)
        self.assertIn('tps', columnas)
        self.assertIn('suspension_del', columnas)

        self.assertNotIn('n_muestra', columnas)
        self.assertNotIn('hora', columnas)
        self.assertNotIn('tiempo_s', columnas)
        self.assertNotIn('freno_tra', columnas)
        self.assertNotIn('sensor_roto', columnas)

    def test_conserva_etiqueta_y_unidad_conocidas(self):
        resultado = canales_para_variables(io.StringIO(CSV_COMPLETO))
        fila_ect = next(f for f in resultado if f[0] == 'ect')
        self.assertEqual(fila_ect, ('ect', 'Temperatura motor (ECT)', '°C'))

    def test_canal_desconocido_usa_su_propio_nombre_sin_unidad(self):
        resultado = canales_para_variables(io.StringIO(CSV_COMPLETO))
        fila_desconocida = next(f for f in resultado if f[0] == 'suspension_del')
        self.assertEqual(fila_desconocida, ('suspension_del', 'suspension_del', ''))

    def test_archivo_ilegible_devuelve_lista_vacia(self):
        self.assertEqual(canales_para_variables('/ruta/que/no/existe/telemetria.csv'), [])
