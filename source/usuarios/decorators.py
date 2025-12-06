# usuarios/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied


def solo_admin_usuarios(view_func):
    """
    Restringe acceso a vistas del módulo Usuarios.
    Solo permite usuarios que pueden ver el módulo Usuarios.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated or not getattr(
            user, "puede_ver_modulo_usuarios", False
        ):
            raise PermissionDenied  # 403
        return view_func(request, *args, **kwargs)

    return _wrapped_view
