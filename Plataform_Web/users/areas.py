from .models import CustomUser

# Color de acento por área técnica, reutilizando la paleta ya cargada de Bootstrap
AREA_COLORS = {
    'aerodinamica': '#0dcaf0',
    'chasis': '#6c757d',
    'business_operations': '#fd7e14',
    'epowertrain': '#198754',
    'electronica': '#6610f2',
    'sdf': '#6f42c1',
    'motor_transmision': '#dc3545',
    'software': '#20c997',
}

# Icono (trazo SVG, viewBox 24x24) por área técnica. Las áreas sin entrada
# aquí usan el hexágono genérico como icono por defecto.
AREA_ICONS = {
    'software': 'M8 9l-4 3 4 3M16 9l4 3-4 3M14 6l-4 12',
}
AREA_ICON_DEFAULT = 'M12 2l8 4.5v9L12 20l-8-4.5v-9L12 2z'


def darken(hex_color, factor=0.55):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * factor) for c in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'


def get_area_nombre(especialidad):
    return dict(CustomUser.ESPECIALIDAD_CHOICES).get(especialidad)


def get_area_color(especialidad):
    return AREA_COLORS.get(especialidad, '#0d6efd')


def get_area_icon_path(especialidad):
    return AREA_ICONS.get(especialidad, AREA_ICON_DEFAULT)


def es_miembro_area(user, especialidad):
    """Puede añadir contenido al área: es de esa especialidad, o es directiva (acceso total)."""
    return user.rol == 'directiva' or user.especialidad == especialidad


def es_gestor_area(user, especialidad):
    """Puede editar/eliminar contenido del área: es su Jefe de Área, o es directiva (acceso total)."""
    return user.rol == 'directiva' or (user.rol == 'jefe_area' and user.especialidad == especialidad)
