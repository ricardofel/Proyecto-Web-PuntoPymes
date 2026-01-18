import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from empleados.models import Empleado
from asistencia.models import JornadaCalculada

class Command(BaseCommand):
    help = 'Genera datos falsos en JornadaCalculada para demos de ventas'

    def handle(self, *args, **kwargs):
        # configuración de rango de fechas
        fin = timezone.now().date()
        inicio = fin - timedelta(days=30)
        
        # limpieza de historial previo en el rango seleccionado
        JornadaCalculada.objects.filter(fecha__range=[inicio, fin]).delete()

        empleados = Empleado.objects.filter(estado='Activo')

        if not empleados.exists():
            self.stdout.write(self.style.ERROR("No hay empleados activos"))
            return

        registros_creados = 0
        dia_actual = inicio

        # iteración por días omitiendo fines de semana
        while dia_actual <= fin:
            if dia_actual.weekday() >= 5:
                dia_actual += timedelta(days=1)
                continue

            for emp in empleados:
                if JornadaCalculada.objects.filter(empleado=emp, fecha=dia_actual).exists():
                    continue

                # determinación aleatoria del estado de asistencia
                opciones = [
                    JornadaCalculada.EstadoJornada.PUNTUAL, 
                    JornadaCalculada.EstadoJornada.ATRASO, 
                    JornadaCalculada.EstadoJornada.FALTA 
                ]
                estado_elegido = random.choices(opciones, weights=[85, 10, 5])[0]

                entrada_dt = None
                salida_dt = None
                minutos_tardanza = 0
                minutos_trabajados = 0

                # cálculo de horarios y tiempos según el estado
                if estado_elegido == JornadaCalculada.EstadoJornada.PUNTUAL:
                    minutos_variacion = random.randint(-30, 0)
                    hora_entrada = (datetime.combine(dia_actual, time(9, 0)) + timedelta(minutes=minutos_variacion)).time()
                    hora_salida = (datetime.combine(dia_actual, time(18, 0)) + timedelta(minutes=random.randint(0, 30))).time()
                    
                    entrada_dt = timezone.make_aware(datetime.combine(dia_actual, hora_entrada))
                    salida_dt = timezone.make_aware(datetime.combine(dia_actual, hora_salida))
                    minutos_trabajados = 480 + random.randint(0, 30)

                elif estado_elegido == JornadaCalculada.EstadoJornada.ATRASO:
                    minutos_tardanza = random.randint(1, 45)
                    hora_entrada = (datetime.combine(dia_actual, time(9, 0)) + timedelta(minutes=minutos_tardanza)).time()
                    hora_salida = (datetime.combine(dia_actual, time(18, 0)) + timedelta(minutes=random.randint(0, 15))).time()

                    entrada_dt = timezone.make_aware(datetime.combine(dia_actual, hora_entrada))
                    salida_dt = timezone.make_aware(datetime.combine(dia_actual, hora_salida))
                    minutos_trabajados = 480 - minutos_tardanza

                # creación del registro en base de datos
                JornadaCalculada.objects.create(
                    empleado=emp,
                    fecha=dia_actual,
                    hora_primera_entrada=entrada_dt,
                    hora_ultima_salida=salida_dt,
                    minutos_trabajados=minutos_trabajados,
                    minutos_tardanza=minutos_tardanza,
                    estado=estado_elegido
                )
                registros_creados += 1

            dia_actual += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Generación completada. Registros creados: {registros_creados}'))