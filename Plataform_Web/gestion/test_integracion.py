import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documentos.models import Documento, Factura
from temporadas.models import Temporada
from users.models import CustomUser

from .models import Gasto


def _pdf(nombre='archivo.pdf'):
    return SimpleUploadedFile(nombre, b'%PDF-1.4 contenido de prueba', content_type='application/pdf')


class AceptarFacturaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.temporada = Temporada.objects.create(
            nombre='2025/2026-test', fecha_inicio=datetime.date(2025, 9, 1),
            fecha_fin=datetime.date(2026, 8, 31), presupuesto=1000, actual=True,
        )
        cls.jefe_electronica = CustomUser.objects.create_user(
            username='jefe_electronica_gasto', password='x', rol='jefe_area', especialidad='electronica',
        )
        cls.miembro_electronica = CustomUser.objects.create_user(
            username='miembro_electronica_gasto', password='x', rol='miembro', especialidad='electronica',
        )

    def _crear_factura_pendiente(self):
        return Factura.objects.create(
            nombre='Sensor de presion', archivo=_pdf(), categoria='electronica',
            empresa='ACME', importe=42, estado='pendiente',
        )

    def test_jefe_de_area_acepta_la_factura_y_genera_el_gasto(self):
        factura = self._crear_factura_pendiente()
        self.client.force_login(self.jefe_electronica)
        self.client.post(f'/gestion/contabilidad/factura/{factura.pk}/aceptar/')

        factura.refresh_from_db()
        self.assertEqual(factura.estado, 'aceptada')

        gasto = Gasto.objects.get(concepto=factura.nombre)
        self.assertEqual(gasto.importe, factura.importe)
        self.assertEqual(gasto.categoria, 'electronica')
        self.assertEqual(gasto.temporada, self.temporada)

    def test_miembro_no_gestor_no_puede_aceptar_la_factura(self):
        # Mismo caso que el bug de Facturas: pertenecer al area no da
        # permiso para gestionarla, solo el jefe de area o directiva.
        factura = self._crear_factura_pendiente()
        self.client.force_login(self.miembro_electronica)
        resp = self.client.post(f'/gestion/contabilidad/factura/{factura.pk}/aceptar/')

        self.assertEqual(resp.status_code, 403)
        factura.refresh_from_db()
        self.assertEqual(factura.estado, 'pendiente')
        self.assertEqual(Gasto.objects.count(), 0)


class SubirDossierTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.temporada = Temporada.objects.create(
            nombre='2025/2026-dossier-test', fecha_inicio=datetime.date(2025, 9, 1),
            fecha_fin=datetime.date(2026, 8, 31), presupuesto=1000, actual=True,
        )
        cls.directiva = CustomUser.objects.create_user(
            username='directiva_dossier', password='x', rol='directiva',
        )
        cls.jefe_area = CustomUser.objects.create_user(
            username='jefe_dossier', password='x', rol='jefe_area', especialidad='software',
        )

    def test_directiva_sube_el_dossier_y_queda_ligado_a_la_temporada_actual(self):
        self.client.force_login(self.directiva)
        self.client.post('/patrocinios/dossier/es/subir/', {'archivo': _pdf()})

        doc = Documento.objects.get(tipo='dossier_patrocinado', nombre='Dossier de Patrocinio (ES)')
        self.assertIn(self.temporada, doc.temporada.all())

    def test_subir_de_nuevo_sustituye_el_dossier_anterior_sin_duplicar(self):
        self.client.force_login(self.directiva)
        self.client.post('/patrocinios/dossier/es/subir/', {'archivo': _pdf('v1.pdf')})
        self.client.post('/patrocinios/dossier/es/subir/', {'archivo': _pdf('v2.pdf')})

        dossiers = Documento.objects.filter(tipo='dossier_patrocinado', nombre='Dossier de Patrocinio (ES)')
        self.assertEqual(dossiers.count(), 1)

    def test_quien_no_es_directiva_no_puede_subir_dossier(self):
        self.client.force_login(self.jefe_area)
        resp = self.client.post('/patrocinios/dossier/es/subir/', {'archivo': _pdf()})

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Documento.objects.filter(tipo='dossier_patrocinado').count(), 0)

    def test_usuario_anonimo_es_redirigido_a_login(self):
        # A diferencia del caso anterior (logueado, rol incorrecto -> 403),
        # quien no ha iniciado sesion si debe ir al formulario de login.
        resp = self.client.post('/patrocinios/dossier/es/subir/', {'archivo': _pdf()})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.headers['Location'])
