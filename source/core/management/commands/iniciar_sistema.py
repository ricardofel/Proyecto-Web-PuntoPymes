from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Empresa
from solicitudes.models import TipoAusencia
from empleados.models import Empleado, Departamento, Cargo

User = get_user_model()

class Command(BaseCommand):
    help = 'Inicializa datos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando...")

        # crear empresa
        empresa, _ = Empresa.objects.get_or_create(
            nombre="PuntoPymes Tech",
            defaults={'ruc': '1100000000001', 'direccion': 'Loja', 'telefono': '0991234567'}
        )

        # crear tipos de ausencia
        tipos = [
            {"nombre": "Vacaciones", "afecta_sueldo": False, "requiere_documento": False},
            {"nombre": "Permiso Médico", "afecta_sueldo": False, "requiere_documento": True},
            {"nombre": "Calamidad Doméstica", "afecta_sueldo": False, "requiere_documento": True},
        ]
        for t in tipos:
            TipoAusencia.objects.get_or_create(nombre=t['nombre'], empresa=empresa, defaults=t)

        # departamentos y cargos
        dep_it, _ = Departamento.objects.get_or_create(nombre="Tecnología", empresa=empresa)
        dep_rh, _ = Departamento.objects.get_or_create(nombre="Recursos Humanos", empresa=empresa)
        
        cargo_dev, _ = Cargo.objects.get_or_create(nombre="Desarrollador", departamento=dep_it)
        cargo_jefe, _ = Cargo.objects.get_or_create(nombre="Gerente General", departamento=dep_it)
        cargo_rh, _ = Cargo.objects.get_or_create(nombre="Analista RRHH", departamento=dep_rh)

        # usuario jefe (admin)
        u_jefe, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@pp.com'})
        if created:
            u_jefe.set_password('admin123')
            u_jefe.is_staff = True
            u_jefe.is_superuser = True
            u_jefe.es_superadmin_negocio = True 
            u_jefe.save()
            self.crear_perfil(u_jefe, empresa, cargo_jefe, "Admin", "Jefe")

        # usuario rrhh
        u_rrhh, created = User.objects.get_or_create(username='rrhh', defaults={'email': 'rrhh@pp.com'})
        if created:
            u_rrhh.set_password('rrhh123')
            u_rrhh.is_staff = True
            u_rrhh.es_admin_rrhh = True 
            u_rrhh.save()
            self.crear_perfil(u_rrhh, empresa, cargo_rh, "Maria", "RRHH")

        # usuario empleado
        u_emp, created = User.objects.get_or_create(username='pedro', defaults={'email': 'pedro@pp.com'})
        if created:
            u_emp.set_password('pedro123')
            u_emp.save()
            self.crear_perfil(u_emp, empresa, cargo_dev, "Pedro", "Desarrollador")

        self.stdout.write(self.style.SUCCESS('Listo'))

    def crear_perfil(self, usuario, empresa, cargo, nombre, apellido):
        # crea ficha empleado
        Empleado.objects.get_or_create(
            usuario=usuario,
            defaults={
                'empresa': empresa,
                'nombres': nombre,
                'apellidos': apellido,
                'cedula': f"110{usuario.id}00000",
                'cargo': cargo,
                'correo_personal': usuario.email,
                'estado': 'activo'
            }
        )