from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Modelos base
from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto

# Modelos y Forms del POA
from poa.models import Objetivo, MetaTactico, Actividad
from poa.forms import ActividadForm
# Importamos la lógica interna
from poa.views.poa_view import _recalcular_avance_meta

User = get_user_model()

class PoaCalculationWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para la Lógica de Cálculo en Cascada.
    """

    def setUp(self):
        # 1. Infraestructura
        self.empresa = Empresa.objects.create(nombre_comercial="POA Corp", ruc="101")
        self.unidad = UnidadOrganizacional.objects.create(nombre="Gerencia", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Gerente", empresa=self.empresa)
        self.empleado = Empleado.objects.create(
            nombres="Boss", apellidos="Man", email="boss@poa.com", cedula="999",
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )

        # 2. Estructura POA
        self.objetivo = Objetivo.objects.create(
            empresa=self.empresa, nombre="Objetivo Estratégico", anio=2025
        )
        
        # CORRECCIÓN 1: Usamos Decimal() explícito para evitar TypeError (float * Decimal)
        self.meta = MetaTactico.objects.create(
            objetivo=self.objetivo, nombre="Meta Táctica 1", 
            valor_esperado=Decimal("100.00"), # <-- Cambio Clave
            valor_actual=Decimal("0.00"),     # <-- Cambio Clave
            fecha_inicio="2025-01-01", fecha_fin="2025-12-31"
        )

    def test_logica_recalculo_avance_meta(self):
        print("\n📈 [TEST] Iniciando: test_logica_recalculo_avance_meta")
        print("   ↳ Objetivo: Validar que completar actividades sube el valor de la meta.")

        # Paso 1: Crear 2 actividades para la meta
        act1 = Actividad.objects.create(
            meta=self.meta, nombre="Act 1", fecha_inicio="2025-01-01", fecha_fin="2025-01-02", estado="pendiente"
        )
        act2 = Actividad.objects.create(
            meta=self.meta, nombre="Act 2", fecha_inicio="2025-01-01", fecha_fin="2025-01-02", estado="pendiente"
        )
        
        # Estado inicial
        _recalcular_avance_meta(self.meta)
        self.assertEqual(self.meta.valor_actual, Decimal("0.00"))

        # Paso 2: Completar UNA actividad (50% de avance)
        act1.estado = "completada"
        act1.save()
        
        # Ejecutamos la lógica interna
        _recalcular_avance_meta(self.meta)
        
        # Verificación en Meta
        self.meta.refresh_from_db()
        print(f"   ↳ Valor Meta tras 1/2 actividades: {self.meta.valor_actual}")
        
        # Como usamos Decimal("100.00"), la mitad es Decimal("50.00")
        self.assertEqual(self.meta.valor_actual, Decimal("50.00"))

        # Paso 3: Completar la SEGUNDA actividad (100% de avance)
        act2.estado = "completada"
        act2.save()
        _recalcular_avance_meta(self.meta)
        
        self.meta.refresh_from_db()
        self.assertEqual(self.meta.valor_actual, Decimal("100.00"))
        print("     ✅ Éxito: La meta reacciona correctamente al progreso de actividades.")

    def test_propiedad_avance_objetivo(self):
        print("\n📊 [TEST] Iniciando: test_propiedad_avance_objetivo")
        print("   ↳ Objetivo: Validar la propiedad calculada @property 'avance' del Objetivo.")

        # Configuramos valores exactos usando Decimal
        self.meta.valor_actual = Decimal("50.00")
        self.meta.save()

        MetaTactico.objects.create(
            objetivo=self.objetivo, nombre="Meta Táctica 2", 
            valor_esperado=Decimal("100.00"), 
            valor_actual=Decimal("100.00"),
            fecha_inicio="2025-01-01", fecha_fin="2025-12-31"
        )

        # Invocamos la propiedad
        avance_real = self.objetivo.avance
        
        print(f"   ↳ Avance Objetivo calculado: {avance_real}%")
        self.assertEqual(avance_real, 75)
        print("     ✅ Éxito: El Objetivo consolida correctamente el avance de sus metas.")


class PoaSecurityWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para Seguridad y Aislamiento de Datos.
    """

    def setUp(self):
        self.client = Client()
        
        # Empresa A (Atacante)
        self.empresa_A = Empresa.objects.create(nombre_comercial="Empresa A", ruc="111")
        
        # CORRECCIÓN 2: Hacemos al usuario Superuser para pasar el decorador de permisos
        # y llegar a la validación interna de empresa (Multitenancy Check).
        # Si fuera usuario normal, el decorador devolvería 403 Forbidden antes de entrar a la vista.
        self.user_A = User.objects.create_user(
            email='userA@poa.com', password='123', 
            is_superuser=True  # <-- ¡Llave maestra para pasar el decorador!
        )
        
        # Vinculamos usuario A a empresa A
        emp_A = Empleado.objects.create(
            nombres="User", apellidos="A", email=self.user_A.email, empresa=self.empresa_A,
            fecha_ingreso="2024-01-01", 
            unidad_org=UnidadOrganizacional.objects.create(nombre="U", empresa=self.empresa_A),
            puesto=Puesto.objects.create(nombre="P", empresa=self.empresa_A)
        )
        self.user_A.empleado = emp_A
        self.user_A.save()

        # Empresa B (Víctima)
        self.empresa_B = Empresa.objects.create(nombre_comercial="Empresa B", ruc="222")
        self.objetivo_B = Objetivo.objects.create(
            empresa=self.empresa_B, nombre="Objetivo Secreto B", anio=2025
        )

    def test_aislamiento_borrado_objetivos(self):
        print("\n🛡️ [TEST] Iniciando: test_aislamiento_borrado_objetivos")
        print("   ↳ Objetivo: Validar que User A (Admin de Emp A) no pueda borrar un objetivo de Empresa B.")

        self.client.force_login(self.user_A)
        
        # Intentamos borrar el objetivo B
        url = reverse('poa:objetivo_eliminar', args=[self.objetivo_B.id])
        
        # Ejecución
        response = self.client.post(url)
        
        # Verificación
        print(f"   ↳ Status Code obtenido: {response.status_code}")
        
        # Ahora sí esperamos 400 (Bad Request) porque pasamos el decorador (es superuser)
        # pero fallamos la validación de empresa interna `_verificar_permiso_empresa`.
        self.assertEqual(response.status_code, 400, "La vista permitió borrar un objetivo ajeno.")
        
        # Confirmamos que el objetivo sigue vivo en DB
        self.assertTrue(Objetivo.objects.filter(id=self.objetivo_B.id).exists())
        print("     ✅ Éxito: El sistema protegió los datos entre empresas (Multitenancy).")


class PoaFormWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para Validaciones de Formularios.
    """
    
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Form Corp", ruc="333")
        self.unidad = UnidadOrganizacional.objects.create(nombre="U", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="P", empresa=self.empresa)
        self.empleado = Empleado.objects.create(
            nombres="Ejecutor", apellidos="Test", email="e@poa.com",
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )

    def test_actividad_form_validacion_ejecutores(self):
        print("\n📝 [TEST] Iniciando: test_actividad_form_validacion_ejecutores")
        print("   ↳ Objetivo: Validar la regla 'clean_ejecutores' que exige al menos un responsable.")

        data = {
            "nombre": "Actividad Sin Dueño",
            "fecha_inicio": "2025-01-01",
            "fecha_fin": "2025-01-05",
            "estado": "pendiente",
            "ejecutores": [] # Lista vacía intencional
        }
        
        form = ActividadForm(data=data)
        
        es_valido = form.is_valid()
        print(f"   ↳ ¿Formulario válido?: {es_valido}")
        
        self.assertFalse(es_valido)
        self.assertIn("ejecutores", form.errors)
        print("     ✅ Éxito: La validación de ejecutores obligatorios funciona.")