# empresas/middleware.py
from .models import Empresa


class EmpresaActualMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.empresa_actual = None

        if request.user.is_authenticated:
            request.empresa_actual = getattr(request.user, "empresa", None)

        response = self.get_response(request)
        return response
