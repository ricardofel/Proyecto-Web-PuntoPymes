from django.utils.deprecation import MiddlewareMixin
from core.models import Empresa


class EmpresaContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Define `request.empresa_actual` para todo el ciclo de la petición.

        La empresa activa se determina según:
        - Rol del usuario (superadmin vs usuario estándar).
        - Parámetro en la URL (?empresa_id=).
        - Valor persistido en la sesión.
        """

        # Valor por defecto: sin empresa asignada.
        request.empresa_actual = None

        # Si el usuario no está autenticado, no se define contexto de empresa.
        if not request.user.is_authenticated:
            return

        # Obtener el perfil de empleado asociado al usuario (si existe).
        empleado = getattr(request.user, "empleado", None)

        # Determinar si el usuario tiene privilegios de superadministrador.
        # Se consideran tanto el superuser de Django como un flag de negocio.
        es_superadmin = request.user.is_superuser or getattr(
            request.user, "es_superadmin_negocio", False
        )

        # Caso A: Superadmin (puede cambiar libremente de empresa).
        if es_superadmin:
            # Prioridad 1: empresa indicada explícitamente en la URL.
            empresa_id_url = request.GET.get("empresa_id")

            if empresa_id_url:
                try:
                    request.empresa_actual = Empresa.objects.get(
                        id=empresa_id_url,
                        estado=True,
                    )
                    # Persistir selección en sesión para futuras peticiones.
                    request.session["empresa_actual_id"] = request.empresa_actual.id
                except Empresa.DoesNotExist:
                    # Si el ID no es válido, se ignora silenciosamente.
                    pass

            # Prioridad 2: empresa almacenada previamente en la sesión.
            elif "empresa_actual_id" in request.session:
                try:
                    request.empresa_actual = Empresa.objects.get(
                        id=request.session["empresa_actual_id"],
                        estado=True,
                    )
                except Empresa.DoesNotExist:
                    # Limpiar sesión si la empresa ya no existe.
                    del request.session["empresa_actual_id"]

        # Caso B: Usuarios estándar (empresa fija).
        elif empleado and empleado.empresa:
            # El usuario queda restringido a la empresa asociada a su perfil.
            request.empresa_actual = empleado.empresa
