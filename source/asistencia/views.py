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
    # 1. Determinar qué empleado estamos viendo
    
    # NUEVO: Si no viene el ID en la URL limpia, intentamos sacarlo de los parámetros GET (?empleado_id=5)
    if not empleado_id:
        empleado_id = request.GET.get('empleado_id')

    if empleado_id:
        # Si encontramos un ID (sea por URL o por GET), buscamos a ese empleado
        empleado = get_object_or_404(Empleado, pk=empleado_id)
    else:
        # Si no hay ID por ningún lado, intentamos mostrar el usuario logueado o el primero
        if hasattr(request.user, 'empleado'):
            empleado = request.user.empleado
        else:
            empleado = Empleado.objects.first() 

    # 2. Determinar Mes y Año (por GET o actual)
    hoy = timezone.now().date()
    try:
        mes = int(request.GET.get('mes', hoy.month))
        anio = int(request.GET.get('anio', hoy.year))
    except ValueError:
        mes = hoy.month
        anio = hoy.year

    # 3. Construir la estructura del Calendario
    cal = calendar.Calendar(firstweekday=6) # 6 = Domingo es el primer día
    matriz_mes = cal.monthdayscalendar(anio, mes)
    
    # 4. Obtener datos de asistencia de la BD
    jornadas = JornadaCalculada.objects.filter(
        empleado=empleado,
        fecha__year=anio,
        fecha__month=mes
    )
    
    datos_dias = {j.fecha.day: j for j in jornadas}
    
    # 5. Armar la data final para la plantilla
    semanas_datos = []
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
                
                info_dia = {
                    'numero': dia,
                    'estado': estado_codigo,
                    'objeto': jornada
                }
                semana_lista.append(info_dia)
        semanas_datos.append(semana_lista)

    # 6. Navegación Mes Anterior / Siguiente
    fecha_actual = date(anio, mes, 1)
    mes_anterior = (fecha_actual - timedelta(days=1))
    mes_siguiente = (fecha_actual + timedelta(days=32)).replace(day=1)

    # Construimos links que mantengan el empleado seleccionado
    param_empleado = f"&empleado_id={empleado.id}" if empleado else ""

    context = {
        'empleado': empleado,
        'mes_actual': fecha_actual.strftime("%B"),
        'anio_actual': anio,
        'calendario': semanas_datos,
        
        # Agregamos el param_empleado para que al cambiar de mes no se pierda el usuario
        'link_anterior': f"?mes={mes_anterior.month}&anio={mes_anterior.year}{param_empleado}",
        'link_siguiente': f"?mes={mes_siguiente.month}&anio={mes_siguiente.year}{param_empleado}",
        
        'empleados_list': Empleado.objects.filter(estado='Activo') 
    }
    
    return render(request, 'asistencia/dashboard_asistencia.html', context)