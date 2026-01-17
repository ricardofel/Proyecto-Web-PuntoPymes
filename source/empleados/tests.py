import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404

# importaciones locales
from .models import Empleado, Contrato
from .forms import EmpleadoForm, ContratoForm
from core.models import Empresa, Rol
from core.storage import private_storage

# --- vistas basadas en clases ---

class ListaEmpleadosView(LoginRequiredMixin, ListView):
    """
    vista principal para listar empleados con funcionalidad de busqueda.
    utiliza paginacion automatica de django.
    """
    model = Empleado
    template_name = 'empleados/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10

    def get_queryset(self):
        # optimizacion de consulta con select_related para evitar query n+1
        queryset = Empleado.objects.select_related('puesto', 'unidad_org', 'empresa').all()
        
        # logica de busqueda por nombre, apellido o cedula
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombres__icontains=query) | 
                Q(apellidos__icontains=query) | 
                Q(cedula__icontains=query)
            )
        return queryset.order_by('-id')


# --- vistas basadas en funciones ---

@login_required
def crear_empleado_view(request):
    """
    gestiona el formulario de alta de nuevos empleados.
    maneja la logica de roles y asignacion de empresa.
    """
    # obtenemos la empresa del usuario actual (asumiendo que tiene una asignada)
    empresa_usuario = getattr(request.user, 'empresa', None)
    empresa_id = empresa_usuario.id if empresa_usuario else None

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, empresa_id=empresa_id)
        if form.is_valid():
            empleado = form.save()
            messages.success(request, f"Empleado {empleado.nombres} registrado exitosamente.")
            return redirect('empleados:lista_empleados')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = EmpleadoForm(empresa_id=empresa_id)

    # carga de roles para el selector manual en el template
    roles = Rol.objects.all()
    
    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles
    })


@login_required
def editar_empleado_view(request, pk):
    """
    permite la edicion de la ficha tecnica de un empleado existente.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    empresa_id = empleado.empresa_id

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado, empresa_id=empresa_id)
        if form.is_valid():
            form.save()
            messages.success(request, "Información actualizada correctamente.")
            return redirect('empleados:lista_empleados')
        else:
            messages.error(request, "No se pudieron guardar los cambios.")
    else:
        form = EmpleadoForm(instance=empleado, empresa_id=empresa_id)

    return render(request, 'empleados/editar_empleado.html', {
        'form': form,
        'empleado': empleado
    })


@login_required
def actualizar_foto_view(request, pk):
    """
    endpoint especifico para la actualizacion rapida de la foto de perfil
    desde el modal en la vista de edicion.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST' and request.FILES.get('foto'):
        empleado.foto = request.FILES['foto']
        empleado.save()
        messages.success(request, "Foto de perfil actualizada.")
    
    return redirect('empleados:editar_empleado', pk=pk)


@login_required
def cambiar_estado_empleado_view(request, pk):
    """
    cambia el estado de un empleado (activo/inactivo) y redirige a la lista.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    
    # logica simple de alternancia o desactivacion
    # aqui podrias implementar logica mas compleja si fuera necesario
    if empleado.estado == Empleado.Estado.ACTIVO:
        empleado.estado = Empleado.Estado.INACTIVO
    else:
        empleado.estado = Empleado.Estado.ACTIVO
    
    empleado.save()
    messages.info(request, f"Estado de {empleado.nombres} actualizado.")
    return redirect('empleados:lista_empleados')


# --- gestion de contratos ---

@login_required
def lista_contratos_view(request, empleado_id):
    """
    muestra el historial de vinculaciones laborales de un empleado especifico.
    """
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    contratos = empleado.contratos.all().order_by('-fecha_inicio')
    
    return render(request, 'empleados/lista_contratos.html', {
        'empleado': empleado,
        'contratos': contratos
    })


@login_required
def crear_contrato_view(request, empleado_id):
    """
    registra una nueva vinculacion laboral y maneja la subida del pdf firmado.
    """
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.empleado = empleado
            contrato.save()
            messages.success(request, "Contrato registrado correctamente.")
            return redirect('empleados:lista_contratos', empleado_id=empleado.id)
    else:
        form = ContratoForm()
    
    return render(request, 'empleados/crear_contrato.html', {
        'form': form,
        'empleado': empleado
    })


@login_required
def servir_contrato_privado(request, filepath):
    """
    vista de seguridad para servir archivos protegidos.
    valida permisos y existencia del archivo antes de entregarlo.
    """
    # 1. limpieza de la ruta para evitar duplicidad de slashes
    ruta_limpia = filepath.strip('/')
    
    # 2. verificacion de existencia en el almacenamiento privado
    if not private_storage.exists(ruta_limpia):
        # intento de recuperacion por si la ruta viene incompleta
        if private_storage.exists(f'contratos/{ruta_limpia}'):
             ruta_limpia = f'contratos/{ruta_limpia}'
        else:
             raise Http404("El documento no se encuentra disponible.")
        
    # 3. entrega del archivo como respuesta binaria
    archivo = private_storage.open(ruta_limpia)
    return FileResponse(archivo)