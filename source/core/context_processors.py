from core.models import Empresa

def global_empresas_selector(request):
    """
    Inyecta la lista de empresas Y la empresa actual en el contexto global.
    """
    contexto = {
        'es_superadmin_global': False,
        'lista_empresas_global': None,
        # AGREGAMOS ESTO: Pasamos la empresa actual detectada por el Middleware
        'empresa_actual': getattr(request, 'empresa_actual', None)
    }

    if not request.user.is_authenticated:
        return contexto

    # Verificamos si es "Dios" (Superuser de Django o SuperAdmin de Negocio)
    es_superadmin = request.user.is_superuser or getattr(request.user, "es_superadmin_negocio", False)

    if es_superadmin:
        contexto['es_superadmin_global'] = True
        contexto['lista_empresas_global'] = Empresa.objects.filter(estado=True).order_by('nombre_comercial')
    
    return contexto