from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.contrib import messages

from empleados.models import Empleado
from core.models import UnidadOrganizacional, Empresa

@login_required
def fijar_entorno_modal(request, empresa_id):
    """
    Vista llamada desde el modal para fijar la empresa en la sesión.
    """
    if request.user.is_superuser:
        empresa = get_object_or_404(Empresa, pk=empresa_id)
        
        request.session['empresa_entorno_id'] = empresa.id
        
        request.session.modified = True
        request.session.save()
        
        messages.success(request, f"Entorno cambiado a: {empresa.nombre_comercial}")
    
    return redirect('dashboard')

@login_required
def dashboard_view(request):
    """
    Dashboard principal.

    Muestra información del usuario, notificaciones recientes y
    contadores filtrados por la empresa seleccionada a nivel global.
    """

    # Modelo cargado dinámicamente para evitar dependencias circulares.
    Notificacion = apps.get_model("notificaciones", "Notificacion")

    # Notificaciones recientes del usuario.
    ultimas_notif = (
        Notificacion.objects
        .filter(usuario=request.user)
        .order_by("-fecha_creacion")[:5]
    )

    # Roles asociados al usuario (relación UsuarioRol -> Rol).
    mis_roles = [ur.rol.nombre for ur in request.user.usuariorol_set.all()]

    # Nombre a mostrar: perfil de empleado o, en su defecto, email.
    try:
        nombre_display = f"{request.user.empleado.nombres} {request.user.empleado.apellidos}"
    except AttributeError:
        nombre_display = request.user.email

    # Empresa activa definida por el middleware.
    empresa = getattr(request, "empresa_actual", None)

    total_empleados = 0
    total_unidades = 0

    # Contadores filtrados por empresa (si existe contexto).
    if empresa:
        total_empleados = Empleado.objects.filter(
            empresa=empresa,
            estado="Activo",
        ).count()
        total_unidades = UnidadOrganizacional.objects.filter(
            empresa=empresa,
            estado=True,
        ).count()

    context = {
        "notificaciones_recientes": ultimas_notif,
        "mis_roles": mis_roles,
        "nombre_display": nombre_display,
        "total_empleados": total_empleados,
        "total_unidades": total_unidades,
        "empresa_actual": empresa,
    }

    return render(request, "core/dashboard.html", context)
