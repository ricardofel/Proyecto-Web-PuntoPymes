import threading

# Almacén thread-local para el usuario de la petición actual
_thread_locals = threading.local()


def get_current_user():
    """Devuelve el usuario asociado a la petición actual (o None)."""
    return getattr(_thread_locals, "user", None)


class AuditoriaMiddleware:
    """
    Middleware que guarda el usuario autenticado en thread-local
    durante el ciclo de vida de la petición y lo limpia al finalizar.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Entrada: asociar el usuario al hilo actual
        _thread_locals.user = getattr(request, "user", None)

        try:
            response = self.get_response(request)
        finally:
            # Salida: limpiar el thread-local para evitar fugas entre peticiones
            _thread_locals.user = None

        return response
