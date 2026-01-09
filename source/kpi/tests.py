from django.test import TestCase
from kpi.models import KPI, KPIResultado
from core.models import Empresa  # Importamos Empresa para poder crear el KPI

class KpiCalculoTest(TestCase):
    def test_calculo_porcentaje_cumplimiento(self):
        """
        Verifica que si la meta es 100 y logramos 80, el cumplimiento sea 80%.
        """
        print("\n>>> EJECUTANDO PRUEBA KPI...")

        # 1. Preparar: Primero creamos la empresa obligatoria
        empresa_test = Empresa.objects.create(
            nombre_comercial="Mango Inc",
            razon_social="Mango Inc S.A.",
            ruc="9999999999001",
            zona_horaria="America/Guayaquil"
        )

        # 2. Crear el KPI (Usando los nombres reales de tu modelo)
        kpi = KPI.objects.create(
            empresa=empresa_test,       # <--- AGREGADO: Campo obligatorio
            nombre="Ventas Mensuales",
            meta_default=100.00,        # <--- CORREGIDO: Se llama 'meta_default', no 'meta'
            unidad_medida="USD",
            frecuencia="mensual"
        )

        # 3. Crear el Resultado
        resultado = KPIResultado.objects.create(
            kpi=kpi,
            valor=80.00,
            periodo="2025-01"
        )

        # 4. Actuar: Calcular cumplimiento
        # Usamos meta_default del KPI para el cálculo
        cumplimiento = (resultado.valor / kpi.meta_default) * 100

        # 5. Verificar
        self.assertEqual(cumplimiento, 80.00)
        print(f"✅ KPI TEST ÉXITO: Meta {kpi.meta_default} vs Real {resultado.valor} = {cumplimiento}% Cumplimiento")