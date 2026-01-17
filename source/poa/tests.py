from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto

from poa.models import Objetivo, MetaTactico, Actividad
from poa.forms import ActividadForm
from poa.views.poa_view import _recalcular_avance_meta

User = get_user_model()

class PoaCalculationWhiteBoxTests(TestCase):
    """
    Tests de lógica de cálculo:
    valida el recálculo en cascada del avance de metas y objetivos.
    """

    def setUp(self):
        # Infraestructura base
        self.empresa = Empresa.objects.create(nombre_comercial="POA Corp", ruc="101")
        self.unidad = UnidadOrganizacional.objects.create(nombre="Gerencia", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Gerente", empresa=self.empresa)
        self.empleado = Empleado.objects.create(
            nombres="Boss", apellidos="Man", email="boss@poa.com", cedula="999",
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )

        # Estructura POA
        self.objetivo = Objetivo.objects.create(
            empresa=self.empresa, nombre="Objetivo Estratégico", anio=2025
        )

        # Usa Decimal para evitar mezclas float/Decimal en cálculos
        self.meta = MetaTactico.objects.create(
            objetivo=self.objetivo, nombre="Meta Táctica 1",
            valor_esperado=Decimal("100.00"),
            valor_actual=Decimal("0.00"),
            fecha_inicio="2025-01-01", fecha_fin="2025-12-31"
        )

    def test_logica_recalculo_avance_meta(self):
        print("\n📈 [TEST] Iniciando: test_logica_recalculo_avance_meta")
        print("   ↳ Objetivo: Validar que completar actividades actualiza el valor de la meta.")

        # Crea dos actividades para la meta (avance esperado: 50% al completar 1)
        act1 = Actividad.objects.create(
            meta=self.meta, nombre="Act 1", fecha_inicio="2025-01-01", fecha_fin="2025-01-02", estado="pendiente"
        )
        act2 = Actividad.objects.create(
            meta=self.meta, nombre="Act 2", fecha_inicio="2025-01-01", fecha_fin="2025-01-02", estado="pendiente"
        )

        # Estado inicial
        _recalcular_avance_meta(self.meta)
        self.assertEqual(self.meta.valor_actual, Decimal("0.00"))

        # Completa una actividad (avance: 50%)
        act1.estado = "completada"
        act1.save()

        _recalcular_avance_meta(self.meta)

        self.meta.refresh_from_db()
        print(f"   ↳ Valor Meta tras 1/2 actividades: {self.meta.valor_actual}")
        self.assertEqual(self.meta.valor_actual, Decimal("50.00"))

        # Completa la segunda actividad (avance: 100%)
        act2.estado = "completada"
        act2.save()
        _recalcular_avance_meta(self.meta)

        self.meta.refresh_from_db()
        self.assertEqual(self.meta.valor_actual, Decimal("100.00"))
        print("     ✅ Éxito: La meta reacciona correctamente al progreso de actividades.")

    def test_propiedad_avance_objetivo(self):
        print("\n📊 [TEST] Iniciando: test_propiedad_avance_objetivo")
        print("   ↳ Objetivo: Validar la propiedad calculada 'avance' del Objetivo.")

        # Configura valores controlados con Decimal
        self.meta.valor_actual = Decimal("50.00")
        self.meta.save()

        MetaTactico.objects.create(
            objetivo=self.objetivo, nombre="Meta Táctica 2",
            valor_esperado=Decimal("100.00"),
            valor_actual=Decimal("100.00"),
            fecha_inicio="2025-01-01", fecha_fin="2025-12-31"
        )

        avance_real = self.objetivo.avance

        print(f"   ↳ Avance Objetivo calculado: {avance_real}%")
        self.assertEqual(avance_real, 75)
        print("     ✅ Éxito: El Objetivo consolida correctamente el avance de sus metas.")


class PoaSecurityWhiteBoxTests(TestCase):
    """
    Tests de seguridad: aislamiento de datos entre empresas (multitenancy).
    """

    def setUp(self):
        self.client = Client()

        # Empresa A (usuario autenticado)
        self.empresa_A = Empresa.objects.create(nombre_comercial="Empresa A", ruc="111")

        # Superuser para acceder a la vista y evaluar la validación interna de empresa
        self.user_A = User.objects.create_user(
            email='userA@poa.com', password='123',
            is_superuser=True
        )

        emp_A = Empleado.objects.create(
            nombres="User", apellidos="A", email=self.user_A.email, empresa=self.empresa_A,
            fecha_ingreso="2024-01-01",
            unidad_org=UnidadOrganizacional.objects.create(nombre="U", empresa=self.empresa_A),
            puesto=Puesto.objects.create(nombre="P", empresa=self.empresa_A)
        )
        self.user_A.empleado = emp_A
        self.user_A.save()

        # Empresa B (objetivo que no debe ser accesible desde A)
        self.empresa_B = Empresa.objects.create(nombre_comercial="Empresa B", ruc="222")
        self.objetivo_B = Objetivo.objects.create(
            empresa=self.empresa_B, nombre="Objetivo Secreto B", anio=2025
        )

    def test_aislamiento_borrado_objetivos(self):
        print("\n🛡️ [TEST] Iniciando: test_aislamiento_borrado_objetivos")
        print("   ↳ Objetivo: Validar que no se pueda borrar un objetivo de otra empresa.")

        self.client.force_login(self.user_A)

        url = reverse('poa:objetivo_eliminar', args=[self.objetivo_B.id])
        response = self.client.post(url)

        print(f"   ↳ Status Code obtenido: {response.status_code}")

        # Se espera fallo por validación interna de empresa
        self.assertEqual(response.status_code, 400, "La vista permitió borrar un objetivo ajeno.")

        self.assertTrue(Objetivo.objects.filter(id=self.objetivo_B.id).exists())
        print("     ✅ Éxito: El sistema protegió los datos entre empresas (Multitenancy).")


class PoaFormWhiteBoxTests(TestCase):
    """
    Tests de validaciones de formularios del módulo POA.
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
        print("   ↳ Objetivo: Validar que se exija al menos un responsable en ejecutores.")

        data = {
            "nombre": "Actividad Sin Dueño",
            "fecha_inicio": "2025-01-01",
            "fecha_fin": "2025-01-05",
            "estado": "pendiente",
            "ejecutores": []
        }

        form = ActividadForm(data=data)

        es_valido = form.is_valid()
        print(f"   ↳ ¿Formulario válido?: {es_valido}")

        self.assertFalse(es_valido)
        self.assertIn("ejecutores", form.errors)
        print("     ✅ Éxito: La validación de ejecutores obligatorios funciona.")
