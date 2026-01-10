from core.models import Empresa

def global_empresas_selector(request):
    """
    Inyecta la lista de empresas en el contexto global, 
    pero SOLO si el usuario es Superusuario.
    """
    if not request.user.is_authenticated:
        return {}

    # Verificamos si es "Dios" (Superuser de Django o SuperAdmin de Negocio)
    es_superadmin = request.user.is_superuser or getattr(request.user, "es_superadmin_negocio", False)

    if es_superadmin:
        # Devolvemos la lista para que el HTML base la pueda usar
        return {
            'lista_empresas_global': Empresa.objects.filter(estado=True).order_by('nombre_comercial'),
            'es_superadmin_global': True # Bandera para facilitar el if en el HTML
        }
    
    return {'es_superadmin_global': False}