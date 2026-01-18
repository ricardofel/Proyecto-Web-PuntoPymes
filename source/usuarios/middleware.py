from core.models import Empresa

class EmpresaActualMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.empresa_actual = None

        if request.user.is_authenticated:
            es_superuser = request.user.is_superuser
            
            empresa_id_sesion = request.session.get('empresa_entorno_id')
            
            if empresa_id_sesion:

                request.empresa_actual = Empresa.objects.filter(id=empresa_id_sesion, estado=True).first()

            if not request.empresa_actual and not es_superuser:
                request.empresa_actual = getattr(request.user, "empresa", None)

        response = self.get_response(request)
        return response