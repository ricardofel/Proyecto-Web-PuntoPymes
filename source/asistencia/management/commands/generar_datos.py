import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from empleados.models import Empleado
# Importamos el modelo correcto según tu archivo models.py
from asistencia.models import JornadaCalculada

class Command(BaseCommand):
    help = 'Genera datos falsos en JornadaCalculada para demos de ventas'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generando datos simulados para el calendario...")

        # 1. Configuración de fechas
        fin = timezone.now().date()
        inicio = fin - timedelta(days=30)
        
        # === NUEVO: BORRAR DATOS VIEJOS PRIMERO ===
        # Esto permite que cada vez que corras el script, los colores cambien
        self.stdout.write(f"Limpiando historial del {inicio} al {fin}...")
        JornadaCalculada.objects.filter(fecha__range=[inicio, fin]).delete()
        # ==========================================

        # 2. Obtener empleados activos
        empleados = Empleado.objects.filter(estado='Activo')

        if not empleados.exists():
            self.stdout.write(self.style.ERROR("No hay empleados activos. Crea empleados primero."))
            return

        registros_creados = 0

        # 3. Iterar por cada día
        dia_actual = inicio
        while dia_actual <= fin:
            # Saltamos fines de semana (Sábado=5, Domingo=6)
            if dia_actual.weekday() >= 5:
                dia_actual += timedelta(days=1)
                continue

            for emp in empleados:
                # Verificar si ya existe registro para no duplicar
                if JornadaCalculada.objects.filter(empleado=emp, fecha=dia_actual).exists():
                    continue

                # === LÓGICA DE COLORES PARA VENTAS ===
                # Weights: 85% Verde (Puntual), 10% Naranja (Atraso), 5% Rojo (Falta)
                opciones = [
                    JornadaCalculada.EstadoJornada.PUNTUAL, # Verde
                    JornadaCalculada.EstadoJornada.ATRASO,  # Naranja
                    JornadaCalculada.EstadoJornada.FALTA    # Rojo
                ]
                estado_elegido = random.choices(opciones, weights=[85, 10, 5])[0]

                # Variables iniciales
                entrada_dt = None
                salida_dt = None
                minutos_tardanza = 0
                minutos_trabajados = 0

                # Hora base de entrada esperada: 09:00 AM
                # Hora base de salida esperada: 18:00 PM

                if estado_elegido == JornadaCalculada.EstadoJornada.PUNTUAL:
                    # Llega entre 08:30 y 09:00
                    minutos_variacion = random.randint(-30, 0)
                    hora_entrada = (datetime.combine(dia_actual, time(9, 0)) + timedelta(minutes=minutos_variacion)).time()
                    
                    # Sale entre 18:00 y 18:30
                    hora_salida = (datetime.combine(dia_actual, time(18, 0)) + timedelta(minutes=random.randint(0, 30))).time()
                    
                    # Convertir a datetime aware (importante para Django)
                    entrada_dt = timezone.make_aware(datetime.combine(dia_actual, hora_entrada))
                    salida_dt = timezone.make_aware(datetime.combine(dia_actual, hora_salida))
                    
                    minutos_trabajados = 480 + random.randint(0, 30) # ~8 horas

                elif estado_elegido == JornadaCalculada.EstadoJornada.ATRASO:
                    # Llega entre 09:01 y 09:45
                    minutos_tardanza = random.randint(1, 45)
                    hora_entrada = (datetime.combine(dia_actual, time(9, 0)) + timedelta(minutes=minutos_tardanza)).time()
                    
                    # Sale normal
                    hora_salida = (datetime.combine(dia_actual, time(18, 0)) + timedelta(minutes=random.randint(0, 15))).time()

                    entrada_dt = timezone.make_aware(datetime.combine(dia_actual, hora_entrada))
                    salida_dt = timezone.make_aware(datetime.combine(dia_actual, hora_salida))
                    
                    minutos_trabajados = 480 - minutos_tardanza

                else: # FALTA
                    # No hay tiempos
                    entrada_dt = None
                    salida_dt = None
                    minutos_trabajados = 0
                    minutos_tardanza = 0

                # Crear el registro en JornadaCalculada
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

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se crearon {registros_creados} registros en JornadaCalculada.'))