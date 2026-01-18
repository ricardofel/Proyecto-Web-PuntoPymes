from datetime import date
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto
from solicitudes.models import SolicitudAusencia, TipoAusencia, RegistroVacaciones
from solicitudes.forms import SolicitudAusenciaForm

User = get_user_model()

class SolicitudesLogicWhiteBoxTests(TestCase):
    """
    Tests de lógica interna:
    - cálculo de días hábiles
    - saldo de vacaciones
    """

    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Mango Solicitudes", ruc="111")
        self.unidad = UnidadOrganizacional.objects.create(nombre="Tecnología", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Desarrollador", empresa=self.empresa)
        self.empleado = Empleado.objects.create(
            nombres="Mango", apellidos="Archimango", cedula="12345", email="mango@test.com",
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )
        self.tipo = TipoAusencia.objects.create(empresa=self.empresa, nombre="Vacaciones")

    def test_calculo_dias_habiles_excluye_fines_semana(self):
        print("\n📅 [TEST] Iniciando: test_calculo_dias_habiles_excluye_fines_semana")

        # Rango: 2026-01-16 (viernes) a 2026-01-19 (lunes)
        # Hábiles esperados: viernes (1) + lunes (1) => 2
        data = {
            'ausencia': self.tipo.id,
            'fecha_inicio': date(2026, 1, 16),
            'fecha_fin': date(2026, 1, 19),
            'motivo': "Descanso necesario"
        }

        form = SolicitudAusenciaForm(data=data, empleado=self.empleado)
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

        # El formulario asigna el valor al objeto en su validación/limpieza
        solicitud = form.save(commit=False)
        print(f"   ↳ Rango: 2026-01-16 al 2026-01-19. Días calculados: {solicitud.dias_habiles}")

        self.assertEqual(solicitud.dias_habiles, 2, "El cálculo de días hábiles no descontó el fin de semana.")
        print("     Exito: El algoritmo de días hábiles es preciso.")

    def test_propiedad_dias_disponibles_vacaciones(self):
        print("\n [TEST] Iniciando: test_propiedad_dias_disponibles_vacaciones")
        registro = RegistroVacaciones.objects.create(
            empresa=self.empresa, empleado=self.empleado, periodo="2025",
            dias_asignados=15.00, dias_tomados=5.50
        )
        print(f"   Asignados: 15, Tomados: 5.5. Disponibles: {registro.dias_disponibles}")
        self.assertEqual(float(registro.dias_disponibles), 9.50)
        print("     Exito: El cálculo de saldo de vacaciones es correcto.")


class SolicitudesViewWhiteBoxTests(TestCase):
    """
    Tests de vistas y flujo:
    - creación con adjuntos
    - aprobación por jefe
    - restricción de edición por estado
    """

    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Mango Corp", ruc="999")
        self.u = UnidadOrganizacional.objects.create(nombre="U", empresa=self.empresa)
        self.p = Puesto.objects.create(nombre="P", empresa=self.empresa)

        # Usuario empleado
        self.user_emp = User.objects.create_user(email='empleado@test.com', password='123')
        self.empleado = Empleado.objects.create(
            nombres="Juan", apellidos="Perez", email=self.user_emp.email, cedula="111",
            empresa=self.empresa, unidad_org=self.u, puesto=self.p, fecha_ingreso="2024-01-01"
        )
        self.user_emp.empleado = self.empleado
        self.user_emp.save()

        # Usuario jefe (superuser)
        self.user_jefe = User.objects.create_superuser(email='jefe@test.com', password='123')
        self.jefe = Empleado.objects.create(
            nombres="Gran", apellidos="Jefe", email=self.user_jefe.email, cedula="000",
            empresa=self.empresa, unidad_org=self.u, puesto=self.p, fecha_ingreso="2024-01-01"
        )
        self.user_jefe.empleado = self.jefe
        self.user_jefe.save()

        self.tipo = TipoAusencia.objects.create(empresa=self.empresa, nombre="Permiso")
        self.client = Client()

    def test_crear_solicitud_con_multiples_adjuntos(self):
        print("\n [TEST] Iniciando: test_crear_solicitud_con_multiples_adjuntos")
        self.client.force_login(self.user_emp)

        # Archivos simulados enviados en 'archivos_nuevos'
        file1 = SimpleUploadedFile("reposo.pdf", b"contenido_pdf", content_type="application/pdf")
        file2 = SimpleUploadedFile("receta.png", b"contenido_imagen", content_type="image/png")

        data = {
            'ausencia': self.tipo.id,
            'fecha_inicio': '2025-05-01',
            'fecha_fin': '2025-05-02',
            'motivo': "Cita médica",
            'archivos_nuevos': [file1, file2]
        }

        response = self.client.post(reverse('solicitudes:crear_solicitud'), data)

        self.assertEqual(response.status_code, 302)
        solicitud = SolicitudAusencia.objects.get(motivo="Cita médica")

        adjuntos_count = solicitud.adjuntos.count()
        print(f"   Solicitud creada con {adjuntos_count} adjuntos.")
        self.assertEqual(adjuntos_count, 2)
        print("     Exito: Los múltiples adjuntos se guardaron y vincularon correctamente.")

    def test_flujo_aprobacion_jefe(self):
        print("\n✅ [TEST] Iniciando: test_flujo_aprobacion_jefe")
        # Solicitud inicial en estado PENDIENTE
        solicitud = SolicitudAusencia.objects.create(
            empresa=self.empresa, empleado=self.empleado, ausencia=self.tipo,
            fecha_inicio="2025-06-01", fecha_fin="2025-06-02", motivo="Vacaciones",
            dias_habiles=2, estado=SolicitudAusencia.Estado.PENDIENTE
        )

        # Jefe registra aprobación
        self.client.force_login(self.user_jefe)
        url = reverse('solicitudes:responder_solicitudes', args=[solicitud.id])

        response = self.client.post(url, {
            'accion': 'aprobar',
            'comentario': 'Disfrute su descanso'
        })

        solicitud.refresh_from_db()
        print(f"   ↳ Acción: Aprobar. Estado final: {solicitud.estado}")

        self.assertEqual(solicitud.estado, SolicitudAusencia.Estado.APROBADO)
        self.assertEqual(solicitud.aprobaciones.count(), 1)
        self.assertEqual(solicitud.aprobaciones.first().comentario, 'Disfrute su descanso')
        print("     Exito: El flujo de aprobación y registro de historial funciona.")

    def test_seguridad_edicion_bloqueada_si_aprobada(self):
        print("\n🛡️ [TEST] Iniciando: test_seguridad_edicion_bloqueada_si_aprobada")
        # Solicitud en estado APROBADO: no debe ser editable por el empleado
        solicitud = SolicitudAusencia.objects.create(
            empresa=self.empresa, empleado=self.empleado, ausencia=self.tipo,
            fecha_inicio="2025-06-01", fecha_fin="2025-06-02", motivo="X",
            estado=SolicitudAusencia.Estado.APROBADO
        )

        self.client.force_login(self.user_emp)
        url = reverse('solicitudes:editar_solicitud', args=[solicitud.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        print("   ↳ El sistema bloqueó la edición de una solicitud aprobada.")
        print("     ✅ Éxito: Las reglas de integridad de estados están activas.")
