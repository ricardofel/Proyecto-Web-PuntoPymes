# usuarios/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied


def solo_superusuario(view_func):
    """
    Solo permite acceso a usuarios con is_superuser=True.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or not getattr(user, "is_superuser", False):
            raise PermissionDenied  # 403

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def solo_admin_rrhh(view_func):
    """
    Solo permite acceso a usuarios con rol de negocio 'Admin RRHH'.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or not getattr(user, "es_admin_rrhh", False):
            raise PermissionDenied  # 403

        return view_func(reques, *args, **kwargs)

    return _wrapped_view


def solo_superusuario_o_admin_rrhh(view_func):
    """
    Permite acceso a:
    - Usuarios con is_superuser=True
    - O usuarios con rol 'Superusuario' (es_superadmin_negocio)
    - O usuarios con rol 'Admin RRHH'
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied  # 403

        if getattr(user, "is_superuser", False):
            return view_func(request, *args, **kwargs)

        if getattr(user, "es_superadmin_negocio", False):
            return view_func(request, *args, **kwargs)

        if getattr(user, "es_admin_rrhh", False):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied

    return _wrapped_view
