from django.apps import apps
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def visor_universal(request, app_label, model_name, pk):
    """
    Vista mágica que muestra el detalle de CUALQUIER objeto del sistema.
    """
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return render(request, 'core/404.html', {'mensaje': 'Modelo no encontrado'})

    objeto = get_object_or_404(model, pk=pk)

    # 🛑 LISTA NEGRA: Campos que NO queremos ver nunca
    CAMPOS_IGNORADOS = [
        'password', 'id', 'pk', 
        'is_superuser', 'is_staff', 'groups', 'user_permissions', 
        'mfa_secret', 'mfa_enabled', 'mfa_backup_codes'
    ]

    detalles = []
    for field in model._meta.fields:
        # 1. Si el campo está en la lista negra, lo saltamos
        if field.name in CAMPOS_IGNORADOS:
            continue
            
        try:
            valor = getattr(objeto, field.name)
            
            if hasattr(objeto, f'get_{field.name}_display'):
                valor = getattr(objeto, f'get_{field.name}_display')()
            
            # Formateo visual para vacíos
            if valor is None or valor == '':
                valor = None # Para que el template lo detecte y ponga "-- Vacío --"

            detalles.append({
                'label': field.verbose_name.capitalize(),
                'valor': valor
            })
        except Exception:
            pass

    context = {
        'titulo': f"Detalle de {model._meta.verbose_name}",
        'objeto_str': str(objeto),
        'objeto_id': pk, # Pasamos el ID limpio para el subtítulo
        'detalles': detalles,
        'tipo': model_name 
    }
    return render(request, 'core/visor_universal.html', context)