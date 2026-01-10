import os

# --- 1. Imports de Django ---
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

# --- 2. Imports del Core (Mixins y Lógica Global) ---
from core.mixins import FiltradoEmpresaMixin

# --- 3. Imports de Usuarios (Decoradores y Roles) ---
from usuarios.decorators import solo_superusuario_o_admin_rrhh
from usuarios.models import Rol, UsuarioRol

# --- 4. Imports Locales (Empleados) ---
from .models import Empleado, Contrato
from .forms import EmpleadoForm

# =========================================================
# VISTAS DE EMPLEADOS
# =========================================================

# 1. LISTA DE EMPLEADOS (Protegida y Filtrada)
@method_decorator(solo_superusuario_o_admin_rrhh, name='dispatch')
class ListaEmpleadosView(FiltradoEmpresaMixin, ListView):
    model = Empleado
    template_name = 'empleados/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10 

    def get_queryset(self):
        # 1. Obtenemos el QuerySet base (filtrado por empresa gracias al Mixin)
        qs = super().get_queryset()

        # 2. Aplicamos lógica de búsqueda (si el usuario escribió algo)
        busqueda = self.request.GET.get('q')
        if busqueda:
            qs = qs.filter(
                Q(nombres__icontains=busqueda) | 
                Q(apellidos__icontains=busqueda) |
                Q(cedula__icontains=busqueda)
            )
        
        return qs.order_by('-id')

# Aquí abajo irían tus otras vistas (Crear, Editar, Eliminar)
# Recuerda convertirlas también a Class Based Views si quieres usar el Mixin,
# o usar la lógica manual si prefieres mantenerlas como funciones por ahora.

# ---------------------------------------------------------
# 2. CREAR EMPLEADO
# ---------------------------------------------------------
def crear_empleado_view(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        
        # 1. Capturamos el Rol elegido en el HTML (Select manual)
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # A. Guardar Empleado 
                    # (Esto dispara el form.save() que convierte los checkboxes a texto "LUN,MAR...")
                    empleado = form.save()
                    
                    email = form.cleaned_data.get('email') or empleado.email
                    
                    if email:
                        User = get_user_model()
                        # Generamos la clave: PuntoPymes + Cédula (o 2025 si no hay cédula)
                        password_acceso = f"PuntoPymes{empleado.cedula or '2025'}"
                        
                        user = None
                        
                        # B. Gestión del Usuario (Crear o Vincular)
                        if User.objects.filter(email=email).exists():
                            # CASO 1: El usuario YA EXISTE -> Lo actualizamos
                            user = User.objects.get(email=email)
                            user.set_password(password_acceso)
                            user.estado = True 
                            
                            # Si tu modelo User tiene campo 'empleado', lo vinculamos
                            if hasattr(user, 'empleado'):
                                user.empleado = empleado
                            
                            user.save()
                            messages.success(request, f"Usuario vinculado. Clave actualizada: {password_acceso}")
                        else:
                            # CASO 2: Usuario NUEVO -> Lo creamos
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                password=password_acceso,
                                estado=True 
                            )
                            if hasattr(user, 'empleado'):
                                user.empleado = empleado
                            user.save()
                            messages.success(request, f"Usuario creado. Clave: {password_acceso}")

                        # C. ASIGNACIÓN DE ROL (Tabla intermedia UsuarioRol)
                        if user:
                            rol_seleccionado = None
                            if rol_id:
                                rol_seleccionado = Rol.objects.filter(id=rol_id).first()
                            
                            # Fallback: Si no hay rol seleccionado, buscar 'Empleado' por defecto
                            if not rol_seleccionado:
                                rol_seleccionado = Rol.objects.filter(nombre="Empleado").first()

                            if rol_seleccionado:
                                # Borramos roles previos para evitar duplicados
                                UsuarioRol.objects.filter(usuario=user).delete()
                                # Asignamos el nuevo
                                UsuarioRol.objects.create(usuario=user, rol=rol_seleccionado)

                    else:
                        messages.warning(request, "Empleado creado SIN usuario (falta email).")

                return redirect('empleados:lista_empleados')

            except Exception as e:
                messages.error(request, f"Error en el proceso: {e}")
        else:
             messages.error(request, "El formulario contiene errores. Revísalos abajo.")
    else:
        form = EmpleadoForm()

    # IMPORTANTE: Enviamos roles al template para llenar el <select>
    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles_disponibles
    })

# ---------------------------------------------------------
# 3. EDICIÓN
# ---------------------------------------------------------
def editar_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST':
        # Al editar, el form cargará los checkboxes marcados automáticamente
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos actualizados correctamente.")
            return redirect('empleados:lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado)

    # También enviamos roles aquí por si el HTML de edición los requiere
    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/editar_empleado.html', {
        'form': form, 
        'empleado': empleado,
        'roles_disponibles': roles_disponibles,
        'es_edicion': True
    })

# ---------------------------------------------------------
# 4. CONTRATOS
# ---------------------------------------------------------
def lista_contratos_view(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    contratos = Contrato.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    return render(request, 'empleados/lista_contratos.html', {'empleado': empleado, 'contratos': contratos})

# ---------------------------------------------------------
# 5. FOTO
# ---------------------------------------------------------
@require_POST
def actualizar_foto_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if 'foto' in request.FILES:
        # Borrado de foto anterior para no llenar el disco
        if empleado.foto and os.path.isfile(empleado.foto.path):
            try: os.remove(empleado.foto.path)
            except: pass
            
        empleado.foto = request.FILES['foto']
        empleado.save()
        messages.success(request, "Foto actualizada.")
    return redirect('empleados:editar_empleado', pk=pk)

# ---------------------------------------------------------
# 6. ESTADO
# ---------------------------------------------------------
@require_POST
def cambiar_estado_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    nuevo_estado = request.POST.get('nuevo_estado')
    
    if nuevo_estado in ['Activo', 'Inactivo', 'Licencia', 'Suspendido']:
        empleado.estado = nuevo_estado
        empleado.save()
        
        # Actualizar también el estado del usuario de sistema si existe
        # (Depende de si tu User tiene un campo 'empleado' vinculado o si lo buscas por email)
        User = get_user_model()
        usuario_asociado = User.objects.filter(email=empleado.email).first()
        
        if usuario_asociado:
            usuario_asociado.estado = (nuevo_estado == 'Activo')
            usuario_asociado.save()
            
        messages.success(request, f"Estado cambiado a {nuevo_estado}")
            
    return redirect('empleados:editar_empleado', pk=pk)