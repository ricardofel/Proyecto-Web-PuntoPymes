from django.shortcuts import render, get_object_or_404
from core.models import Empresa, UnidadOrganizacional
from django.shortcuts import redirect
from core.forms import UnidadOrganizacionalForm

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

# --- VISTA PARA CREAR ---
def crear_unidad(request):
    # Obtenemos el ID de la empresa desde la URL (ej: ?empresa_id=1)
    empresa_id = request.GET.get('empresa_id')
    
    if not empresa_id:
        return redirect('organizacion') # Seguridad: Si no hay empresa, volver al panel

    empresa = get_object_or_404(Empresa, id=empresa_id)

    if request.method == 'POST':
        form = UnidadOrganizacionalForm(request.POST, empresa_id=empresa_id)
        if form.is_valid():
            unidad = form.save(commit=False)
            unidad.empresa = empresa # Asignamos la empresa automáticamente
            unidad.save()
            # Redirigimos al panel manteniendo la empresa seleccionada
            return redirect(f'/organizacion/?empresa_id={empresa_id}')
    else:
        form = UnidadOrganizacionalForm(empresa_id=empresa_id)

    context = {
        'form': form,
        'titulo': 'Nueva Unidad Organizacional',
        'boton_texto': 'Crear Unidad',
        'empresa': empresa
    }
    return render(request, 'core/organizacion/unidad_form.html', context)

# --- VISTA PARA EDITAR ---
def editar_unidad(request, pk):
    unidad = get_object_or_404(UnidadOrganizacional, pk=pk)
    empresa_id = unidad.empresa.id

    if request.method == 'POST':
        form = UnidadOrganizacionalForm(request.POST, instance=unidad, empresa_id=empresa_id)
        if form.is_valid():
            form.save()
            return redirect(f'/organizacion/?empresa_id={empresa_id}')
    else:
        form = UnidadOrganizacionalForm(instance=unidad, empresa_id=empresa_id)

    context = {
        'form': form,
        'titulo': f'Editar: {unidad.nombre}',
        'boton_texto': 'Guardar Cambios',
        'empresa': unidad.empresa
    }
    return render(request, 'core/organizacion/unidad_form.html', context)