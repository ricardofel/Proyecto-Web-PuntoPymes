import threading
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from auditoria.models import LogAuditoria
from auditoria.middleware import AuditoriaMiddleware, _thread_locals
from auditoria.constants import AccionesLog

# Obtenemos tu modelo de usuario personalizado
User = get_user_model()

class AuditoriaCoreWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para el núcleo lógico: Middleware y Señales.
    Objetivo: Verificar que el sistema captura al usuario y registra eventos automáticamente.
    """

    def setUp(self):
        # Usuario auditor (quien hace la acción)
        self.auditor = User.objects.create_user(email='auditor@test.com', password='123')
        # Usuario víctima (objeto a manipular)
        self.victima_email = 'victima@test.com'

    def test_middleware_gestion_hilos(self):
        print("\n🕵️ [TEST] Iniciando: test_middleware_gestion_hilos")
        print("   ↳ Objetivo: Validar que el Middleware limpia el usuario del hilo (Thread Local) al terminar.")
        
        # 1. Simulamos una petición entrante
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.auditor # Simulamos que Django ya autenticó al usuario
        
        # 2. Definimos una respuesta dummy (lo que hace la vista)
        def get_response_mock(req):
            # DENTRO de la vista: El usuario debería estar disponible globalmente
            usuario_actual = getattr(_thread_locals, 'user', None)
            self.assertEqual(usuario_actual, self.auditor, "El middleware no inyectó al usuario en el hilo")
            return "Respuesta OK"

        # 3. Ejecutamos el Middleware (Caja Blanca: probamos el método __call__)
        middleware = AuditoriaMiddleware(get_response_mock)
        middleware(request)
        print("   ↳ Paso 1: Middleware ejecutado correctamente.")

        # 4. Verificación CRÍTICA (Bloque finally)
        # Al salir del middleware, la variable global debe estar vacía para no contaminar otras peticiones
        usuario_residual = getattr(_thread_locals, 'user', None)
        self.assertIsNone(usuario_residual)
        print("     ✅ Éxito: El middleware limpió el rastro del hilo (evitó 'memory leaks' de identidad).")

    def test_signal_integracion_completa(self):
        print("\n🕵️ [TEST] Iniciando: test_signal_integracion_completa")
        print("   ↳ Objetivo: Verificar que al crear un User, la señal dispara y crea un LogAuditoria.")

        # PREPARACIÓN (Simulamos el contexto del middleware manualmente)
        # Esto es necesario porque los tests corren sin pasar por el middleware real
        _thread_locals.user = self.auditor

        # ACCIÓN: Creamos un usuario nuevo (esto debería disparar post_save en 'usuarios')
        # Nota: 'usuarios' está en tu lista APPS_DEL_PROYECTO en signals.py
        User.objects.create_user(email=self.victima_email, password='123')
        print("   ↳ Paso 1: Usuario víctima creado.")

        # LIMPIEZA
        _thread_locals.user = None

        # VERIFICACIÓN (Caja Blanca)
        # Buscamos si existe un log que coincida con la acción
        log = LogAuditoria.objects.filter(
            accion=AccionesLog.CREAR,
            modelo='USUARIO', # Ojo: en signals.py usas upper()
            usuario=self.auditor # El log debe decir que lo hizo el auditor
        ).first()

        self.assertIsNotNone(log, "No se creó el registro de auditoría automático")
        self.assertIn(self.victima_email, log.detalle, "El detalle del log no contiene el ID/Email del objeto creado")
        print("     ✅ Éxito: La señal capturó la creación y atribuyó la autoría correctamente.")


class AuditoriaViewWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para la Vista del Dashboard.
    Objetivo: Validar seguridad y filtros de búsqueda.
    """

    def setUp(self):
        # Superusuario (único con acceso)
        self.admin = User.objects.create_user(email='admin@test.com', password='123', is_superuser=True, is_staff=True)
        self.client = Client()
        self.client.force_login(self.admin)

    def test_dashboard_filtro_busqueda(self):
        print("\n📊 [TEST] Iniciando: test_dashboard_filtro_busqueda")
        print("   ↳ Objetivo: Verificar que la lógica 'if query:' en la vista filtra los resultados.")

        # 1. Crear datos de prueba (Ruido vs Objetivo)
        LogAuditoria.objects.create(modulo='TEST', accion='X', detalle='Error crítico en servidor')
        LogAuditoria.objects.create(modulo='TEST', accion='X', detalle='Actualización de perfil')
        LogAuditoria.objects.create(modulo='TEST', accion='X', detalle='Login exitoso')
        
        # 2. Ejecutar búsqueda (Query params)
        url = reverse('auditoria:dashboard')
        response = self.client.get(url, {'q': 'crítico'})
        print("   ↳ Paso 1: Buscando 'crítico' en el dashboard...")

        # 3. Inspección de Contexto (White Box)
        logs_en_contexto = response.context['page_obj'].object_list
        
        self.assertEqual(len(logs_en_contexto), 1, "El filtro debería traer solo 1 resultado")
        self.assertEqual(logs_en_contexto[0].detalle, 'Error crítico en servidor')
        print("     ✅ Éxito: La vista filtró la lista correctamente antes de renderizar.")

    def test_acceso_denegado_no_superuser(self):
        print("\n📊 [TEST] Iniciando: test_acceso_denegado_no_superuser")
        print("   ↳ Objetivo: Validar el decorador @solo_superusuario.")
        
        # Usuario mortal
        mortal = User.objects.create_user(email='mortal@test.com', password='123', is_superuser=False)
        self.client.force_login(mortal)
        
        url = reverse('auditoria:dashboard')
        response = self.client.get(url)
        
        # Esperamos un 403 Forbidden (o 302 a login/home según tu decorador, 
        # pero asumiendo standard Forbidden o redirección de seguridad)
        print(f"   ↳ Código de respuesta obtenido: {response.status_code}")
        
        # Nota: Si tu decorador 'solo_superusuario' redirige a home, cambia 403 por 302
        if response.status_code in [403, 302]:
            print("     ✅ Éxito: El acceso fue restringido.")
        else:
            self.fail(f"Fallo de seguridad: Usuario normal entró con status {response.status_code}")