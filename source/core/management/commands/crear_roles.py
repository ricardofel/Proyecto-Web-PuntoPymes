from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction

class Command(BaseCommand):
    help = 'Estandariza los roles del sistema y migra usuarios existentes.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        User = get_user_model()

        try:
            Rol = apps.get_model('usuarios', 'Rol')
        except LookupError:
            Rol = apps.get_model('core', 'Rol')

        configuracion_roles = [
            {'nombre': 'Superusuario', 'descripcion': 'Control total del sistema'},
            {'nombre': 'Admin RRHH', 'descripcion': 'Gestión de personal y nómina'},
            {'nombre': 'Empleado', 'descripcion': 'Acceso al portal del colaborador'},
        ]

        nombres_nuevos = [r['nombre'] for r in configuracion_roles]
        mapa_roles = {r['nombre'].lower(): r['nombre'] for r in configuracion_roles}
        rol_default_nombre = 'Empleado'

        self.stdout.write("Verificando roles oficiales...")

        for config in configuracion_roles:
            rol, created = Rol.objects.get_or_create(
                nombre=config['nombre'],
                defaults={'descripcion': config['descripcion'], 'estado': True}
            )
            if created:
                self.stdout.write(f"Rol creado: {config['nombre']}")

        roles_obsoletos = Rol.objects.exclude(nombre__in=nombres_nuevos)

        if roles_obsoletos.exists():
            self.stdout.write("Procesando roles obsoletos...")
            
            rol_default = Rol.objects.get(nombre=rol_default_nombre)

            for rol_viejo in roles_obsoletos:
                nombre_lower = rol_viejo.nombre.lower()
                
                if nombre_lower in mapa_roles:
                    nombre_destino = mapa_roles[nombre_lower]
                    rol_destino = Rol.objects.get(nombre=nombre_destino)
                else:
                    rol_destino = rol_default

                usuarios_afectados = User.objects.filter(roles_asignados=rol_viejo)
                
                if usuarios_afectados.exists():
                    count = usuarios_afectados.count()
                    self.stdout.write(f"Migrando {count} usuarios de '{rol_viejo.nombre}' a '{rol_destino.nombre}'.")
                    
                    for usuario in usuarios_afectados:
                        usuario.roles_asignados.remove(rol_viejo)
                        usuario.roles_asignados.add(rol_destino)

                rol_viejo.delete()
                self.stdout.write(f"Rol eliminado: {rol_viejo.nombre}")

        self.stdout.write(self.style.SUCCESS('Proceso de estandarización de roles finalizado correctamente.'))