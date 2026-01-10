from django.test import TestCase
from core.models import Empresa, UnidadOrganizacional

class CoreJerarquiaTest(TestCase):
    def test_jerarquia_organizacional(self):
        """
        Prueba que las Unidades Organizacionales respeten la relación Padre-Hijo.
        (Ej: Empresa -> Sede Central -> Departamento IT)
        """
        print("\n>>> EJECUTANDO PRUEBA CORE...")

        # 1. Preparar (Arrange) - Crear la Empresa base
        empresa = Empresa.objects.create(
            nombre_comercial="Mango Holdings",
            razon_social="Mango Holdings S.A.",
            ruc="1799999999001",
            zona_horaria="America/Guayaquil"
        )

        # 2. Actuar (Act) - Crear la jerarquía
        # Nivel 1: Sede Central (No tiene padre)
        sede_central = UnidadOrganizacional.objects.create(
            empresa=empresa,
            nombre="Sede Central",
            tipo="Sede",
            padre=None
        )

        # Nivel 2: Departamento de Tecnología (Hijo de Sede Central)
        depto_it = UnidadOrganizacional.objects.create(
            empresa=empresa,
            nombre="Tecnología",
            tipo="Departamento",
            padre=sede_central
        )

        # 3. Verificar (Assert)
        # Verificar que Tecnología es hijo de Sede Central
        self.assertEqual(depto_it.padre, sede_central)
        
        # Verificar que la Sede Central tiene hijos (usando related_name='hijos')
        # Esto confirma que la relación inversa funciona
        self.assertTrue(sede_central.hijos.exists())
        self.assertEqual(sede_central.hijos.first(), depto_it)

        print(f"✅ CORE TEST ÉXITO: {depto_it.nombre} está correctamente subordinado a {sede_central.nombre}.")