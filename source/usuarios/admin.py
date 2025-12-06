from django.contrib import admin
from .models import Usuario, Rol, UsuarioRol

# Esto habilita la gestión visual en /admin/
admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(UsuarioRol)
