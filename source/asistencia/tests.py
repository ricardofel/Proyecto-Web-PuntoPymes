import json
from datetime import datetime, time, timedelta
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from core.models import Empresa, UnidadOrganizacional
from empleados.models import Empleado, Puesto
from asistencia.models import JornadaCalculada, EventoAsistencia

User = get_user_model()

class AsistenciaWhiteBoxTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre_comercial="Mango Time", ruc="111")
        self.unidad = UnidadOrganizacional.objects.create(nombre="Planta", empresa=self.empresa)
        self.puesto = Puesto.objects.create(nombre="Operario", empresa=self.empresa)
        
        self.user = User.objects.create_user(email='ana@mango.com', password='123')
        self.empleado = Empleado.objects.create(
            nombres="Ana", apellidos="Lopez", cedula="0101", email=self.user.email,
            empresa=self.empresa, unidad_org=self.unidad, puesto=self.puesto,
            fecha_ingreso="2024-01-01",
            hora_entrada_teorica=time(9, 0),
            hora_salida_teorica=time(18, 0)
        )
        self.user.empleado = self.empleado
        self.user.save()
        
        self.client = Client()
        self.client.force_login(self.user)

    def test_registrar_entrada_logica_tardanza(self):
        print("\n [TEST] Iniciando: test_registrar_entrada_logica_tardanza")
        ahora = timezone.localtime(timezone.now()).replace(hour=9, minute=15, second=0)
        
        with patch('django.utils.timezone.now', return_value=ahora):
            url = reverse('asistencia:registrar_marca')
            self.client.post(url, {'tipo_marca': 'entrada'})

        jornada = JornadaCalculada.objects.get(empleado=self.empleado, fecha=ahora.date())
        self.assertEqual(jornada.estado, JornadaCalculada.EstadoJornada.ATRASO)
        print("     Éxito: Atraso detectado correctamente.")

class AsistenciaApiWhiteBoxTests(TestCase):
    def setUp(self):
        self.empresa_A = Empresa.objects.create(nombre_comercial="Empresa A", ruc="A")
        self.u_A = UnidadOrganizacional.objects.create(nombre="U A", empresa=self.empresa_A)
        self.p_A = Puesto.objects.create(nombre="P A", empresa=self.empresa_A)
        self.user_A = User.objects.create_user(email='admin_a@test.com', password='123')
        self.emp_A = Empleado.objects.create(nombres="A", apellidos="A", email="a@t.com", cedula="A1", empresa=self.empresa_A, unidad_org=self.u_A, puesto=self.p_A, fecha_ingreso="2025-01-01")
        
        self.empresa_B = Empresa.objects.create(nombre_comercial="Empresa B", ruc="B")
        self.u_B = UnidadOrganizacional.objects.create(nombre="U B", empresa=self.empresa_B)
        self.p_B = Puesto.objects.create(nombre="P B", empresa=self.empresa_B)
        self.emp_B = Empleado.objects.create(nombres="B", apellidos="B", email="b@t.com", cedula="B1", empresa=self.empresa_B, unidad_org=self.u_B, puesto=self.p_B, fecha_ingreso="2025-01-01")
        
        self.client = Client()
        self.client.force_login(self.user_A)

    def test_api_detalle_aislamiento_empresa(self):
        print("\n [TEST] Iniciando: test_api_detalle_aislamiento_empresa")
        
        url = reverse('asistencia:api_detalle_dia')
        
        session = self.client.session
        session['empresa_actual_id'] = self.empresa_A.id
        session.save()

        response = self.client.get(url, {'empleado_id': self.emp_B.id, 'fecha': '2025-01-01'})
        data = response.json()
        self.assertEqual(len(data.get('eventos', [])), 0)
        print("      Éxito: Aislamiento de API verificado.")