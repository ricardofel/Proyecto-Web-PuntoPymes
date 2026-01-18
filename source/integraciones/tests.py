import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from integraciones.models import IntegracionErp, Webhook
from integraciones.constants import EstadoIntegracion, EventosWebhook
from integraciones.services.integracion_service import IntegracionService

from empleados.models import Empleado, Puesto
from core.models import Empresa, UnidadOrganizacional
from solicitudes.models import SolicitudAusencia, TipoAusencia

import talenttrack.api_router


User = get_user_model()


class IntegracionServiceWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para servicios externos usando mocks.
    """

    def setUp(self):
        self.erp = IntegracionErp.objects.create(
            nombre="SAP Test",
            url_api="https://api.fake.com/status",
            api_key="123",
        )

    @patch("integraciones.services.integracion_service.requests.get")
    def test_probar_conexion_erp_logica_estados(self, mock_get):
        print("\n[TEST] Iniciando: test_probar_conexion_erp_logica_estados")

        # Caso 1: HTTP 200.
        mock_response_ok = MagicMock()
        mock_response_ok.status_code = 200
        mock_response_ok.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response_ok

        exito, msg = IntegracionService.probar_conexion_erp(self.erp)

        self.erp.refresh_from_db()
        print(f"   Caso 200 OK -> Estado DB: {self.erp.estado_sincronizacion}")
        self.assertTrue(exito)
        self.assertEqual(self.erp.estado_sincronizacion, EstadoIntegracion.EXITOSO)

        # Caso 2: HTTP 500.
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_get.return_value = mock_response_fail

        exito_fail, msg_fail = IntegracionService.probar_conexion_erp(self.erp)

        self.erp.refresh_from_db()
        print(f"   Caso 500 Error -> Estado DB: {self.erp.estado_sincronizacion}")
        self.assertFalse(exito_fail)
        self.assertEqual(self.erp.estado_sincronizacion, EstadoIntegracion.ERROR)

        print("   Exito: la lógica de estados de conexión funciona.")


class IntegracionApiWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para endpoints API.
    """

    def setUp(self):
        self.client = Client()

        # Integración activa con API key válida.
        self.api_key_secreta = "k2-secret-key-123"
        self.erp = IntegracionErp.objects.create(
            nombre="ERP Externo",
            url_api="http://localhost",
            api_key=self.api_key_secreta,
            activo=True,
        )

        # Objetos base requeridos por la lógica del servicio (IDs fijos).
        self.empresa = Empresa.objects.create(id=1, nombre_comercial="Empresa Default", ruc="111")
        self.unidad = UnidadOrganizacional.objects.create(id=1, nombre="Unidad Default", empresa=self.empresa)
        self.puesto = Puesto.objects.create(id=1, nombre="Puesto Default", empresa=self.empresa)

    def test_importar_empleados_api_logica_masiva(self):
        print("\n[TEST] Iniciando: test_importar_empleados_api_logica_masiva")
        print("   Objetivo: validar procesamiento masivo y asignación de IDs por defecto.")

        payload = {
            "empleados": [
                {
                    "nombres": "API User",
                    "apellidos": "Test",
                    "email": "api@test.com",
                    "cedula": "555555",
                    "fecha_ingreso": "2025-01-01",
                    "fecha_nacimiento": "1990-01-01",
                },
                {
                    "nombres": "User Error",
                    "email": "",
                },
            ]
        }

        try:
            url = reverse("integracionerp-importar-empleados")
        except Exception:
            url = "/api/v1/integraciones/erp/importar_empleados/"
        print(f"   URL generada: {url}")

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_API_KEY=self.api_key_secreta,
        )

        try:
            data_resp = response.json()
        except json.JSONDecodeError:
            self.fail(f"Respuesta no JSON: {response.content}")

        print(f"   Respuesta API: {data_resp}")

        if "creados" in data_resp:
            self.assertEqual(data_resp["creados"], 1)

            nuevo_emp = Empleado.objects.get(email="api@test.com")
            self.assertEqual(nuevo_emp.empresa_id, 1)
            self.assertEqual(nuevo_emp.puesto_id, 1)
            print("   Exito: la API autenticó y procesó el JSON correctamente.")
        else:
            self.fail(f"Fallo en API. Error devuelto: {data_resp.get('error', 'Desconocido')}")


class IntegracionSignalWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para signals y webhooks.
    """

    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Test Corp", ruc="9090")
        self.unidad = UnidadOrganizacional.objects.create(nombre="U", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="P", empresa=self.empresa)
        self.empleado = Empleado.objects.create(
            nombres="Web",
            apellidos="Hook",
            email="hook@test.com",
            cedula="888",
            empresa=self.empresa,
            unidad_org=self.unidad,
            puesto=self.puesto,
            fecha_ingreso="2024-01-01",
        )

        self.webhook = Webhook.objects.create(
            nombre="Slack RRHH",
            evento=EventosWebhook.SOLICITUD_APROBADA,
            url_destino="https://slack.com/api/webhook",
            activo=True,
        )

        self.tipo_ausencia = TipoAusencia.objects.create(nombre="Vacaciones", empresa=self.empresa)

    @patch("integraciones.services.integracion_service.IntegracionService.disparar_webhook")
    def test_signal_webhook_nuevo_permiso(self, mock_disparar):
        print("\n[TEST] Iniciando: test_signal_webhook_nuevo_permiso")
        print("   Objetivo: verificar que el signal llama al servicio de webhook.")

        SolicitudAusencia.objects.create(
            empleado=self.empleado,
            empresa=self.empresa,
            ausencia=self.tipo_ausencia,
            fecha_inicio="2025-05-01",
            fecha_fin="2025-05-05",
            motivo="Descanso",
            dias_habiles=3,
        )

        if mock_disparar.called:
            print("   El servicio de webhook fue invocado.")
            args, _ = mock_disparar.call_args
            webhook_llamado = args[0]
            payload = args[1]

            self.assertEqual(webhook_llamado, self.webhook)
            self.assertEqual(payload["evento"], "NUEVA_SOLICITUD")
            self.assertIn("Web Hook", payload["empleado"])
        else:
            self.fail("El signal no disparó el webhook (mock_disparar no fue llamado).")

        print("   Exito: la integración entre Solicitudes y Webhooks funciona.")
