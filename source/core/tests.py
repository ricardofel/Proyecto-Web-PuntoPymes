from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.views.generic import ListView

from core.models import Empresa, UnidadOrganizacional
from core.middleware import EmpresaContextMiddleware
from core.mixins import FiltradoEmpresaMixin

User = get_user_model()


class CoreMiddlewareWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para EmpresaContextMiddleware.

    Objetivo:
    - Validar la prioridad de selección de empresa para superusuarios.
    - Regla esperada: el parámetro de URL tiene prioridad sobre la sesión (URL > Sesión).
    """

    def setUp(self):
        # Infraestructura base para pruebas de middleware.
        self.factory = RequestFactory()
        self.middleware = EmpresaContextMiddleware(get_response=lambda r: None)

        # Usuario superadmin para poder cambiar de empresa.
        # Nota: se crea con email/password y el flag is_superuser.
        self.superadmin = User.objects.create_user(
            email="admin@core.com",
            password="123",
            is_superuser=True,
        )

        # Dos empresas para validar cambio de contexto (A -> B).
        self.empresa_A = Empresa.objects.create(nombre_comercial="Empresa A", ruc="111", razon_social="A SA")
        self.empresa_B = Empresa.objects.create(nombre_comercial="Empresa B", ruc="222", razon_social="B SA")

    def _preparar_request(self, url_params={}):
        """
        Helper: arma un request con sesión y usuario autenticado.

        - url_params se envía como querystring (RequestFactory.get).
        - Se inyecta SessionMiddleware para habilitar request.session.
        """
        request = self.factory.get("/", url_params)
        request.user = self.superadmin

        # Inyectar soporte de sesión en el request creado por RequestFactory.
        middleware_session = SessionMiddleware(lambda r: None)
        middleware_session.process_request(request)
        request.session.save()
        return request

    def test_middleware_logica_prioridad_url_vs_session(self):
        print("\n[TEST] Iniciando: test_middleware_logica_prioridad_url_vs_session")
        print("   Objetivo: Validar que 'empresa_id' en la URL tiene prioridad sobre la sesión.")

        # Paso 1: contexto inicial vía sesión (sin parámetro en URL).
        request_1 = self._preparar_request()
        request_1.session["empresa_actual_id"] = self.empresa_A.id  # Simula sesión previa.

        # Ejecutar middleware (sin empresa_id en URL).
        self.middleware.process_request(request_1)

        # Validación: sin URL, debe respetar el valor de sesión.
        self.assertEqual(request_1.empresa_actual, self.empresa_A)
        print("   Paso 1: el middleware respetó la empresa desde la sesión.")

        # Paso 2: cambio de contexto mediante querystring ?empresa_id=<B>.
        request_2 = self._preparar_request({"empresa_id": self.empresa_B.id})
        request_2.session["empresa_actual_id"] = self.empresa_A.id  # Sesión anterior todavía en A.

        # Ejecutar middleware.
        self.middleware.process_request(request_2)

        # Validación: URL debe sobrescribir y actualizar sesión.
        self.assertEqual(request_2.empresa_actual, self.empresa_B, "La URL no tuvo prioridad sobre la sesión")
        self.assertEqual(
            request_2.session["empresa_actual_id"],
            self.empresa_B.id,
            "La sesión no se actualizó con el nuevo ID",
        )
        print("   Exito: la prioridad URL > Sesión funciona correctamente.")


class CoreMixinWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para FiltradoEmpresaMixin.

    Objetivo:
    - Asegurar multitenencia: las vistas deben filtrar por empresa_actual.
    - Comportamiento defensivo: si no hay empresa_actual, retornar QuerySet vacío.
    """

    class VistaDummy(FiltradoEmpresaMixin, ListView):
        """Vista mínima para probar el mixin de forma aislada."""
        model = UnidadOrganizacional
        object_list = []  # Requerido por ListView en algunos flujos internos.

    def setUp(self):
        self.user = User.objects.create_user(email="user@core.com", password="123")
        self.empresa_X = Empresa.objects.create(nombre_comercial="Empresa X", ruc="888", razon_social="X Corp")
        self.empresa_Y = Empresa.objects.create(nombre_comercial="Empresa Y", ruc="999", razon_social="Y Corp")

        # Datos: unidades en empresas distintas.
        self.unidad_X = UnidadOrganizacional.objects.create(nombre="Unidad X", empresa=self.empresa_X)
        self.unidad_Y = UnidadOrganizacional.objects.create(nombre="Unidad Y", empresa=self.empresa_Y)

    def test_get_queryset_aislamiento_datos(self):
        print("\n[TEST] Iniciando: test_get_queryset_aislamiento_datos")
        print("   Objetivo: verificar que el mixin aplica filter(empresa=empresa_actual).")

        # Simular request donde el middleware ya asignó empresa_actual.
        request = RequestFactory().get("/")
        request.user = self.user
        request.empresa_actual = self.empresa_X

        vista = self.VistaDummy()
        vista.request = request
        vista.kwargs = {}

        # Ejecución directa del método (caja blanca).
        queryset_resultado = vista.get_queryset()

        # Verificación de aislamiento de datos.
        print(f"   Total en DB: {UnidadOrganizacional.objects.count()}")
        print(f"   Total filtrado por mixin: {queryset_resultado.count()}")

        self.assertIn(self.unidad_X, queryset_resultado)
        self.assertNotIn(self.unidad_Y, queryset_resultado)
        self.assertEqual(queryset_resultado.count(), 1)

        # Verificación adicional: el SQL debe incluir el filtro por empresa_id.
        sql_query = str(queryset_resultado.query)
        self.assertIn("empresa_id", sql_query, "El QuerySet no contiene la cláusula WHERE empresa_id")
        print("   Exito: el mixin aplicó el filtro correctamente.")

    def test_get_queryset_defensivo_sin_empresa(self):
        print("\n[TEST] Iniciando: test_get_queryset_defensivo_sin_empresa")
        print("   Objetivo: si no existe empresa_actual, retornar QuerySet vacío (qs.none).")

        # Request sin empresa_actual (simula falla del middleware o sesión caducada).
        request = RequestFactory().get("/")
        request.user = self.user

        vista = self.VistaDummy()
        vista.request = request
        vista.kwargs = {}

        queryset_resultado = vista.get_queryset()

        # Debe retornar vacío, no explotar ni traer todos los registros.
        self.assertEqual(queryset_resultado.count(), 0, "Debería retornar QuerySet vacío por seguridad")
        print("   Exito: el comportamiento defensivo funciona.")
