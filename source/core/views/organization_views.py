from django.shortcuts import render, get_object_or_404
from core.models import Empresa, UnidadOrganizacional

def organizacion_dashboard(request):
    # 1. Obtenemos todas las empresas para el menú desplegable
    empresas = Empresa.objects.filter(estado=True)
    
    # 2. Verificamos si hay una empresa seleccionada en la URL (ej: ?empresa_id=1)
    empresa_id = request.GET.get('empresa_id')
    
    empresa_actual = None
    unidades = []

    if empresa_id:
        # Si seleccionaron una, buscamos esa empresa y sus unidades
        empresa_actual = get_object_or_404(Empresa, id=empresa_id)
        unidades = UnidadOrganizacional.objects.filter(empresa=empresa_actual).order_by('nombre')
    elif empresas.exists():
        # Si no seleccionaron nada pero hay empresas, tomamos la primera por defecto
        empresa_actual = empresas.first()
        unidades = UnidadOrganizacional.objects.filter(empresa=empresa_actual).order_by('nombre')

    context = {
        'empresas': empresas,
        'empresa_actual': empresa_actual,
        'unidades': unidades
    }
    return render(request, 'core/organizacion/panel_organizacion.html', context)