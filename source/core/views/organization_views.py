from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.models import Empresa, UnidadOrganizacional
from core.forms import UnidadOrganizacionalForm

@login_required
def organizacion_dashboard(request):
    """
    Panel principal de Organización.
    Ahora responde 100% a la selección global del menú lateral.
    """
    
    # 1. OBTENER LA EMPRESA DEL CONTEXTO GLOBAL (Middleware)
    # Ya no buscamos en GET['empresa_id'] manualmente, confiamos en el sistema global.
    empresa_actual = getattr(request, 'empresa_actual', None)

    unidades = []

    # 2. FILTRAR LAS UNIDADES
    if empresa_actual:
        # Si hay empresa seleccionada, traemos SUS unidades
        unidades = UnidadOrganizacional.objects.filter(
            empresa=empresa_actual
        ).select_related('padre').order_by('nombre')
    else:
        # Si no hay empresa (ej: SuperAdmin nuevo sin seleccionar nada), lista vacía.
        unidades = []

    # 3. RENDERIZAR
    # Nota: Ya no necesitamos pasar 'empresas' (la lista completa) porque 
    # el selector ahora vive en el sidebar (base_dashboard.html).
    context = {
        'unidades': unidades,
        'empresa_actual': empresa_actual,
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