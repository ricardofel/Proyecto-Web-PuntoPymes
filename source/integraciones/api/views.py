from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny

from integraciones.models import IntegracionErp, Webhook, LogIntegracion
from empleados.models import Empleado
from asistencia.models import EventoAsistencia

from integraciones.services.integracion_service import IntegracionService
from .serializers import (
    IntegracionErpSerializer,
    WebhookSerializer,
    LogIntegracionSerializer,
)


class IntegracionErpViewSet(viewsets.ModelViewSet):
    """
    API para gestionar conexiones ERP.

    Incluye endpoints personalizados para:
    - Importación de empleados (API Key).
    - Exportación de nómina.
    - Exportación de asistencia.
    """
    queryset = IntegracionErp.objects.all().order_by("nombre")
    serializer_class = IntegracionErpSerializer

    # Por defecto, el CRUD queda restringido a administradores.
    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="importar-empleados",
    )
    def importar_empleados(self, request):
        """
        Importa empleados desde un ERP.

        Seguridad:
        - Se valida manualmente el header X-API-KEY contra IntegracionErp activa.
        """
        api_key = request.headers.get("X-API-KEY")

        integracion = IntegracionErp.objects.filter(api_key=api_key, activo=True).first()
        if not integracion:
            return Response(
                {"error": "Unauthorized / API Key inválida"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            empleados_data = request.data.get("empleados", [])
            creados, errores = IntegracionService.importar_empleados(empleados_data, api_key)

            LogIntegracion.objects.create(
                integracion=integracion,
                endpoint="/api/integraciones/erp/importar-empleados/",
                codigo_respuesta=201 if not errores else 206,
                mensaje_respuesta=(
                    f"Procesados: {len(empleados_data)}. Creados: {creados}. Errores: {len(errores)}"
                ),
            )

            return Response(
                {"creados": creados, "errores": errores},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAdminUser],
        url_path="exportar-nomina",
    )
    def exportar_nomina(self, request):
        """
        Exporta información básica para cálculo de nómina externo.
        """
        try:
            empleados = Empleado.objects.select_related("puesto", "unidad_org").all()

            data = []
            for emp in empleados:
                salario_actual = getattr(emp, "salario", 0)

                data.append(
                    {
                        "id": emp.id,
                        "nombre": f"{emp.nombres} {emp.apellidos}",
                        "cargo": emp.puesto.nombre if emp.puesto else "S/N",
                        "departamento": emp.unidad_org.nombre if emp.unidad_org else "S/N",
                        "salario": float(salario_actual),
                    }
                )

            return Response({"datos": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAdminUser],
        url_path="exportar-asistencia",
    )
    def exportar_asistencia(self, request):
        """
        Exporta los últimos 50 eventos de asistencia.
        """
        try:
            eventos = (
                EventoAsistencia.objects.select_related("empleado")
                .order_by("-registrado_el")[:50]
            )

            data = [
                {
                    "fecha": ev.registrado_el,
                    "empleado": f"{ev.empleado.nombres} {ev.empleado.apellidos}",
                    "tipo": ev.get_tipo_display(),
                }
                for ev in eventos
            ]

            return Response({"eventos": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebhookViewSet(viewsets.ModelViewSet):
    """
    CRUD de webhooks (admin).
    """
    queryset = Webhook.objects.all().order_by("nombre")
    serializer_class = WebhookSerializer
    permission_classes = [IsAdminUser]


class LogIntegracionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Solo lectura: auditoría de integraciones.
    """
    queryset = LogIntegracion.objects.select_related("integracion", "webhook").all().order_by("-fecha")
    serializer_class = LogIntegracionSerializer
    permission_classes = [IsAdminUser]
