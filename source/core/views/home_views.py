from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps

# 1. IMPORTAMOS LOS MODELOS QUE VAMOS A CONTAR
from empleados.models import Empleado
from core.models import UnidadOrganizacional

@login_required
def dashboard_view(request):
    """
    Vista del Dashboard Principal.
    Muestra resumen filtrado por la empresa seleccionada (si aplica).
    """
    Notificacion = apps.get_model('notificaciones', 'Notificacion')
    
    # --- A. LÓGICA ORIGINAL (Notificaciones y Usuario) ---
    
    # 1. Notificaciones
    ultimas_notif = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]

    # 2. Roles reales de la base de datos (relación UsuarioRol)
    mis_roles = [ur.rol.nombre for ur in request.user.usuariorol_set.all()]

    # 3. Nombre para mostrar (Empleado o Email)
    try:
        # Intenta obtener datos del perfil de empleado
        nombre_display = f"{request.user.empleado.nombres} {request.user.empleado.apellidos}"
    except AttributeError:
        # Si es superuser o no tiene perfil, usa el email
        nombre_display = request.user.email

    # --- B. NUEVA LÓGICA (Contadores por Empresa) ---
    
    # 4. Obtenemos la empresa del Middleware (o del selector global)
    empresa = getattr(request, 'empresa_actual', None)
    
    total_empleados = 0
    total_unidades = 0

    if empresa:
        # Si hay una empresa seleccionada, filtramos los datos
        # Nota: Ajusta 'estado' según tus modelos ('Activo' para empleados, True para unidades)
        total_empleados = Empleado.objects.filter(empresa=empresa, estado='Activo').count()
        total_unidades = UnidadOrganizacional.objects.filter(empresa=empresa, estado=True).count()

    # --- C. CONTEXTO FINAL ---
    context = {
        'notificaciones_recientes': ultimas_notif,
        'mis_roles': mis_roles,
        'nombre_display': nombre_display,
        
        # Variables nuevas para el Dashboard
        'total_empleados': total_empleados,
        'total_unidades': total_unidades,
        'empresa_actual': empresa, 
    }
    
    return render(request, "core/dashboard.html", context)