from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.models import CustomUser
from .models import Factura


def _pdf(nombre='archivo.pdf'):
    return SimpleUploadedFile(nombre, b'%PDF-1.4 contenido de prueba', content_type='application/pdf')


class FacturasAreaPermisosTests(TestCase):
    """Comprueba que la tarjeta 'Facturas' deshabilitada en area_tecnica.html
    corresponde de verdad a un 403 en el servidor, y no solo a un enlace
    escondido en la plantilla."""

    @classmethod
    def setUpTestData(cls):
        cls.jefe_electronica = CustomUser.objects.create_user(
            username='jefe_electronica', password='x', rol='jefe_area', especialidad='electronica',
        )
        cls.miembro_electronica = CustomUser.objects.create_user(
            username='miembro_electronica', password='x', rol='miembro', especialidad='electronica',
        )
        cls.miembro_chasis = CustomUser.objects.create_user(
            username='miembro_chasis', password='x', rol='miembro', especialidad='chasis',
        )

    def test_facturas_area_devuelve_403_si_no_pertenece_al_area(self):
        self.client.force_login(self.miembro_chasis)
        resp = self.client.get('/areas/electronica/facturas/')
        self.assertEqual(resp.status_code, 403)

    def test_facturas_area_accesible_para_miembro_del_area(self):
        self.client.force_login(self.miembro_electronica)
        resp = self.client.get('/areas/electronica/facturas/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['puede_gestionar'])

    def test_facturas_area_accesible_para_jefe_del_area(self):
        self.client.force_login(self.jefe_electronica)
        resp = self.client.get('/areas/electronica/facturas/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['puede_gestionar'])

    def test_documentos_area_es_accesible_aunque_no_seas_del_area(self):
        # Documentacion, a diferencia de Facturas, es visible para cualquier
        # usuario logueado: por eso su tarjeta nunca se deshabilita.
        self.client.force_login(self.miembro_chasis)
        resp = self.client.get('/areas/electronica/documentos/')
        self.assertEqual(resp.status_code, 200)

    def test_anadir_factura_rechaza_a_quien_no_es_del_area(self):
        self.client.force_login(self.miembro_chasis)
        resp = self.client.post('/areas/electronica/facturas/anadir/', {
            'nombre': 'Factura intrusa',
            'empresa': 'ACME',
            'importe': '50.00',
            'archivo': _pdf(),
        })
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Factura.objects.count(), 0)


class EditarFacturaPermisosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.jefe_electronica = CustomUser.objects.create_user(
            username='jefe_electronica2', password='x', rol='jefe_area', especialidad='electronica',
        )
        cls.miembro_electronica = CustomUser.objects.create_user(
            username='miembro_electronica2', password='x', rol='miembro', especialidad='electronica',
        )
        cls.factura = Factura.objects.create(
            nombre='Sensor de presion', archivo=_pdf(), categoria='electronica',
            empresa='ACME', importe=42, estado='pendiente',
        )

    def test_miembro_no_gestor_no_puede_editar_la_factura_de_su_propia_area(self):
        self.client.force_login(self.miembro_electronica)
        resp = self.client.get(f'/documentos/factura/{self.factura.pk}/editar/')
        self.assertEqual(resp.status_code, 403)

    def test_jefe_de_area_si_puede_editar_la_factura(self):
        self.client.force_login(self.jefe_electronica)
        resp = self.client.get(f'/documentos/factura/{self.factura.pk}/editar/')
        self.assertEqual(resp.status_code, 200)
