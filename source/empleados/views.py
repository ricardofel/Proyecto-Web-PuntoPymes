from django.shortcuts import render
from .models import Empleado  # <--- 1. IMPORTANTE: Importar el modelo
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