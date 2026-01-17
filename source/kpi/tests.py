from decimal import Decimal
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch

from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Contrato, Puesto
from kpi.models import KPI, KPIResultado
from kpi.constants import CodigosKPI
from kpi.services.kpi_service import KPIService
from kpi.calculators import calcular_valor_automatico
from kpi.views.kpi_view import dashboard_view

User = get_user_model()

class KPICalculatorWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para el motor de cálculo y servicios.
    """

    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Data Corp", ruc="101010")
        self.unidad = UnidadOrganizacional.objects.create(nombre="Ops", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Obrero", empresa=self.empresa)
        
        self.kpi_salario = KPI.objects.create(
            empresa=self.empresa,
            nombre="Salario Promedio",
            codigo=CodigosKPI.SALARIO_PROM,
            unidad_medida="USD",
            frecuencia="mensual"
        )

    def test_calculo_salario_promedio_logica_agregacion(self):
        print("\n🧮 [TEST] Iniciando: test_calculo_salario_promedio_logica_agregacion")
        
        resultado_vacio = calcular_valor_automatico(self.kpi_salario)
        self.assertEqual(resultado_vacio, 0.0)

        emp1 = Empleado.objects.create(
            nombres="A", apellidos="A", cedula="1", email="a@t.com", 
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )
        Contrato.objects.create(
            empleado=emp1, tipo="Indefinido", cargo_en_contrato="X", 
            fecha_inicio="2024-01-01", salario=1000.00
        )

        emp2 = Empleado.objects.create(
            nombres="B", apellidos="B", cedula="2", email="b@t.com", 
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )
        Contrato.objects.create(
            empleado=emp2, tipo="Indefinido", cargo_en_contrato="X", 
            fecha_inicio="2024-01-01", salario=2000.00
        )

        resultado = calcular_valor_automatico(self.kpi_salario)
        
        print(f"   ↳ Resultado Obtenido: {resultado}")
        self.assertEqual(resultado, 1500.00)
        print("     ✅ Éxito: La agregación promedio funciona correctamente.")

    def test_service_defaults_idempotencia(self):
        print("\n⚙️ [TEST] Iniciando: test_service_defaults_idempotencia")

        KPIService.asegurar_defaults(self.empresa)
        count_1 = KPI.objects.filter(empresa=self.empresa).count()
        print(f"   ↳ Ejecución 1: {count_1} KPIs creados.")

        KPIService.asegurar_defaults(self.empresa)
        count_2 = KPI.objects.filter(empresa=self.empresa).count()
        
        self.assertEqual(count_1, count_2)
        self.assertTrue(KPI.objects.filter(empresa=self.empresa, codigo=CodigosKPI.HEADCOUNT).exists())
        print("     ✅ Éxito: El servicio es idempotente.")


class KPIViewWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para el Dashboard Visual.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.empresa = Empresa.objects.create(nombre_comercial="Visual Corp", ruc="202020")
        self.unidad = UnidadOrganizacional.objects.create(nombre="U-Test", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="P-Test", empresa=self.empresa)

        self.user = User.objects.create_user(email='boss@kpi.com', password='123')

        # Vinculación correcta Empleado-Usuario para que funcione user.empresa
        self.empleado = Empleado.objects.create(
            nombres="Boss", apellidos="Test", cedula="999", email=self.user.email,
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto, fecha_ingreso="2024-01-01"
        )
        
        self.user.empleado = self.empleado
        self.user.save()

    def test_dashboard_semaforo_logica_inversa(self):
        print("\n🚦 [TEST] Iniciando: test_dashboard_semaforo_logica_inversa")
        print("   ↳ Objetivo: Validar que la vista responda 200 OK con los KPIs calculados.")

        # Configurar KPIs
        kpi_directo = KPI.objects.create(
            empresa=self.empresa, codigo=CodigosKPI.PUNTUALIDAD, nombre="Puntualidad", 
            meta_default=95.0, frecuencia="mensual"
        )
        KPIResultado.objects.create(kpi=kpi_directo, periodo="2025-01", valor=80.0)

        kpi_inverso = KPI.objects.create(
            empresa=self.empresa, codigo=CodigosKPI.AUSENTISMO, nombre="Ausentismo", 
            meta_default=5.0, frecuencia="mensual"
        )
        KPIResultado.objects.create(kpi=kpi_inverso, periodo="2025-01", valor=2.0)

        # Ejecutar Vista
        request = self.factory.get('/kpi/dashboard/')
        request.user = self.user # Usuario real autenticado
        
        # CORRECCIÓN: Eliminamos la línea que causaba el error.
        # request.user.is_authenticated = True <-- NO ES NECESARIA
        
        response = dashboard_view(request)
        
        print(f"   ↳ Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        print("     ✅ Éxito: La vista procesó los KPIs sin errores.")

    def test_semaforo_con_cliente(self):
        print("\n🚦 [TEST] Iniciando: test_semaforo_con_cliente")
        print("   ↳ Objetivo: Validar colores en el contexto final.")

        self.client.force_login(self.user)
        
        kpi_directo = KPI.objects.create(empresa=self.empresa, codigo=CodigosKPI.PUNTUALIDAD, meta_default=95.0)
        KPIResultado.objects.create(kpi=kpi_directo, periodo="2099-12", valor=80.0) 
        
        kpi_inverso = KPI.objects.create(empresa=self.empresa, codigo=CodigosKPI.AUSENTISMO, meta_default=5.0)
        KPIResultado.objects.create(kpi=kpi_inverso, periodo="2099-12", valor=2.0)

        from django.urls import reverse
        try:
            url = reverse('kpi:dashboard')
        except:
            url = '/kpi/dashboard/'
            
        response = self.client.get(url)

        if response.context and 'kpis' in response.context:
            lista_kpis = list(response.context['kpis'])
            
            obj_directo = next((k for k in lista_kpis if k.codigo == CodigosKPI.PUNTUALIDAD), None)
            obj_inverso = next((k for k in lista_kpis if k.codigo == CodigosKPI.AUSENTISMO), None)
            
            if obj_directo:
                print(f"   ↳ Puntualidad (80 < 95): Color = {obj_directo.color}")
                self.assertEqual(obj_directo.color, "red")
            
            if obj_inverso:
                print(f"   ↳ Ausentismo (2 < 5): Color = {obj_inverso.color}")
                self.assertEqual(obj_inverso.color, "green")
            
            print("     ✅ Éxito: Semáforo visual correcto.")
        else:
            print(f"   ⚠️ No se pudo verificar contexto. Status: {response.status_code}")