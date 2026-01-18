from django.contrib.auth.mixins import LoginRequiredMixin

class FiltradoEmpresaMixin(LoginRequiredMixin):
    """
    Mixin de filtrado por empresa.

    Responsabilidades:
    1. Filtrar automáticamente el QuerySet por la empresa actual.
    2. Exponer la variable `empresa_actual` al contexto de la plantilla.
    """

    def get_queryset(self):
        # Obtener el QuerySet base definido por la vista.
        qs = super().get_queryset()

        # Comportamiento defensivo:
        # si no existe empresa_actual en el request, retornar QuerySet vacío.
        if not getattr(self.request, "empresa_actual", None):
            return qs.none()

        # Filtrado principal por empresa.
        # Se asume que el modelo posee un campo ForeignKey llamado `empresa`.
        return qs.filter(empresa=self.request.empresa_actual)

    def get_context_data(self, **kwargs):
        # Inyectar empresa_actual en el contexto para uso en plantillas.
        context = super().get_context_data(**kwargs)
        context["empresa_actual"] = getattr(self.request, "empresa_actual", None)
        return context
