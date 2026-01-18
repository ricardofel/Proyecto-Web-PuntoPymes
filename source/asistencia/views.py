import calendar
from datetime import date, datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST, require_safe
from django.http import JsonResponse

from empleados.models import Empleado
from .models import JornadaCalculada, EventoAsistencia

# redirección inicial según el rol del usuario
@login_required
@require_safe
def asistencia_home_view(request):
    usuario = request.user
    es_jefe = (
        usuario.is_superuser or 
        getattr(usuario, 'es_admin_rrhh', False) or 
        getattr(usuario, 'es_superadmin_negocio', False)
    )
    if es_jefe:
        return redirect('asistencia:dashboard')
    else:
        return redirect('asistencia:zona_marcaje')

@login_required
@require_safe
def zona_marcaje_view(request):
    return render(request, 'asistencia/registro_entradasalida.html')

# procesamiento de la marcación de asistencia
@login_required
@require_POST
def registrar_marca_view(request):
    usuario = request.user
    if not hasattr(usuario, 'empleado'):
        messages.error(request, "No tienes una ficha de empleado asignada.")
        return redirect('asistencia:zona_marcaje')
    
    empleado = usuario.empleado
    accion = request.POST.get('tipo_marca')
    ahora = timezone.localtime(timezone.now())
    hoy = ahora.date()

    tipo_map = {
        'entrada': EventoAsistencia.TipoEvento.CHECK_IN,
        'salida': EventoAsistencia.TipoEvento.CHECK_OUT,
        'pausa_in': EventoAsistencia.TipoEvento.PAUSA_IN,
        'pausa_out': EventoAsistencia.TipoEvento.PAUSA_OUT,
    }

    if accion not in tipo_map:
        messages.error(request, "Acción no válida.")
        return redirect('asistencia:zona_marcaje')

    EventoAsistencia.objects.create(
        empleado=empleado,
        tipo=tipo_map[accion],
        registrado_el=ahora,
        origen='web',
        ip_address=request.META.get('REMOTE_ADDR')
    )

    jornada, created = JornadaCalculada.objects.get_or_create(
        empleado=empleado,
        fecha=hoy
    )

    if accion == 'entrada':
        if not jornada.hora_primera_entrada:
            jornada.hora_primera_entrada = ahora
            
            hora_teorica_naive = datetime.combine(hoy, empleado.hora_entrada_teorica)
            hora_teorica_aware = timezone.make_aware(hora_teorica_naive, timezone.get_current_timezone())
            margen = timedelta(minutes=0) 

            if ahora > (hora_teorica_aware + margen):
                diferencia = ahora - hora_teorica_aware
                minutos_tarde = int(diferencia.total_seconds() / 60)
                jornada.minutos_tardanza = minutos_tarde
                jornada.estado = JornadaCalculada.EstadoJornada.ATRASO
                messages.warning(request, f"Entrada con {minutos_tarde} min de atraso.")
            else:
                jornada.minutos_tardanza = 0
                jornada.estado = JornadaCalculada.EstadoJornada.PUNTUAL
                messages.success(request, "Entrada puntual registrada.")
        else:
            messages.info(request, "Entrada registrada (ya existía).")

    elif accion == 'salida':
        jornada.hora_ultima_salida = ahora
        
        if jornada.hora_primera_entrada:
            tiempo_trabajado = ahora - jornada.hora_primera_entrada
            jornada.minutos_trabajados = int(tiempo_trabajado.total_seconds() / 60)
        else:
            jornada.minutos_trabajados = 0

        inicio_teorico = datetime.combine(hoy, empleado.hora_entrada_teorica)
        fin_teorico = datetime.combine(hoy, empleado.hora_salida_teorica)
        if fin_teorico < inicio_teorico:
            fin_teorico += timedelta(days=1)
        duracion_teorica = fin_teorico - inicio_teorico
        minutos_objetivo = int(duracion_teorica.total_seconds() / 60)

        if jornada.minutos_trabajados < (minutos_objetivo - 1):
            jornada.estado = JornadaCalculada.EstadoJornada.FALTA
            faltan = minutos_objetivo - jornada.minutos_trabajados
            messages.error(request, f"JORNADA INCOMPLETA (Faltaron {faltan} min).")
        elif jornada.minutos_tardanza > 0:
            jornada.estado = JornadaCalculada.EstadoJornada.ATRASO
            messages.warning(request, "Horas cumplidas, pero mantienes el atraso de entrada.")
        else:
            jornada.estado = JornadaCalculada.EstadoJornada.PUNTUAL
            messages.success(request, "¡Jornada perfecta! Salida registrada.")

    elif accion == 'pausa_in':
        messages.info(request, "Inicio de descanso registrado.")
    elif accion == 'pausa_out':
        messages.info(request, "Fin de descanso registrado.")

    jornada.save()
    return redirect('asistencia:zona_marcaje')

