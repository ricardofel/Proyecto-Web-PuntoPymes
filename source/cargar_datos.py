import random
from datetime import date, timedelta
from django.utils import timezone
from empleados.models import Empleado
from asistencia.models import JornadaCalculada

# --- BUCLE PARA TODOS LOS EMPLEADOS ---
todos = Empleado.objects.all()
print(f"Generando asistencias para {todos.count()} empleados...")

for empleado in todos:
    print(f" -> Procesando: {empleado.nombres} {empleado.apellidos}")

    # Calculamos fechas del mes actual
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)

    # Recorremos día a día
    for i in range((hoy - inicio_mes).days + 1):
        fecha_proceso = inicio_mes + timedelta(days=i)
        
        # Saltamos fines de semana
        if fecha_proceso.weekday() >= 5:
            continue

        # Decisión aleatoria
        azar = random.choice(['puntual', 'puntual', 'atraso', 'falta', 'permiso'])
        
        entrada = None
        salida = None
        estado = 'falta'
        min_tardanza = 0
        
        if azar == 'puntual':
            estado = 'puntual'
            entrada = timezone.datetime.combine(fecha_proceso, timezone.datetime.strptime("08:55", "%H:%M").time())
            salida = timezone.datetime.combine(fecha_proceso, timezone.datetime.strptime("18:05", "%H:%M").time())
        
        elif azar == 'atraso':
            estado = 'atraso'
            min_tardanza = 25
            entrada = timezone.datetime.combine(fecha_proceso, timezone.datetime.strptime("09:25", "%H:%M").time())
            salida = timezone.datetime.combine(fecha_proceso, timezone.datetime.strptime("18:00", "%H:%M").time())

        elif azar == 'permiso':
            estado = 'permiso'
        
        # Guardar
        JornadaCalculada.objects.update_or_create(
            empleado=empleado,
            fecha=fecha_proceso,
            defaults={
                'hora_primera_entrada': entrada,
                'hora_ultima_salida': salida,
                'estado': estado,
                'minutos_tardanza': min_tardanza,
                'minutos_trabajados': 480 if entrada else 0
            }
        )

print("¡Hecho! Todos los empleados tienen datos.")