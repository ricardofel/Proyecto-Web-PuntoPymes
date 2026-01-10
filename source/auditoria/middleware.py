import threading

# Almacén temporal para guardar el usuario en el hilo actual
_thread_locals = threading.local()

def get_current_user():
    """Devuelve el usuario que está haciendo la petición actual (o None)"""
    return getattr(_thread_locals, 'user', None)

class AuditoriaMiddleware:
    """
    Middleware que intercepta cada petición al servidor,
    agarra al usuario (request.user) y lo guarda en el almacén temporal
    para que signals.py lo pueda consultar después.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Antes de que la vista procese nada: Guardamos al usuario
        _thread_locals.user = getattr(request, 'user', None)
        
        response = self.get_response(request)
        
        # 2. Después (Limpieza): No es estrictamente necesario en hilos modernos, 
        # pero es buena práctica no dejar basura.
        return response