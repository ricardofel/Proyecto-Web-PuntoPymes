# usuarios/views/usuarios_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from usuarios.models import Rol
from usuarios.decorators import solo_superusuario_o_admin_rrhh

# IMPORTANTE: Hemos agregado PerfilUsuarioForm a los imports
from ..forms import UsuarioForm, PerfilUsuarioForm

User = get_user_model()

@login_required
@solo_superusuario_o_admin_rrhh
def lista_usuarios(request):
    """
    Listado de usuarios con búsqueda y filtros por estado, rol y EMPRESA (Multi-tenant).
    """
    
    # 1. INICIAMOS EL QUERYSET BASE
    # Usamos select_related para optimizar la consulta a la BD
    usuarios = User.objects.select_related("empleado", "empleado__empresa").prefetch_related("roles_asignados").exclude(id=request.user.id)

    # 2. LOGICA DE FILTRADO MULTI-TENANT (LA CLAVE DEL ÉXITO 🔑)
    
    # CASO A: Superusuario Global
    if request.user.is_superuser:
        # Obtenemos la empresa seleccionada en el menú lateral (Middleware)
        empresa_actual = getattr(request, 'empresa_actual', None)
        
        if empresa_actual:
            # Filtramos usuarios cuyo EMPLEADO pertenezca a esa empresa
            usuarios = usuarios.filter(empleado__empresa=empresa_actual)
        else:
            # Si no hay empresa seleccionada, mostramos todos (o podrías no mostrar nada)
            pass

    # CASO B: Admin RRHH (No Superuser)
    elif hasattr(request.user, 'empleado') and request.user.empleado:
        # Filtramos estrictamente por la empresa del empleado logueado
        mi_empresa = request.user.empleado.empresa
        usuarios = usuarios.filter(empleado__empresa=mi_empresa)
    
    # CASO C: Usuario "Huérfano" (Sin empleado asociado)
    else:
        # Por seguridad, no le mostramos nada
        usuarios = usuarios.none()

    # 3. FILTROS DE INTERFAZ (Búsqueda, Estado, Rol)
    q = request.GET.get("q", "").strip()
    filtro_estado = request.GET.get("estado", "").strip()
    filtro_rol = request.GET.get("rol", "").strip()

    # Búsqueda por correo, nombre, apellido o cédula
    if q:
        usuarios = usuarios.filter(
            Q(email__icontains=q)
            | Q(empleado__nombres__icontains=q)
            | Q(empleado__apellidos__icontains=q)
            | Q(empleado__cedula__icontains=q) # Agregué cédula también
        )

    # Filtro por estado (activo / inactivo)
    if filtro_estado == "activo":
        usuarios = usuarios.filter(estado=True)
    elif filtro_estado == "inactivo":
        usuarios = usuarios.filter(estado=False)

    # Filtro por rol
    if filtro_rol:
        usuarios = usuarios.filter(roles_asignados__nombre=filtro_rol)

    # Ordenamiento final
    usuarios = usuarios.distinct().order_by('-fecha_creacion')

    # Roles disponibles para el combo de filtros
    roles = Rol.objects.filter(estado=True).order_by("nombre")

    # Enviamos la empresa actual al contexto por si quieres mostrarla en el título
    empresa_actual_ctx = getattr(request, 'empresa_actual', None)

    context = {
        "usuarios": usuarios,
        "titulo": "Gestión de Usuarios",
        "q": q,
        "filtro_estado": filtro_estado,
        "filtro_rol": filtro_rol,
        "roles": roles,
        "empresa_actual": empresa_actual_ctx
    }
    return render(request, "usuarios/lista_usuarios.html", context)


@login_required
@solo_superusuario_o_admin_rrhh
def gestionar_usuario(request, user_id=None):
    """
    Crear o editar un usuario (Admin/RRHH).
    - Si viene user_id => editar.
    - Si no viene => crear.
    """
    if user_id:
        usuario = get_object_or_404(User, pk=user_id)
        titulo = "Editar Usuario"
    else:
        usuario = None
        titulo = "Crear Nuevo Usuario"

    # 🛡️ Si el usuario objetivo es superuser y quien edita NO lo es → bloqueo
    if usuario and usuario.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "No tienes permisos para editar a un superadministrador del sistema.",
        )
        return redirect("usuarios:lista_usuarios")

    if request.method == "POST":
        form = UsuarioForm(
            request.POST,
            instance=usuario,
            usuario_actual=request.user,
        )
        if form.is_valid():
            form.save()
            mensaje = (
                "Usuario creado exitosamente."
                if usuario is None
                else "Usuario actualizado exitosamente."
            )
            messages.success(request, mensaje)
            return redirect("usuarios:lista_usuarios")
    else:
        form = UsuarioForm(instance=usuario, usuario_actual=request.user)

    context = {
        "form": form,
        "titulo": titulo,
    }
    return render(request, "usuarios/form_usuario.html", context)


# ==========================================
# NUEVA VISTA PARA "MI PERFIL"
# ==========================================

@login_required
def perfil_usuario(request):
    """
    Vista para que el usuario logueado gestione sus propios datos
    (foto y teléfono) sin permisos administrativos.
    """
    usuario = request.user
    
    if request.method == 'POST':
        # request.FILES es necesario para procesar la imagen subida
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=usuario)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado correctamente!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores indicados en el formulario.')
    else:
        form = PerfilUsuarioForm(instance=usuario)

    context = {
        'form': form,
        'usuario': usuario,
        'titulo': 'Mi Perfil'
    }
    return render(request, 'usuarios/perfil.html', context)