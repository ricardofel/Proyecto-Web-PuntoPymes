from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    rol = models.CharField(
        max_length=50,
        choices=[
            ("SUPERADMIN", "Super Admin"),
            ("ADMIN_RRHH", "Admin RRHH"),
            ("MANAGER", "Manager"),
            ("EMPLEADO", "Empleado"),
        ],
        default="EMPLEADO",
    )

    def __str__(self):
        return f"{self.username} ({self.rol})"
