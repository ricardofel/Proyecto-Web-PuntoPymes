from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db.models import Q
from empleados.models import Empleado, Puesto, ruta_foto_empleado
from empleados.forms import EmpleadoForm
from empleados.views import ListaEmpleadosView
from core.models import Empresa, UnidadOrganizacional

User = get_user_model()

class EmpleadoLogicWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para Lógica de Datos y Automatización.
    Objetivo: Validar transformaciones en Forms y sincronización por Signals.
    """

    def setUp(self):
        # Infraestructura mínima requerida
        self.empresa = Empresa.objects.create(nombre_comercial="Empresa Test", ruc="123123")
        self.unidad = UnidadOrganizacional.objects.create(nombre="RRHH", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Analista", empresa=self.empresa)

    def test_form_procesamiento_dias_laborales(self):
        print("\n📝 [TEST] Iniciando: test_form_procesamiento_dias_laborales")
        print("   ↳ Objetivo: Validar que el Form convierte la lista ['LUN', 'MAR'] a string 'LUN,MAR'.")

        # FIX: Agregamos hora_entrada y hora_salida porque el formulario las requiere
        data_form = {
            'nombres': 'Juan',
            'apellidos': 'Perez',
            'cedula': '0999999999',
            'email': 'juan@test.com',
            'fecha_ingreso': '2025-01-01',
            'empresa': self.empresa.id,
            'unidad_org': self.unidad.id,
            'puesto': self.puesto.id,
            'estado': 'Activo',
            'hora_entrada_teorica': '09:00', # Agregado
            'hora_salida_teorica': '18:00',  # Agregado
            'dias_laborales_select': ['LUN', 'VIE'] 
        }

        # Instanciamos el form
        form = EmpleadoForm(data=data_form, empresa_id=self.empresa.id)
        
        if form.is_valid():
            empleado = form.save(commit=False)
            
            # Verificamos la transformación interna
            print(f"   ↳ Input (Lista): {data_form['dias_laborales_select']}")
            print(f"   ↳ Output (Modelo): '{empleado.dias_laborales}'")
            
            self.assertEqual(empleado.dias_laborales, "LUN,VIE", "El formulario no concatenó correctamente la lista.")
            print("     ✅ Éxito: La lógica de conversión de datos del formulario funciona.")
        else:
            self.fail(f"El formulario no fue válido: {form.errors}")

    def test_signal_sincronizacion_usuario(self):
        print("\n⚡ [TEST] Iniciando: test_signal_sincronizacion_usuario")
        print("   ↳ Objetivo: Validar que al desactivar un empleado, su usuario de sistema se bloquea automáticamente.")

        email_test = 'sync@test.com'
        
        # 1. Crear Empleado 
        # (El signal se dispara AQUÍ y crea el Usuario automáticamente)
        empleado = Empleado.objects.create(
            nombres="Test", apellidos="Sync", cedula="11111", email=email_test,
            fecha_ingreso="2025-01-01", empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto,
            estado='Activo'
        )
        print("   ↳ Paso 1: Empleado creado. El signal debería haber creado el usuario.")

        # FIX: En lugar de crear el usuario manual (que da error duplicado), lo buscamos.
        usuario = User.objects.get(email=email_test)
        
        # Pre-verificación
        self.assertTrue(usuario.estado, "El usuario debería iniciar activo (creado por signal).")

        # 2. ACCIÓN: Cambiamos estado del empleado a 'Inactivo'
        print("   ↳ Paso 2: Cambiando estado de empleado a 'Inactivo'...")
        empleado.estado = 'Inactivo'
        empleado.save() # Esto dispara el signal 'sync_empleado_con_usuario' nuevamente

        # 3. VERIFICACIÓN
        usuario.refresh_from_db()
        print(f"   ↳ Estado final del Usuario: {usuario.estado}")
        
        self.assertFalse(usuario.estado, "El signal falló: El usuario sigue activo tras desactivar empleado.")
        print("     ✅ Éxito: La señal de sincronización protegió el acceso al sistema.")


class EmpleadoViewWhiteBoxTests(TestCase):
    """
    [Caja Blanca] Tests para Vistas y Utilidades.
    Objetivo: Validar lógica de búsqueda y generación de rutas.
    """

    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Empresa View", ruc="999")
        self.unidad = UnidadOrganizacional.objects.create(nombre="IT", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Dev", empresa=self.empresa)
        self.user = User.objects.create_user(email='view@test.com', password='123')
        
        # Datos de prueba para búsqueda
        Empleado.objects.create(nombres="Carlos", apellidos="Santana", cedula="010101", email="c@t.com", fecha_ingreso="2025-01-01", empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto)
        Empleado.objects.create(nombres="Maria", apellidos="Callas", cedula="020202", email="m@t.com", fecha_ingreso="2025-01-01", empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto)

    def test_lista_empleados_logica_busqueda(self):
        print("\n🔍 [TEST] Iniciando: test_lista_empleados_logica_busqueda")
        print("   ↳ Objetivo: Validar que el QuerySet filtra por nombre, apellido O cédula (Lógica OR).")

        # Simulamos Request con parámetro de búsqueda 'q'
        request = RequestFactory().get('/empleados/', {'q': 'Santana'})
        request.user = self.user
        request.empresa_actual = self.empresa 

        # Instanciamos la vista
        vista = ListaEmpleadosView()
        vista.request = request
        vista.kwargs = {}

        # Ejecución (Caja Blanca: get_queryset)
        qs = vista.get_queryset()
        
        # Verificación
        print(f"   ↳ Buscando 'Santana'. Resultados encontrados: {qs.count()}")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().nombres, "Carlos")

        # Prueba 2: Búsqueda por cédula parcial
        request = RequestFactory().get('/empleados/', {'q': '0202'}) 
        request.user = self.user
        request.empresa_actual = self.empresa
        vista.request = request
        qs = vista.get_queryset()

        print(f"   ↳ Buscando cédula '0202'. Resultados encontrados: {qs.count()}")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().nombres, "Maria")
        print("     ✅ Éxito: La lógica de búsqueda multicampo funciona.")

    def test_utilidad_ruta_foto_dinamica(self):
        print("\n📂 [TEST] Iniciando: test_utilidad_ruta_foto_dinamica")
        print("   ↳ Objetivo: Validar que la función genera rutas con ID formateado (Padding de ceros).")

        class EmpleadoMock:
            id = 5
        
        instancia = EmpleadoMock()
        filename = "foto_perfil.jpg"

        # Ejecución directa
        ruta_generada = ruta_foto_empleado(instancia, filename)
        
        # Verificación
        expected_folder = "empleado_00000005"
        
        print(f"   ↳ Ruta generada: {ruta_generada}")
        self.assertIn(expected_folder, ruta_generada)
        self.assertTrue(ruta_generada.endswith(".jpg"))
        print("     ✅ Éxito: La ruta del archivo se genera con formato estándar.")