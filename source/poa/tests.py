from django.test import TestCase
from poa.models import Objetivo, MetaTactico
from core.models import Empresa  # <--- IMPORTANTE: Importar el modelo Empresa

class PoaJerarquiaTest(TestCase):
    def test_objetivo_promedia_metas(self):
        """
        Si tengo 2 metas (una al 0% y otra al 100%), el objetivo debe estar al 50%.
        """
        print(">>> EJECUTANDO PRUEBA POA...") 
        
        # 1. Preparar: Primero creamos la empresa dueña del objetivo
        empresa_test = Empresa.objects.create(
            nombre_comercial="Mango Corp",
            razon_social="Mango Corp S.A.",
            ruc="1234567890001",
            zona_horaria="America/Guayaquil"
        )

        # Ahora creamos el objetivo asignándole esa empresa
        objetivo = Objetivo.objects.create(
            nombre="Expansión Global", 
            anio=2025, 
            empresa=empresa_test  # <--- AQUÍ ESTABA EL ERROR
        )
        
        MetaTactico.objects.create(objetivo=objetivo, nombre="Abrir sede Perú", valor_esperado=10, valor_actual=0, fecha_inicio="2025-01-01", fecha_fin="2025-12-31")
        MetaTactico.objects.create(objetivo=objetivo, nombre="Abrir sede Chile", valor_esperado=10, valor_actual=10, fecha_inicio="2025-01-01", fecha_fin="2025-12-31")

        # 2. Actuar
        progreso_real = objetivo.avance

        # 3. Verificar
        self.assertEqual(progreso_real, 50)
        print(f"\n✅ POA TEST ÉXITO: Objetivo calculado al {progreso_real}% (Esperado 50%)")