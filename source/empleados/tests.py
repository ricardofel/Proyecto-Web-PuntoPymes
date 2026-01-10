from django.test import TestCase
from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto
from datetime import date

class EmpleadoModelTest(TestCase):
    def test_creacion_empleado_y_capitalizacion(self):
        """
        Prueba que al crear un empleado con nombres en minúscula, 
        el sistema los capitalice automáticamente (Juan Perez).
        """
        print("\n>>> EJECUTANDO PRUEBA EMPLEADOS...")

        # 1. Preparar (Arrange) - Crear las dependencias obligatorias
        empresa = Empresa.objects.create(
            nombre_comercial="Mango Corp",
            razon_social="Mango Corp S.A.",
            ruc="1234567890001",
            zona_horaria="America/Guayaquil"
        )
        
        unidad = UnidadOrganizacional.objects.create(
            empresa=empresa,
            nombre="Tecnología",
            tipo="Departamento"
        )
        
        puesto = Puesto.objects.create(
            empresa=empresa,
            nombre="Desarrollador Backend",
            nivel="Senior"
        )

        # 2. Actuar (Act) - Crear empleado con nombres "feos" (todo minúscula)
        empleado = Empleado.objects.create(
            empresa=empresa,
            unidad_org=unidad,
            puesto=puesto,
            nombres="juan carlos",      # <--- El usuario escribió mal
            apellidos="perez lopez",    # <--- El usuario escribió mal
            cedula="1100110011",
            email="juan.test@mango.com",
            fecha_ingreso=date(2025, 1, 1),
            estado="activo"
        )

        # 3. Verificar (Assert)
        # La lógica interna (save) debería haberlo arreglado
        self.assertEqual(empleado.nombres, "Juan Carlos")
        self.assertEqual(empleado.apellidos, "Perez Lopez")
        
        # Verificar que el 'helper' nombre_completo funcione
        self.assertEqual(empleado.nombre_completo, "Juan Carlos Perez Lopez")
        
        print(f"✅ EMPLEADOS TEST ÉXITO: '{empleado.nombre_completo}' se guardó capitalizado correctamente.")