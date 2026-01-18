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
@require_http_methods(["GET", "POST"])
def crear_empleado_view(request):
    # Obtenemos el contexto de la empresa desde el middleware
    empresa_actual = getattr(request, 'empresa_actual', None)

    if request.method == 'POST':
        # Pasamos empresa_actual al formulario para gestionar su visibilidad
        form = EmpleadoForm(request.POST, request.FILES, empresa_actual=empresa_actual)
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Creación del Empleado
                    empleado = form.save(commit=False)
                    if empresa_actual:
                        empleado.empresa = empresa_actual
                    empleado.save()
                    
                    # 2. Gestión del Usuario de Sistema
                    email = form.cleaned_data.get('email') or empleado.email
                    
                    if email:
                        User = get_user_model()
                        user = User.objects.filter(email=email).first()
                        
                        if not user:
                            # Creamos el usuario SIN el campo 'username' para evitar errores
                            password_acceso = get_random_string(length=12)
                            user = User.objects.create_user(
                                email=email, 
                                password=password_acceso, 
                                estado=True
                            )
                            messages.success(request, f"Usuario creado. Clave temporal: {password_acceso}")
                        else:
                            messages.info(request, "El empleado se ha vinculado a un usuario existente.")

                        # Vinculación bidireccional
                        user.empleado = empleado
                        user.save()

                        # 3. Asignación de Roles (Usando UsuarioRol)
                        if rol_id:
                            rol_obj = Rol.objects.filter(id=rol_id).first()
                        else:
                            rol_obj = Rol.objects.filter(nombre="Empleado").first()

                        if user and rol_obj:
                            # Limpieza y asignación
                            UsuarioRol.objects.filter(usuario=user).delete()
                            UsuarioRol.objects.create(usuario=user, rol=rol_obj)

                    else:
                        messages.warning(request, "Empleado registrado sin acceso al sistema (Falta email).")

                return redirect('empleados:lista_empleados')

            except Exception as e:
                messages.error(request, f"Error del sistema: {e}")
        else:
            messages.error(request, "El formulario contiene errores. Revise los campos.")
    
    else:
        # GET: Inicializamos el formulario con el contexto de la empresa
        form = EmpleadoForm(empresa_actual=empresa_actual)

    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles_disponibles
    })

@login_required
@require_http_methods(["GET", "POST"])
def editar_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    empresa_actual = getattr(request, 'empresa_actual', None)

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado, empresa_actual=empresa_actual)
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Actualizar datos del empleado
                    empleado = form.save()

                    # 2. Gestión del Usuario de Sistema
                    email = form.cleaned_data.get('email')
                    if email:
                        User = get_user_model()
                        user = getattr(empleado, 'usuario', None)
                        
                        # Si no tiene usuario vinculado, buscamos si existe uno suelto por email
                        if not user:
                            user = User.objects.filter(email=email).first()
                        
                        if user:
                            # Actualizar email si cambió
                            if user.email != email:
                                user.email = email
                                user.save()
                            
                            # Asegurar vinculación (OneToOne)
                            if not hasattr(user, 'empleado'):
                                user.empleado = empleado
                                user.save()

                            # 3. Actualizar Rol (Usando UsuarioRol explícito)
                            if rol_id:
                                rol_obj = Rol.objects.filter(id=rol_id).first()
                                if rol_obj:
                                    # Borramos roles viejos y ponemos el nuevo
                                    UsuarioRol.objects.filter(usuario=user).delete()
                                    UsuarioRol.objects.create(usuario=user, rol=rol_obj)

                    messages.success(request, "Empleado actualizado correctamente.")
                    return redirect('empleados:lista_empleados')

            except Exception as e:
                messages.error(request, f"Error al actualizar: {e}")
        else:
            messages.error(request, "Verifique los errores en el formulario.")
    
    else:
        # GET
        form = EmpleadoForm(instance=empleado, empresa_actual=empresa_actual)

    roles_disponibles = Rol.objects.filter(estado=True)
    
    # Pre-selección del rol actual en el HTML
    rol_actual_id = None
    if hasattr(empleado, 'usuario') and empleado.usuario:
        usuario_rol = UsuarioRol.objects.filter(usuario=empleado.usuario).first()
        if usuario_rol:
            rol_actual_id = usuario_rol.rol.id

    return render(request, 'empleados/editar_empleado.html', {
        'form': form,
        'empleado': empleado,
        'roles_disponibles': roles_disponibles,
        'rol_actual_id': rol_actual_id
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