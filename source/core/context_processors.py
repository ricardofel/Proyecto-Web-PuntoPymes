from core.models import Empresa


def global_empresas_selector(request):
    """
    Context processor global.

    Expone en el contexto:
    - empresa_actual: empresa determinada por el middleware.
    - es_superadmin_global: flag de privilegios elevados.
    - lista_empresas_global: listado de empresas activas (solo para superadmins).
    """

    contexto = {
        "es_superadmin_global": False,
        "lista_empresas_global": None,
        "empresa_actual": getattr(request, "empresa_actual", None),
    }

    # Si el usuario no está autenticado, se retorna el contexto base.
    if not request.user.is_authenticated:
        return contexto

    # Determinar privilegios de superadministrador (Django o rol de negocio).
    es_superadmin = request.user.is_superuser or getattr(
        request.user, "es_superadmin_negocio", False
    )

    if es_superadmin:
        contexto["es_superadmin_global"] = True
        contexto["lista_empresas_global"] = (
            Empresa.objects.filter(estado=True).order_by("nombre_comercial")
        )

    return contexto
