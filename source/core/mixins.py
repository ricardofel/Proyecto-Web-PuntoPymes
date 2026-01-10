from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class FiltradoEmpresaMixin(LoginRequiredMixin):
    """
    Mixin mágico: 
    1. Filtra automáticamente cualquier QuerySet por la empresa actual.
    2. Inyecta la variable {{ empresa_actual }} en todas las plantillas.
    """
    
    def get_queryset(self):
        # 1. Obtenemos la consulta original de la vista (ej: Empleado.objects.all())
        qs = super().get_queryset()
        
        # 2. Si por alguna razón no hay empresa (ej: error raro), devolvemos lista vacía por seguridad
        if not getattr(self.request, 'empresa_actual', None):
            return qs.none()
            
        # 3. FILTRO MAESTRO: Filtramos por el campo 'empresa'
        # Esto asume que tus modelos (Empleado, Unidad, etc.) tienen un campo llamado 'empresa'
        return qs.filter(empresa=self.request.empresa_actual)

    def get_context_data(self, **kwargs):
        # Esto hace que {{ empresa_actual }} esté disponible en el HTML automáticamente
        context = super().get_context_data(**kwargs)
        context['empresa_actual'] = getattr(self.request, 'empresa_actual', None)
        return context