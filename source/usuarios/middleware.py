# empresas/middleware.py
class EmpresaActualMiddleware:
    """
    Middleware que inyecta la empresa actual en el objeto request.

    Si el usuario está autenticado y tiene una empresa asociada,
    se expone como `request.empresa_actual` para su uso en vistas,
    servicios y plantillas.
    """

    def __init__(self, get_response):
        # Función que procesa la solicitud siguiente en la cadena de middleware
        self.get_response = get_response

    def __call__(self, request):
        # Valor por defecto cuando no hay usuario autenticado o empresa asociada
        request.empresa_actual = None

        if request.user.is_authenticated:
            # Obtiene la empresa asociada al usuario, si existe
            request.empresa_actual = getattr(request.user, "empresa", None)

        response = self.get_response(request)
        return response
