from django.contrib import admin
from .models import Empresa, UnidadOrganizacional 

# Registramos los modelos para que aparezcan en el panel
admin.site.register(Empresa)
admin.site.register(UnidadOrganizacional)