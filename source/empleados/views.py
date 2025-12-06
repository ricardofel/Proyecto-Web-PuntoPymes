import os
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from .models import Empleado 
from .forms import EmpleadoForm
from .models import Empleado, Contrato 
from .forms import EmpleadoForm

def lista_empleados_view(request):
    # Empezamos trayendo todos los empleados
    empleados = Empleado.objects.all().order_by('-id') # O el orden que prefieras

    # Capturamos lo que el usuario escribió en el buscador (campo 'q')
    busqueda = request.GET.get('q')

    if busqueda:
        # Si hay algo escrito, filtramos.
        # Usamos __icontains para que no importen mayúsculas/minúsculas
        # Usamos Q(...) | Q(...) para decir "O" (Nombre O Apellido O Cédula)
        empleados = empleados.filter(
            Q(nombres__icontains=busqueda) | 
            Q(apellidos__icontains=busqueda) |
            Q(cedula__icontains=busqueda)
        )

    return render(request, 'empleados/lista_empleados.html', {
        'empleados': empleados
    })

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

def lista_contratos_view(request, empleado_id):
    # 1. Obtenemos el empleado (o error 404 si no existe)
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    # 2. Filtramos SOLO los contratos de este empleado
    contratos = Contrato.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    
    return render(request, 'empleados/lista_contratos.html', {
        'empleado': empleado,
        'contratos': contratos
    })

@require_POST # Seguridad: Solo funciona si envían datos (POST)
def actualizar_foto_view(request, pk):
    # 1. Buscamos al empleado por su ID
    empleado = get_object_or_404(Empleado, pk=pk)

    # 2. Verificamos si llegó un archivo en el paquete 'foto'
    if 'foto' in request.FILES:
        # (Opcional pero recomendado) Borramos la foto anterior del disco
        if empleado.foto:
            try:
                if os.path.isfile(empleado.foto.path):
                    os.remove(empleado.foto.path)
            except Exception as e:
                print(f"Error al borrar foto vieja: {e}")

        # 3. Asignamos la nueva foto. 
        # Django usará automáticamente tu función 'ruta_foto_empleado' del models.py 
        # para ponerle el nombre correcto y guardarla en la carpeta 'media/empleados/fotos'
        empleado.foto = request.FILES['foto']
        empleado.save()

    # 4. Recargamos la página para que veas la foto nueva
    return redirect('empleados:editar_empleado', pk=pk)

@require_POST # Solo acepta peticiones POST (seguridad)
def cambiar_estado_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    
    # 1. Capturamos el nuevo estado enviado desde el formulario
    nuevo_estado = request.POST.get('nuevo_estado')
    
    # 2. Lista de estados válidos (para seguridad extra)
    estados_validos = ['Activo', 'Inactivo', 'Licencia', 'Suspendido']
    
    # 3. Si el estado es válido, lo actualizamos
    if nuevo_estado in estados_validos:
        empleado.estado = nuevo_estado
        empleado.save()
    
    # 4. Regresamos a la misma página
    return redirect('empleados:editar_empleado', pk=pk)