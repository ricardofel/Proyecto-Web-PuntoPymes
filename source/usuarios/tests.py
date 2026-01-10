from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

class SeguridadTest(TestCase):
    def test_acceso_denegado_a_no_admin(self):
        """
        Un usuario normal NO debe poder ver la lista de usuarios.
        """
        # 1. Preparar: Crear usuario mortal (no staff/admin)
        User = get_user_model()
        usuario_mortal = User.objects.create_user(email='mortal@test.com', password='123')
        
        # 2. Actuar: Intentar entrar a una vista protegida
        self.client.login(email='mortal@test.com', password='123')
        # Asumiendo que la url es 'usuarios:lista_usuarios'
        respuesta = self.client.get(reverse('usuarios:lista_usuarios'))

        # 3. Verificar: Esperamos un error 403 (Prohibido) o redirección (302)
        # No esperamos un 200 (OK)
        self.assertNotEqual(respuesta.status_code, 200)
        print(f"\n✅ SEGURIDAD TEST: Acceso denegado correctamente (Status: {respuesta.status_code})")