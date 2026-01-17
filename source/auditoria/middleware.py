import threading

# Almacén temporal para guardar el usuario en el hilo actual
_thread_locals = threading.local()

def get_current_user():
    """Devuelve el usuario que está haciendo la petición actual (o None)"""
    return getattr(_thread_locals, 'user', None)

class AuditoriaMiddleware:
    """
    Middleware que intercepta cada petición, guarda el usuario
    y LIMPIA al salir.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Entrada: Guardamos al usuario
        _thread_locals.user = getattr(request, 'user', None)
        
        try:
            response = self.get_response(request)
        finally:
            # 2. Salida (CRÍTICO): Limpiamos la referencia para no contaminar hilos
            _thread_locals.user = None
            
        return response