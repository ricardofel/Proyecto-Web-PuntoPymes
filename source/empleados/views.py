import os

# imports de django
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.utils.decorators import method_decorator
# Importamos require_http_methods para ser explícitos con SonarQube
from django.views.decorators.http import require_POST, require_safe, require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.utils.crypto import get_random_string

# imports del core y utilidades
from core.mixins import FiltradoEmpresaMixin
from core.storage import private_storage

# imports de usuarios (control de acceso)
from usuarios.decorators import solo_superusuario_o_admin_rrhh
from usuarios.models import Rol, UsuarioRol

# imports locales
from .models import Empleado, Contrato
from .forms import EmpleadoForm, ContratoForm


# --- vistas basadas en clases ---

@method_decorator(solo_superusuario_o_admin_rrhh, name='dispatch')
class ListaEmpleadosView(FiltradoEmpresaMixin, ListView):
    """
    Vista de listado principal de empleados.
    Integra filtrado por empresa (mixin) y búsqueda por múltiples campos.
    """
    model = Empleado
    template_name = 'empleados/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10 

    def get_queryset(self):
        qs = super().get_queryset()
        busqueda = self.request.GET.get('q')
        if busqueda:
            qs = qs.filter(
                Q(nombres__icontains=busqueda) | 
                Q(apellidos__icontains=busqueda) |
                Q(cedula__icontains=busqueda)
            )
        return qs.order_by('-id')


# --- vistas basadas en funciones ---

@login_required
@require_http_methods(["GET", "POST"]) # Blindaje explícito
def crear_empleado_view(request):
    """
    Gestiona el alta de empleados y la creación automática de su usuario.
    Acepta GET (formulario) y POST (creación).
    """
    empresa_actual = getattr(request, 'empresa_actual', None)
    empresa_id = empresa_actual.id if empresa_actual else None

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, empresa_id=empresa_id)
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Preparación del objeto empleado
                    empleado = form.save(commit=False)
                    if empresa_actual:
                        empleado.empresa = empresa_actual
                    empleado.save()
                    
                    # 2. Gestión del usuario de sistema asociado
                    email = form.cleaned_data.get('email') or empleado.email
                    
                    if email:
                        User = get_user_model()
                        # Generación de contraseña segura
                        password_acceso = get_random_string(length=12)
                        
                        user = None
                        if User.objects.filter(email=email).exists():
                            # Vinculación con usuario existente
                            user = User.objects.get(email=email)
                            user.estado = True 
                            if hasattr(user, 'empleado'): 
                                user.empleado = empleado
                            user.save()
                            messages.success(request, "Usuario vinculado existente.")
                        else:
                            # Creación de nuevo usuario
                            user = User.objects.create_user(
                                username=email, email=email, password=password_acceso, estado=True 
                            )
                            if hasattr(user, 'empleado'): 
                                user.empleado = empleado
                            user.save()
                            messages.success(request, f"Usuario creado. Clave temporal: {password_acceso}")

                        # 3. Asignación de Roles
                        if user:
                            rol_obj = None
                            if rol_id: 
                                rol_obj = Rol.objects.filter(id=rol_id).first()
                            
                            if not rol_obj: 
                                rol_obj = Rol.objects.filter(nombre="Empleado").first()

                            if rol_obj:
                                UsuarioRol.objects.filter(usuario=user).delete()
                                UsuarioRol.objects.create(usuario=user, rol=rol_obj)
                    else:
                        messages.warning(request, "Empleado creado SIN acceso al sistema (falta email).")

                return redirect('empleados:lista_empleados')

            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")
        else:
             messages.error(request, "Error en el formulario. Verifique los campos.")
    
    # Manejo del método GET
    else:
        form = EmpleadoForm(empresa_id=empresa_id)

    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles_disponibles
    })


@login_required
@require_http_methods(["GET", "POST"]) # Blindaje explícito
def editar_empleado_view(request, pk):
    """
    Permite la edición de datos del empleado.
    Acepta GET (ver datos) y POST (guardar cambios).
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    empresa_id = empleado.empresa.id if empleado.empresa else None
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado, empresa_id=empresa_id)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado actualizado.")
            return redirect('empleados:lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado, empresa_id=empresa_id)

    roles_disponibles = Rol.objects.filter(estado=True)
    
    rol_actual_id = None
    usuario_asociado = get_user_model().objects.filter(email=empleado.email).first()
    if usuario_asociado:
        ur = UsuarioRol.objects.filter(usuario=usuario_asociado).first()
        if ur: rol_actual_id = ur.rol.id

    return render(request, 'empleados/editar_empleado.html', {
        'form': form, 
        'empleado': empleado,
        'roles_disponibles': roles_disponibles,
        'rol_actual_id': rol_actual_id,
        'es_edicion': True
    })


# --- gestión de contratos y utilidades ---

@login_required
@require_safe
def lista_contratos_view(request, empleado_id):
    """
    Vista de solo lectura.
    """
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    contratos = Contrato.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    return render(request, 'empleados/lista_contratos.html', {
        'empleado': empleado, 
        'contratos': contratos
    })


@login_required
@require_http_methods(["GET", "POST"]) # Blindaje explícito
def crear_contrato_view(request, empleado_id):
    """
    Registra un nuevo contrato.
    Acepta GET (formulario) y POST (crear).
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


@require_POST
@login_required
def actualizar_foto_view(request, pk):
    """
    Solo POST.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    if 'foto' in request.FILES:
        if empleado.foto and os.path.isfile(empleado.foto.path):
            try: 
                os.remove(empleado.foto.path)
            except OSError: 
                pass
        
        empleado.foto = request.FILES['foto']
        empleado.save()
        messages.success(request, "Foto actualizada.")
    return redirect('empleados:editar_empleado', pk=pk)


@require_POST
@login_required
def cambiar_estado_empleado_view(request, pk):
    """
    Solo POST.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    nuevo_estado = request.POST.get('nuevo_estado')
    
    if nuevo_estado in ['Activo', 'Inactivo', 'Licencia', 'Suspendido']:
        empleado.estado = nuevo_estado
        empleado.save()
        
        User = get_user_model()
        u = User.objects.filter(email=empleado.email).first()
        if u:
            u.estado = (nuevo_estado == 'Activo')
            u.save()
            
        messages.success(request, f"Estado cambiado a {nuevo_estado}")
    return redirect('empleados:editar_empleado', pk=pk)


@login_required
@require_safe
def servir_contrato_privado(request, filepath):
    """
    Solo GET.
    """
    filepath = filepath.strip('/')
    ruta_final = filepath

    if not private_storage.exists(ruta_final):
        if private_storage.exists(f'contratos/{ruta_final}'):
             ruta_final = f'contratos/{ruta_final}'
        else:
             raise Http404(f"El documento no se encuentra en: {ruta_final}")
        
    archivo = private_storage.open(ruta_final)
    return FileResponse(archivo)