from django.shortcuts import render, redirect, get_object_or_404
from .models import Empleado 
from .forms import EmpleadoForm

def lista_empleados_view(request):
    empleados_list = Empleado.objects.select_related('puesto', 'unidad_org').all()
    
    context = {
        'empleados': empleados_list  # <--- 3. EL PAQUETE: Esto conecta con tu HTML
    }
    
    return render(request, 'empleados/lista_empleados.html', context)

def crear_empleado_view(request):
    if request.method == 'POST':
        # Si el usuario envió datos, llenamos el formulario con ellos
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save() # ¡Guardado en Postgres!
            return redirect('empleados:lista_empleados') # Te devuelve a la lista
    else:
        # Si es la primera vez que entra, formulario vacío
        form = EmpleadoForm()

    return render(request, 'empleados/crear_empleado.html', {'form': form})

def editar_empleado_view(request, pk):
    # 1. Buscamos el empleado por su ID (pk). Si no existe, da error 404.
    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == 'POST':
        # 2. Cargamos el form con los datos POST y la instancia del empleado (para actualizar, no crear)
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('empleados:lista_empleados')
    else:
        # 3. Si es GET, cargamos el formulario con los datos actuales del empleado
        form = EmpleadoForm(instance=empleado)

    return render(request, 'empleados/editar_empleado.html', {
        'form': form,
        'empleado': empleado
    })