from django.apps import apps
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def visor_universal(request, app_label, model_name, pk):
    """
    Vista genérica de detalle.

    Muestra los campos visibles de cualquier modelo del sistema,
    excluyendo explícitamente campos sensibles o técnicos.
    """

    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return render(request, "core/404.html", {"mensaje": "Modelo no encontrado"})

    objeto = get_object_or_404(model, pk=pk)

    # Campos que nunca deben mostrarse (seguridad y ruido técnico).
    CAMPOS_IGNORADOS = [
        "password",
        "id",
        "pk",
        "is_superuser",
        "is_staff",
        "groups",
        "user_permissions",
        "mfa_secret",
        "mfa_enabled",
        "mfa_backup_codes",
    ]

    detalles = []
    for field in model._meta.fields:
        # Omitir campos incluidos en la lista de exclusión.
        if field.name in CAMPOS_IGNORADOS:
            continue

        try:
            valor = getattr(objeto, field.name)

            # Usar display() cuando el campo tenga choices definidos.
            if hasattr(objeto, f"get_{field.name}_display"):
                valor = getattr(objeto, f"get_{field.name}_display")()

            # Normalizar valores vacíos para que el template los trate como "sin dato".
            if valor is None or valor == "":
                valor = None

            detalles.append(
                {
                    "label": field.verbose_name.capitalize(),
                    "valor": valor,
                }
            )
        except Exception:
            # Cualquier error al acceder o formatear el campo se ignora silenciosamente.
            pass

    context = {
        "titulo": f"Detalle de {model._meta.verbose_name}",
        "objeto_str": str(objeto),
        "objeto_id": pk,
        "detalles": detalles,
        "tipo": model_name,
    }

    return render(request, "core/visor_universal.html", context)
