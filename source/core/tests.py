from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.views.generic import ListView
from unittest.mock import MagicMock

# Importamos tus componentes del core
from core.models import Empresa, UnidadOrganizacional
from core.middleware import EmpresaContextMiddleware
from core.mixins import FiltradoEmpresaMixin

User = get_user_model()

class CoreMiddlewareWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para EmpresaContextMiddleware.
    Objetivo: Validar la lógica de prioridad (URL > Sesión) para Superadmins.
    """

    def setUp(self):
        # 1. Creamos infraestructura básica
        self.factory = RequestFactory()
        self.middleware = EmpresaContextMiddleware(get_response=lambda r: None)
        
        # 2. Creamos un Super Admin (Dios del sistema)
        # Nota: Usamos solo email/password como aprendimos antes
        self.superadmin = User.objects.create_user(
            email='admin@core.com', 
            password='123',
            is_superuser=True
        )

        # 3. Creamos dos empresas para probar el "viaje" entre ellas
        self.empresa_A = Empresa.objects.create(nombre_comercial="Empresa A", ruc="111", razon_social="A SA")
        self.empresa_B = Empresa.objects.create(nombre_comercial="Empresa B", ruc="222", razon_social="B SA")

    def _preparar_request(self, url_params={}):
        """Helper para armar un request con sesión y usuario"""
        request = self.factory.get('/', url_params)
        request.user = self.superadmin
        
        # Truco: Agregamos soporte de sesión al request mockeado
        middleware_session = SessionMiddleware(lambda r: None)
        middleware_session.process_request(request)
        request.session.save()
        return request

    def test_middleware_logica_prioridad_url_vs_session(self):
        print("\n🧠 [TEST] Iniciando: test_middleware_logica_prioridad_url_vs_session")
        print("   ↳ Objetivo: Validar que el parámetro ?empresa_id=X mata a la sesión guardada.")

        # PASO 1: Establecer contexto inicial (El admin está trabajando en Empresa A)
        request_1 = self._preparar_request()
        request_1.session['empresa_actual_id'] = self.empresa_A.id # Simulamos sesión previa
        
        # Ejecutamos middleware (sin param URL)
        self.middleware.process_request(request_1)
        
        # Validación Rama 1: Debe respetar la sesión si no hay URL
        self.assertEqual(request_1.empresa_actual, self.empresa_A)
        print("   ↳ Paso 1: El middleware respetó la empresa A desde la sesión.")

        # PASO 2: El cambio de contexto (El admin hace clic en Empresa B en el selector)
        # Esto envía ?empresa_id=ID_B en la URL
        request_2 = self._preparar_request({'empresa_id': self.empresa_B.id})
        request_2.session['empresa_actual_id'] = self.empresa_A.id # La sesión vieja decía A
        
        # Ejecutamos middleware
        self.middleware.process_request(request_2)

        # Validación Rama 2: La URL debe sobreescribir la sesión y actualizarla
        self.assertEqual(request_2.empresa_actual, self.empresa_B, "La URL no tuvo prioridad sobre la sesión")
        self.assertEqual(request_2.session['empresa_actual_id'], self.empresa_B.id, "La sesión no se actualizó con el nuevo ID")
        print("     ✅ Éxito: La lógica de cambio de empresa (URL Override) funciona correctamente.")


class CoreMixinWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para FiltradoEmpresaMixin.
    Objetivo: Asegurar que las vistas filtren datos (Multitenencia) o se bloqueen defensivamente.
    """

    class VistaDummy(FiltradoEmpresaMixin, ListView):
        """Vista falsa para probar el Mixin aisladamente"""
        model = UnidadOrganizacional
        object_list = [] # Necesario para ListView mockeado

    def setUp(self):
        self.user = User.objects.create_user(email='user@core.com', password='123')
        self.empresa_X = Empresa.objects.create(nombre_comercial="Empresa X", ruc="888", razon_social="X Corp")
        self.empresa_Y = Empresa.objects.create(nombre_comercial="Empresa Y", ruc="999", razon_social="Y Corp")

        # Datos: Creamos unidades en ambas empresas
        self.unidad_X = UnidadOrganizacional.objects.create(nombre="Unidad X", empresa=self.empresa_X)
        self.unidad_Y = UnidadOrganizacional.objects.create(nombre="Unidad Y", empresa=self.empresa_Y)

    def test_get_queryset_aislamiento_datos(self):
        print("\n🛡️ [TEST] Iniciando: test_get_queryset_aislamiento_datos")
        print("   ↳ Objetivo: Verificar que el Mixin inyecta el .filter(empresa=...) automáticamente.")

        # Preparar Request simulando que el Middleware ya hizo su trabajo
        request = RequestFactory().get('/')
        request.user = self.user
        request.empresa_actual = self.empresa_X # <-- El usuario está en Empresa X

        # Instanciar la vista dummy
        vista = self.VistaDummy()
        vista.request = request
        vista.kwargs = {}

        # Ejecución (Caja Blanca: llamamos directo a get_queryset)
        queryset_resultado = vista.get_queryset()

        # Verificación
        print(f"   ↳ Total en DB: {UnidadOrganizacional.objects.count()}")
        print(f"   ↳ Total filtrado por Mixin: {queryset_resultado.count()}")

        # Debe traer la unidad de X, pero NO la de Y
        self.assertIn(self.unidad_X, queryset_resultado)
        self.assertNotIn(self.unidad_Y, queryset_resultado)
        self.assertEqual(queryset_resultado.count(), 1)
        
        # Inspección profunda: Verificar que el SQL generado contiene el filtro
        sql_query = str(queryset_resultado.query)
        self.assertIn('empresa_id', sql_query, "El QuerySet no contiene la cláusula WHERE empresa_id")
        print("     ✅ Éxito: El Mixin aplicó el filtro de seguridad correctamente.")

    def test_get_queryset_defensivo_sin_empresa(self):
        print("\n🛡️ [TEST] Iniciando: test_get_queryset_defensivo_sin_empresa")
        print("   ↳ Objetivo: Verificar el 'retorno seguro' (qs.none) si falla la detección de empresa.")

        # Request SIN atributo empresa_actual (simulando error de middleware o sesión caducada)
        request = RequestFactory().get('/')
        request.user = self.user
        # NO seteamos request.empresa_actual (será None o inexistente)

        vista = self.VistaDummy()
        vista.request = request
        vista.kwargs = {}

        # Ejecución
        queryset_resultado = vista.get_queryset()

        # Verificación: Debe retornar vacío, no explotar ni traer todo
        self.assertEqual(queryset_resultado.count(), 0, "Debería retornar QuerySet vacío por seguridad")
        print("     ✅ Éxito: El mecanismo de defensa (Circuit Breaker) funcionó.")