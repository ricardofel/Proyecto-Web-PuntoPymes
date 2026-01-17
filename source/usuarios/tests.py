from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

# Modelos necesarios
from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto
from usuarios.models import Rol, UsuarioRol
from usuarios.services.usuario_service import UsuarioService
from usuarios.constants import NombresRoles
from usuarios.decorators import solo_superusuario_o_admin_rrhh

User = get_user_model()

class UsuarioQuerySetWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para UsuarioQuerySet.
    """

    def setUp(self):
        # 1. Infraestructura: 2 Empresas
        self.empresa_A = Empresa.objects.create(nombre_comercial="Empresa A", ruc="111")
        self.empresa_B = Empresa.objects.create(nombre_comercial="Empresa B", ruc="222")

        # 2. Usuarios en Empresa A (Con cédulas distintas)
        self.user_A = self._crear_usuario_empresa("a@test.com", self.empresa_A, "0101010101")
        self.user_A_2 = self._crear_usuario_empresa("a2@test.com", self.empresa_A, "0202020202")

        # 3. Usuario en Empresa B
        self.user_B = self._crear_usuario_empresa("b@test.com", self.empresa_B, "0303030303")

        # 4. Superusuario
        self.superuser = User.objects.create_superuser(email="admin@test.com", password="123")

    def _crear_usuario_empresa(self, email, empresa, cedula):
        """Helper para crear usuario con empleado vinculado de forma segura."""
        
        # CORRECCIÓN 1: Usamos get_or_create para evitar duplicados de Unidad/Puesto en la misma empresa
        unidad, _ = UnidadOrganizacional.objects.get_or_create(nombre="U-Test", empresa=empresa)
        puesto, _ = Puesto.objects.get_or_create(nombre="P-Test", empresa=empresa)
        
        # CORRECCIÓN 2: Pasamos la cédula explícita para evitar unique_empresa_cedula
        empleado = Empleado.objects.create(
            nombres="Test", apellidos="User", email=email,
            cedula=cedula, # <--- ¡Clave para evitar el choque!
            empresa=empresa, unidad_org=unidad, puesto=puesto, fecha_ingreso="2024-01-01"
        )
        
        # CORRECCIÓN 3: Recuperamos el usuario creado por el signal
        user = User.objects.get(email=email)
        user.set_password("123")
        user.save()
        
        return user

    def test_visibles_para_aislamiento_empresas(self):
        print("\n👁️ [TEST] Iniciando: test_visibles_para_aislamiento_empresas")
        print("   ↳ Objetivo: Validar que un usuario de A solo vea usuarios de A.")

        qs_A = User.objects.visibles_para(self.user_A)
        emails_visibles = [u.email for u in qs_A]
        print(f"   ↳ Usuario A ve: {emails_visibles}")
        
        self.assertIn(self.user_A_2, qs_A, "Debería ver a su compañero de empresa.")
        self.assertNotIn(self.user_B, qs_A, "NO debería ver a usuarios de otra empresa.")
        self.assertNotIn(self.user_A, qs_A, "No debería verse a sí mismo.")

        qs_Admin = User.objects.visibles_para(self.superuser)
        print(f"   ↳ Superuser ve total: {qs_Admin.count()}")
        self.assertEqual(qs_Admin.count(), 3)
        print("     ✅ Éxito: La multitenencia en el QuerySet funciona.")

    def test_busqueda_general_logica_or(self):
        print("\n🔍 [TEST] Iniciando: test_busqueda_general_logica_or")
        
        qs_nombre = User.objects.busqueda_general("Test")
        self.assertIn(self.user_A, qs_nombre)

        qs_email = User.objects.busqueda_general("a@test")
        self.assertIn(self.user_A, qs_email)
        print("     ✅ Éxito: La búsqueda integra campos de Usuario y Empleado.")


class UsuarioServiceWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para UsuarioService.
    """

    def setUp(self):
        self.editor_admin = User.objects.create_superuser(email="god@test.com", password="123")
        self.usuario_target = User.objects.create_user(email="target@test.com", password="123")
        
        # Usamos get_or_create para robustez
        self.rol_rrhh, _ = Rol.objects.get_or_create(nombre=NombresRoles.ADMIN_RRHH)
        self.rol_super, _ = Rol.objects.get_or_create(nombre=NombresRoles.SUPERUSUARIO)
        self.rol_normal, _ = Rol.objects.get_or_create(nombre="Empleado Normal")

    def test_mapeo_roles_a_permisos(self):
        print("\n⚙️ [TEST] Iniciando: test_mapeo_roles_a_permisos")
        print("   ↳ Objetivo: Validar que el servicio actualiza is_staff/is_superuser según el rol.")

        # Caso 1: RRHH
        data_rrhh = {'roles': self.rol_rrhh}
        UsuarioService.crear_o_actualizar_usuario(self.usuario_target, data_rrhh, self.editor_admin)
        self.usuario_target.refresh_from_db()
        self.assertTrue(self.usuario_target.is_staff)
        self.assertFalse(self.usuario_target.is_superuser)

        # Caso 2: Superusuario
        data_super = {'roles': self.rol_super}
        UsuarioService.crear_o_actualizar_usuario(self.usuario_target, data_super, self.editor_admin)
        self.usuario_target.refresh_from_db()
        self.assertTrue(self.usuario_target.is_superuser)

        # Caso 3: Normal
        data_normal = {'roles': self.rol_normal}
        UsuarioService.crear_o_actualizar_usuario(self.usuario_target, data_normal, self.editor_admin)
        self.usuario_target.refresh_from_db()
        self.assertFalse(self.usuario_target.is_staff)
        print("     ✅ Éxito: Permisos mapeados correctamente.")


class UsuarioDecoratorWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para Decoradores de Seguridad.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.normal = User.objects.create_user(email="normal@test.com", password="123")
        self.rrhh = User.objects.create_user(email="rrhh@test.com", password="123")
        
        rol_rrhh, _ = Rol.objects.get_or_create(nombre=NombresRoles.ADMIN_RRHH)
        UsuarioRol.objects.create(usuario=self.rrhh, rol=rol_rrhh)

    def test_decorador_acceso_denegado(self):
        print("\n⛔ [TEST] Iniciando: test_decorador_acceso_denegado")
        
        @solo_superusuario_o_admin_rrhh
        def vista_protegida(request):
            return HttpResponse("Entraste")

        request = self.factory.get('/')
        request.user = self.normal
        
        with self.assertRaises(PermissionDenied):
            vista_protegida(request)
        print("     ✅ Éxito: Bloqueado correctamente.")

    def test_decorador_acceso_permitido(self):
        print("\n✅ [TEST] Iniciando: test_decorador_acceso_permitido")
        
        @solo_superusuario_o_admin_rrhh
        def vista_protegida(request):
            return HttpResponse("Entraste")

        request = self.factory.get('/')
        request.user = self.rrhh
        
        response = vista_protegida(request)
        self.assertEqual(response.status_code, 200)
        print("     ✅ Éxito: Permitido correctamente.")