from django.utils.deprecation import MiddlewareMixin
from core.models import Empresa

class EmpresaContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Define `request.empresa_actual` globalmente basándose en el rol y la sesión.
        """
        request.empresa_actual = None # Por defecto arrancamos sin empresa
        
        if not request.user.is_authenticated:
            return

        # Intentamos obtener el perfil de empleado del usuario
        # (Asumiendo que tienes una relación OneToOne o similar, o usas related_name='empleado')
        # Si tu relación es distinta, ajusta esta línea.
        empleado = getattr(request.user, 'empleado', None)
        
        # --- LÓGICA DE ROLES ---
        
        # CASO A: SuperAdmin (Puede "viajar" entre empresas)
        # Verificamos si es superuser de Django O si tiene el rol de negocio de SuperAdmin
        es_superadmin = request.user.is_superuser or getattr(request.user, "es_superadmin_negocio", False)

        if es_superadmin:
            # 1. ¿Viene el ID en la URL? (ej: ?empresa_id=5) -> Prioridad Máxima
            empresa_id_url = request.GET.get('empresa_id')
            
            if empresa_id_url:
                try:
                    # Buscamos la empresa y la guardamos en el request
                    request.empresa_actual = Empresa.objects.get(id=empresa_id_url, estado=True)
                    # La guardamos también en la sesión del navegador para recordarla en el siguiente clic
                    request.session['empresa_actual_id'] = request.empresa_actual.id
                except Empresa.DoesNotExist:
                    pass
            
            # 2. Si no viene en URL, ¿la tenemos guardada de antes en la sesión?
            elif 'empresa_actual_id' in request.session:
                try:
                    request.empresa_actual = Empresa.objects.get(id=request.session['empresa_actual_id'], estado=True)
                except Empresa.DoesNotExist:
                    # Si la empresa fue borrada pero el ID seguía en sesión, limpiamos.
                    del request.session['empresa_actual_id'] 

        # CASO B: Mortales (Admin RRHH, Empleado, Manager) -> Atados a su empresa
        # Si tiene perfil de empleado y ese empleado tiene empresa asignada...
        elif empleado and empleado.empresa:
            # Forzamos su empresa real. No pueden salir de ahí.
            request.empresa_actual = empleado.empresa