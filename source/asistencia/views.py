import calendar
from datetime import date, datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from empleados.models import Empleado
from .models import JornadaCalculada

@login_required
def dashboard_asistencia_view(request, empleado_id=None):
    
    # ==============================================================================
    # 1. CONTROL DE ACCESO (Lógica de Roles)
    # ==============================================================================
    usuario = request.user
    
    es_jefe = (
        usuario.is_superuser or 
        getattr(usuario, 'es_admin_rrhh', False) or 
        getattr(usuario, 'es_superadmin_negocio', False)
    )

    if not es_jefe:
        return render(request, 'asistencia/registro_entradasalida.html')

    # ==============================================================================
    # 2. DETERMINAR EMPLEADO (Opción Trampa)
    # ==============================================================================
    
    if not empleado_id:
        empleado_id = request.GET.get('empleado_id')

    # Si el ID está vacío o es la opción por defecto, empleado será None
    empleado = None
    if empleado_id and empleado_id != "":
        empleado = get_object_or_404(Empleado, pk=empleado_id)

    # ==============================================================================
    # 3. DETERMINAR MES Y AÑO
    # ==============================================================================
    hoy = timezone.now().date()
    try:
        mes = int(request.GET.get('mes', hoy.month))
        anio = int(request.GET.get('anio', hoy.year))
    except (ValueError, TypeError):
        mes = hoy.month
        anio = hoy.year

    fecha_actual_obj = date(anio, mes, 1)
    
    # ==============================================================================
    # 4. CONSTRUIR CALENDARIO (Solo si hay un empleado seleccionado)
    # ==============================================================================
    semanas_datos = []
    
    if empleado:
        cal = calendar.Calendar(firstweekday=6)
        matriz_mes = cal.monthdayscalendar(anio, mes)
        
        # Obtener datos de asistencia
        jornadas = JornadaCalculada.objects.filter(
            empleado=empleado,
            fecha__year=anio,
            fecha__month=mes
        )
        
        datos_dias = {j.fecha.day: j for j in jornadas}
        
        for semana in matriz_mes:
            semana_lista = []
            for dia in semana:
                if dia == 0:
                    semana_lista.append(None)
                else:
                    jornada = datos_dias.get(dia)
                    estado_codigo = 'futuro' 
                    
                    if jornada:
                        estado_codigo = jornada.estado
                    elif date(anio, mes, dia) < hoy:
                        estado_codigo = 'sin_registro'
                    
                    semana_lista.append({
                        'numero': dia,
                        'estado': estado_codigo,
                        'objeto': jornada
                    })
            semanas_datos.append(semana_lista)

    # ==============================================================================
    # 5. NAVEGACIÓN Y CONTEXTO
    # ==============================================================================
    mes_anterior_date = fecha_actual_obj - timedelta(days=1)
    mes_siguiente_date = (fecha_actual_obj + timedelta(days=32)).replace(day=1)

    # Mantener el ID del empleado en los links de navegación si existe
    param_empleado = f"&empleado_id={empleado.id}" if empleado else ""

    context = {
        'empleado': empleado,
        'mes_actual': fecha_actual_obj.strftime("%B"),
        'anio_actual': anio,
        'calendario': semanas_datos,
        
        'link_anterior': f"?mes={mes_anterior_date.month}&anio={mes_anterior_date.year}{param_empleado}",
        'link_siguiente': f"?mes={mes_siguiente_date.month}&anio={mes_siguiente_date.year}{param_empleado}",
        
        'empleados_list': Empleado.objects.filter(estado='Activo') 
    }
    
    return render(request, 'asistencia/dashboard_asistencia.html', context)