from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from notificaciones.models import Notificacion
from notificaciones.services.notificacion_service import NotificacionService

# Obtenemos el modelo de usuario real de tu proyecto
User = get_user_model()

class NotificacionServiceWhiteBoxTests(TestCase):
    """
    Tests de Caja Blanca para NotificacionService.
    Objetivo: Validar caminos lógicos (if/else) y límites de datos.
    """

    def setUp(self):
        # CORRECCIÓN: Eliminamos 'username'. Tu modelo usa email como identificador único.
        self.usuario = User.objects.create_user(
            email='mango_service@prueba.com', 
            password='password123'
        )

    def test_crear_notificacion_ruta_validacion_usuario(self):
        print("\n🔵 [TEST] Iniciando: test_crear_notificacion_ruta_validacion_usuario")
        print("   ↳ Objetivo: Validar que el 'if not usuario' proteja el método.")
        
        # Caso 1: Camino del fallo (Branch False)
        print("   ↳ Paso 1: Intentando crear notificación con usuario=None...")
        resultado_fail = NotificacionService.crear_notificacion(
            usuario=None,
            titulo="Test Fail",
            mensaje="Esto no debe crearse"
        )
        self.assertIsNone(resultado_fail)
        self.assertEqual(Notificacion.objects.count(), 0)
        print("     ✅ Éxito: El sistema rechazó correctamente el usuario nulo.")

        # Caso 2: Camino del éxito (Branch True)
        print("   ↳ Paso 2: Intentando crear notificación con usuario válido...")
        resultado_ok = NotificacionService.crear_notificacion(
            usuario=self.usuario,
            titulo="Test OK",
            mensaje="Esto sí"
        )
        self.assertIsNotNone(resultado_ok)
        self.assertEqual(Notificacion.objects.count(), 1)
        print("     ✅ Éxito: Notificación creada correctamente.")

    def test_obtener_resumen_navbar_limites_slicing(self):
        print("\n🔵 [TEST] Iniciando: test_obtener_resumen_navbar_limites_slicing")
        print("   ↳ Objetivo: Validar que el slicing [:5] corte la lista aunque haya más datos.")
        
        # Preparación
        total_creadas = 7
        print(f"   ↳ Paso 1: Creando {total_creadas} notificaciones (excediendo el límite de 5)...")
        for i in range(total_creadas):
            NotificacionService.crear_notificacion(
                usuario=self.usuario,
                titulo=f"Notif {i}",
                mensaje="Cuerpo mensaje"
            )

        # Ejecución
        resumen = NotificacionService.obtener_resumen_navbar(self.usuario)
        print("   ↳ Paso 2: Datos obtenidos del servicio.")

        # Verificación
        print(f"   ↳ Paso 3: Verificando conteos (Total esperado: {total_creadas}, Lista esperada: 5)...")
        
        # Validación lógica interna 1: Conteo total real
        self.assertEqual(resumen['num_no_leidas'], total_creadas)
        
        # Validación lógica interna 2: Límite visual (Slice)
        self.assertEqual(len(resumen['ultimas']), 5)
        print("     ✅ Éxito: El conteo es correcto y la lista se recortó a 5 items.")


class NotificacionViewsWhiteBoxTests(TestCase):
    """
    Tests de Caja Blanca para las Vistas (Controladores).
    Objetivo: Validar cambios de estado y contexto de plantillas.
    """

    def setUp(self):
        # CORRECCIÓN: Eliminamos 'username' aquí también.
        self.usuario = User.objects.create_user(
            email='mango_view@prueba.com', 
            password='password123'
        )
        self.client = Client()
        self.client.force_login(self.usuario) 

    def test_marcar_una_leida_logica_cambio_estado(self):
        print("\n🟠 [TEST] Iniciando: test_marcar_una_leida_logica_cambio_estado")
        print("   ↳ Objetivo: Verificar que la vista cambie 'leido' de False a True en la BD.")

        # Estado inicial
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            titulo="Prueba Estado",
            mensaje="...",
            leido=False
        )
        print(f"   ↳ Estado inicial en BD: Leído = {notificacion.leido}")

        url = reverse('notificaciones:marcar_leida', args=[notificacion.id])
        
        # Ejecución
        print("   ↳ Paso 1: Llamando a la vista...")
        self.client.get(url)

        # Verificación Persistencia
        notificacion.refresh_from_db()
        print(f"   ↳ Estado final en BD: Leído = {notificacion.leido}")
        
        self.assertTrue(notificacion.leido)
        print("     ✅ Éxito: La vista actualizó la base de datos correctamente.")

    def test_lista_notificaciones_calculo_contexto(self):
        print("\n🟠 [TEST] Iniciando: test_lista_notificaciones_calculo_contexto")
        print("   ↳ Objetivo: Inspeccionar variables de contexto antes de renderizar.")

        # Escenario
        Notificacion.objects.create(usuario=self.usuario, titulo="Leída", leido=True)
        Notificacion.objects.create(usuario=self.usuario, titulo="No Leída 1", leido=False)
        Notificacion.objects.create(usuario=self.usuario, titulo="No Leída 2", leido=False)
        print("   ↳ Setup: Se crearon 1 leída y 2 NO leídas.")

        url = reverse('notificaciones:lista_notificaciones')
        response = self.client.get(url)

        # Inspección
        conteo_contexto = response.context['no_leidas']
        total_contexto = len(response.context['notificaciones'])
        
        print(f"   ↳ Variable 'no_leidas' en contexto: {conteo_contexto}")
        print(f"   ↳ Variable 'notificaciones' (total) en contexto: {total_contexto}")

        self.assertEqual(conteo_contexto, 2)
        self.assertEqual(total_contexto, 3)
        print("     ✅ Éxito: Los cálculos internos de la vista son correctos.")