# panel de control y calendario de asistencia
@login_required
@require_safe
def dashboard_asistencia_view(request):
    usuario = request.user
    es_jefe = (
        usuario.is_superuser or 
        getattr(usuario, 'es_admin_rrhh', False) or 
        getattr(usuario, 'es_superadmin_negocio', False)
    )

    empresa_actual = getattr(request, 'empresa_actual', None)

    target_empleado = None
    lista_empleados = None
    
    if es_jefe and empresa_actual:
        lista_empleados = Empleado.objects.filter(empresa=empresa_actual, estado='Activo')
    
    if es_jefe:
        empleado_id = request.GET.get('empleado_id')
        if empleado_id:
            target_empleado = get_object_or_404(Empleado, pk=empleado_id, empresa=empresa_actual)
    else:
        if hasattr(usuario, 'empleado'):
            target_empleado = usuario.empleado
        else:
            messages.error(request, "Tu usuario no tiene una ficha de empleado asociada.")
            return redirect('core:home')

    hoy = timezone.now().date()
    try:
        mes = int(request.GET.get('mes', hoy.month))
        anio = int(request.GET.get('anio', hoy.year))
    except (ValueError, TypeError):
        mes = hoy.month
        anio = hoy.year

    fecha_actual_obj = date(anio, mes, 1)
    semanas_datos = []

    if target_empleado:
        cal = calendar.Calendar(firstweekday=6)
        matriz_mes = cal.monthdayscalendar(anio, mes)
        
        jornadas = JornadaCalculada.objects.filter(
            empleado=target_empleado,
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

    mes_anterior = fecha_actual_obj - timedelta(days=1)
    mes_siguiente = (fecha_actual_obj + timedelta(days=32)).replace(day=1)
    
    param_empleado = ""
    if es_jefe and target_empleado:
        param_empleado = f"&empleado_id={target_empleado.id}"

    context = {
        'empleado': target_empleado,
        'es_jefe': es_jefe,
        'mes_actual': fecha_actual_obj.strftime("%B"),
        'anio_actual': anio,
        'calendario': semanas_datos,
        'link_anterior': f"?mes={mes_anterior.month}&anio={mes_anterior.year}{param_empleado}",
        'link_siguiente': f"?mes={mes_siguiente.month}&anio={mes_siguiente.year}{param_empleado}",
        'empleados_list': lista_empleados, 
        'empresa_actual': empresa_actual
    }
    
    return render(request, 'asistencia/dashboard_asistencia.html', context)

@login_required
@require_safe
def obtener_detalle_dia_view(request):
    empleado_id = request.GET.get('empleado_id')
    fecha_str = request.GET.get('fecha')
    
    if not empleado_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    empresa_actual = getattr(request, 'empresa_actual', None)
    
    eventos = EventoAsistencia.objects.filter(
        empleado_id=empleado_id,
        empleado__empresa=empresa_actual,
        registrado_el__date=fecha_str
    ).order_by('registrado_el')
    
    data = []
    for e in eventos:
        color = "gray"
        if e.tipo == EventoAsistencia.TipoEvento.CHECK_IN:
            color = "green"
        elif e.tipo == EventoAsistencia.TipoEvento.CHECK_OUT:
            color = "red"
        elif e.tipo == EventoAsistencia.TipoEvento.PAUSA_IN:
            color = "blue"
        elif e.tipo == EventoAsistencia.TipoEvento.PAUSA_OUT:
            color = "orange"

        hora_local = timezone.localtime(e.registrado_el)

        data.append({
            'hora': hora_local.strftime('%I:%M %p'),
            'tipo_legible': e.get_tipo_display(),
            'color': color,
            'origen': e.origen
        })
        
    return JsonResponse({'eventos': data})