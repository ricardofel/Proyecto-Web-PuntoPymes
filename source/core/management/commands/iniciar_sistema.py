from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crea los 3 roles de sistema (Grupos de Usuario)'

    def handle(self, *args, **kwargs):
        roles = ['EMPLEADO', 'ADMIN_RRHH', 'SUPERADMIN']

        for nombre in roles:
            grupo, created = Group.objects.get_or_create(name=nombre)
            if created:
                self.stdout.write(f"Creado Rol: {nombre}")
            else:
                self.stdout.write(f"Ya existía Rol: {nombre}")

        self.stdout.write(self.style.SUCCESS('Roles de sistema listos.'))