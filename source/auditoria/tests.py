from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from auditoria.models import LogAuditoria
from auditoria.middleware import AuditoriaMiddleware, _thread_locals
from auditoria.constants import AccionesLog

# Modelo de usuario configurado en el proyecto
User = get_user_model()


class AuditoriaCoreWhiteBoxTests(TestCase):
    """
    Tests de caja blanca para el núcleo: middleware y señales.
    Verifica captura de usuario en thread-local y registro automático de eventos.
    """

    def setUp(self):
        self.auditor = User.objects.create_user(email='auditor@test.com', password='123')
        self.victima_email = 'victima@test.com'

    def test_middleware_gestion_hilos(self):
        print("\n[TEST] test_middleware_gestion_hilos")
        print("  Objetivo: validar que el middleware limpia el usuario del hilo al finalizar.")

        # Simula una petición entrante con usuario autenticado
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.auditor

        # Simula la vista: dentro del procesamiento el usuario debe estar disponible en thread-local
        def get_response_mock(req):
            usuario_actual = getattr(_thread_locals, 'user', None)
            self.assertEqual(usuario_actual, self.auditor, "El middleware no inyectó al usuario en el hilo")
            return "Respuesta OK"

        # Ejecuta el middleware (probando __call__)
        middleware = AuditoriaMiddleware(get_response_mock)
        middleware(request)
        print("  Paso: middleware ejecutado.")

        # Al finalizar, el thread-local no debe quedar contaminado
        usuario_residual = getattr(_thread_locals, 'user', None)
        self.assertIsNone(usuario_residual)
        print("  OK: thread-local limpiado.")

    def test_signal_integracion_completa(self):
        print("\n[TEST] test_signal_integracion_completa")
        print("  Objetivo: verificar que al crear un User se genera un LogAuditoria vía señal.")

        # Simula contexto de middleware: tests no pasan por middleware real
        _thread_locals.user = self.auditor

        # Crear usuario dispara post_save en app de usuarios (según configuración del proyecto)
        User.objects.create_user(email=self.victima_email, password='123')
        print("  Paso: usuario creado.")

        # Limpieza de thread-local
        _thread_locals.user = None

        # Verificación: existe log con autoría del auditor
        log = LogAuditoria.objects.filter(
            accion=AccionesLog.CREAR,
            modelo='USUARIO',
            usuario=self.auditor
        ).first()

        self.assertIsNotNone(log, "No se creó el registro de auditoría automático")
        self.assertIn(self.victima_email, log.detalle, "El detalle del log no contiene el ID/Email del objeto creado")
        print("  OK: log creado y atribuido correctamente.")


class AuditoriaViewWhiteBoxTests(TestCase):
    """
    Tests de caja blanca para la vista del dashboard.
    Valida control de acceso y filtrado de búsqueda.
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='123',
            is_superuser=True,
            is_staff=True
        )
        self.client = Client()
        self.client.force_login(self.admin)

    def test_dashboard_filtro_busqueda(self):
        print("\n[TEST] test_dashboard_filtro_busqueda")
        print("  Objetivo: validar que el parámetro 'q' filtra resultados en el dashboard.")

        # Datos de prueba
        LogAuditoria.objects.create(modulo='TEST', accion='X', detalle='Error crítico en servidor')
        LogAuditoria.objects.create(modulo='TEST', accion='X', detalle='Actualización de perfil')
        LogAuditoria.objects.create(modulo='TEST', accion='X', detalle='Login exitoso')

        url = reverse('auditoria:dashboard')
        response = self.client.get(url, {'q': 'crítico'})
        print("  Paso: búsqueda ejecutada con q='crítico'.")

        logs_en_contexto = response.context['page_obj'].object_list

        self.assertEqual(len(logs_en_contexto), 1, "El filtro debería traer solo 1 resultado")
        self.assertEqual(logs_en_contexto[0].detalle, 'Error crítico en servidor')
        print("  OK: filtro aplicado correctamente.")

    def test_acceso_denegado_no_superuser(self):
        print("\n[TEST] test_acceso_denegado_no_superuser")
        print("  Objetivo: validar restricción de acceso a usuarios no superusuario.")

        mortal = User.objects.create_user(email='mortal@test.com', password='123', is_superuser=False)
        self.client.force_login(mortal)

        url = reverse('auditoria:dashboard')
        response = self.client.get(url)

        # Dependiendo del decorador, puede devolver 403 o redirigir (302)
        print(f"  Status: {response.status_code}")

        if response.status_code in [403, 302]:
            print("  OK: acceso restringido.")
        else:
            self.fail(f"Fallo de seguridad: usuario normal entró con status {response.status_code}")
