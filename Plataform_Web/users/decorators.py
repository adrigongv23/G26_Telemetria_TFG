from django.contrib.auth.decorators import login_required, user_passes_test


def require_rol(*roles):
    def decorator(view_func):
        return login_required(user_passes_test(lambda u: u.rol in roles)(view_func))
    return decorator
