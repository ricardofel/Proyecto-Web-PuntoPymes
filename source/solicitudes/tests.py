from django.test import TestCase
from datetime import date
from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto
from solicitudes.models import SolicitudAusencia, TipoAusencia

class SolicitudWorkflowTest(TestCase):
    def test_creacion_solicitud_estado_inicial(self):
        """
        Prueba que al crear una solicitud, esta nazca en estado 'PENDIENTE'
        y se asocie correctamente al tipo de ausencia.
        """
        print("\n>>> EJECUTANDO PRUEBA SOLICITUDES...")

        # 1. Preparar (Arrange) - La infraestructura necesaria
        empresa = Empresa.objects.create(
            nombre_comercial="Mango Vacations", 
            razon_social="Mango V S.A.", 
            ruc="1790011001001",
            zona_horaria="America/Guayaquil"
        )
        
        unidad = UnidadOrganizacional.objects.create(empresa=empresa, nombre="Ventas")
        puesto = Puesto.objects.create(empresa=empresa, nombre="Vendedor")
        
        empleado = Empleado.objects.create(
            empresa=empresa, unidad_org=unidad, puesto=puesto,
            nombres="Pedro", apellidos="Picapiedra", cedula="1100220033",
            email="pedro@mango.com", fecha_ingreso=date(2024, 1, 1)
        )

        # Crear el "Menú" de ausencias (ej: Vacaciones, Permiso Médico)
        tipo_vacaciones = TipoAusencia.objects.create(
            empresa=empresa,
            nombre="Vacaciones",
            afecta_sueldo=True
        )

        # 2. Actuar (Act) - El empleado pide vacaciones
        solicitud = SolicitudAusencia.objects.create(
            empresa=empresa,
            empleado=empleado,
            ausencia=tipo_vacaciones,
            fecha_inicio=date(2025, 5, 1),
            fecha_fin=date(2025, 5, 5),
            dias_habiles=3,
            motivo="Viaje a la playa"
        )

        # 3. Verificar (Assert)
        # Debe nacer PENDIENTE (nadie la ha aprobado aún)
        self.assertEqual(solicitud.estado, SolicitudAusencia.Estado.PENDIENTE)
        
        # Verificar que se relacionó con el tipo correcto
        self.assertEqual(solicitud.ausencia.nombre, "Vacaciones")

        print(f"✅ SOLICITUDES TEST ÉXITO: La solicitud de {empleado.nombres} se creó en estado {solicitud.estado}.")