from django.test import SimpleTestCase

from .areas import es_gestor_area, es_miembro_area
from .models import CustomUser


def _usuario(rol, especialidad=None):
    # Instancia en memoria, sin guardar en BD: estas funciones solo leen
    # atributos del usuario, no hace falta tocar MySQL para probarlas.
    return CustomUser(rol=rol, especialidad=especialidad)


class EsMiembroAreaTests(SimpleTestCase):
    def test_directiva_es_miembro_de_cualquier_area(self):
        directiva = _usuario('directiva', especialidad=None)
        self.assertTrue(es_miembro_area(directiva, 'chasis'))
        self.assertTrue(es_miembro_area(directiva, 'software'))

    def test_jefe_area_es_miembro_de_su_propia_area(self):
        jefe = _usuario('jefe_area', especialidad='software')
        self.assertTrue(es_miembro_area(jefe, 'software'))

    def test_jefe_area_no_es_miembro_de_otra_area(self):
        jefe = _usuario('jefe_area', especialidad='software')
        self.assertFalse(es_miembro_area(jefe, 'chasis'))

    def test_miembro_es_miembro_de_su_propia_area(self):
        miembro = _usuario('miembro', especialidad='electronica')
        self.assertTrue(es_miembro_area(miembro, 'electronica'))

    def test_miembro_no_es_miembro_de_otra_area(self):
        miembro = _usuario('miembro', especialidad='electronica')
        self.assertFalse(es_miembro_area(miembro, 'chasis'))

    def test_usuario_sin_especialidad_asignada_no_es_miembro_de_ningun_area(self):
        miembro = _usuario('miembro', especialidad=None)
        self.assertFalse(es_miembro_area(miembro, 'chasis'))


class EsGestorAreaTests(SimpleTestCase):
    def test_directiva_es_gestor_de_cualquier_area(self):
        directiva = _usuario('directiva', especialidad=None)
        self.assertTrue(es_gestor_area(directiva, 'chasis'))
        self.assertTrue(es_gestor_area(directiva, 'software'))

    def test_jefe_area_es_gestor_de_su_propia_area(self):
        jefe = _usuario('jefe_area', especialidad='software')
        self.assertTrue(es_gestor_area(jefe, 'software'))

    def test_jefe_area_no_es_gestor_de_otra_area(self):
        jefe = _usuario('jefe_area', especialidad='software')
        self.assertFalse(es_gestor_area(jefe, 'chasis'))

    def test_miembro_de_la_propia_area_no_es_gestor(self):
        # Es justo el caso que causaba el 403 al pulsar "Ver" en Facturas
        # antes de deshabilitar el enlace: pertenecer al area no basta para
        # gestionarla, solo el jefe de area (o directiva) puede.
        miembro = _usuario('miembro', especialidad='electronica')
        self.assertFalse(es_gestor_area(miembro, 'electronica'))

    def test_miembro_de_otra_area_no_es_gestor(self):
        miembro = _usuario('miembro', especialidad='electronica')
        self.assertFalse(es_gestor_area(miembro, 'chasis'))
