# usuarios/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied


def solo_superusuario(view_func):
    """
    Restringe el acceso únicamente a usuarios autenticados
    con el flag is_superuser=True.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or not getattr(user, "is_superuser", False):
            raise PermissionDenied  # Respuesta HTTP 403

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def solo_admin_rrhh(view_func):
    """
    Restringe el acceso a usuarios autenticados con el rol
    de negocio 'Admin RRHH'.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or not getattr(user, "es_admin_rrhh", False):
            raise PermissionDenied  # Respuesta HTTP 403

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def solo_superusuario_o_admin_rrhh(view_func):
    """
    Permite el acceso a usuarios autenticados que cumplan
    al menos una de las siguientes condiciones:
    - is_superuser=True (superusuario del sistema)
    - es_superadmin_negocio=True (rol de negocio equivalente)
    - es_admin_rrhh=True (administrador de RRHH)
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied  # Respuesta HTTP 403

        if getattr(user, "is_superuser", False):
            return view_func(request, *args, **kwargs)

        if getattr(user, "es_superadmin_negocio", False):
            return view_func(request, *args, **kwargs)

        if getattr(user, "es_admin_rrhh", False):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied

    return _wrapped_view
