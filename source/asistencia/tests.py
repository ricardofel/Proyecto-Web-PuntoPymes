from django.test import TestCase
from django.utils import timezone
from datetime import datetime, time
from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto
from asistencia.models import JornadaCalculada

class AsistenciaSemaforoTest(TestCase):
    def test_calculo_estado_automatico(self):
        """
        Prueba que el sistema asigne el estado correcto (Puntual, Atraso, Incompleto)
        automáticamente al guardar la jornada.
        """
        print("\n>>> EJECUTANDO PRUEBA ASISTENCIA...")

        # 1. Preparar (Arrange) - Crear al empleado
        empresa = Empresa.objects.create(nombre_comercial="Mango Time", razon_social="M Time S.A.", ruc="1111111111001", zona_horaria="America/Guayaquil")
        unidad = UnidadOrganizacional.objects.create(empresa=empresa, nombre="RRHH")
        puesto = Puesto.objects.create(empresa=empresa, nombre="Asistente")
        
        empleado = Empleado.objects.create(
            empresa=empresa, unidad_org=unidad, puesto=puesto,
            nombres="Ana", apellidos="Lopez", cedula="0101010101",
            email="ana@mango.com", fecha_ingreso="2025-01-01"
        )

        # 2. Caso A: Solo marcó entrada (Sin atraso)
        # Debería estar "INCOMPLETO" (Gris) porque aún no sale
        jornada = JornadaCalculada.objects.create(
            empleado=empleado,
            fecha="2025-02-01",
            hora_primera_entrada=timezone.now(),
            minutos_tardanza=0
        )
        self.assertEqual(jornada.estado, JornadaCalculada.EstadoJornada.INCOMPLETO)
        print("   -> Caso Entrada sola: OK (Incompleto)")

        # 3. Caso B: Marcó entrada PERO llegó tarde
        # Debería marcar "ATRASO" (Naranja) inmediatamente
        jornada.minutos_tardanza = 15 # 15 min tarde
        jornada.save() # El método save() recalcula
        self.assertEqual(jornada.estado, JornadaCalculada.EstadoJornada.ATRASO)
        print("   -> Caso Atraso detectado: OK (Atraso)")

        # 4. Caso C: Marcó Salida y fue Puntual
        # Debería marcar "PUNTUAL" (Verde)
        jornada.minutos_tardanza = 0
        jornada.hora_ultima_salida = timezone.now()
        jornada.save()
        self.assertEqual(jornada.estado, JornadaCalculada.EstadoJornada.PUNTUAL)
        print("   -> Caso Jornada perfecta: OK (Puntual)")

        print(f"✅ ASISTENCIA TEST ÉXITO: El semáforo de estados funciona correctamente.")