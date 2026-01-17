from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny

# Imports de modelos (Rutas absolutas)
from integraciones.models import IntegracionErp, Webhook, LogIntegracion
from empleados.models import Empleado
from asistencia.models import EventoAsistencia

# Imports de servicios y serializadores
from integraciones.services.integracion_service import IntegracionService
from .serializers import (
    IntegracionErpSerializer, 
    WebhookSerializer, 
    LogIntegracionSerializer
)

class IntegracionErpViewSet(viewsets.ModelViewSet):
    """
    API para gestionar conexiones ERP.
    Incluye endpoints personalizados para sincronización de datos.
    """
    queryset = IntegracionErp.objects.all().order_by('nombre')
    serializer_class = IntegracionErpSerializer
    # Por defecto protegemos todo, pero en las acciones personalizadas
    # gestionaremos la seguridad vía API Key si es necesario.
    permission_classes = [IsAdminUser] 

    # --- ACCIÓN 1: IMPORTAR EMPLEADOS (POST) ---
    # URL: /api/integraciones/erp/importar_empleados/
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='importar-empleados')
    def importar_empleados(self, request):
        """
        Recibe un JSON con empleados desde el ERP y los crea/actualiza en el sistema.
        Valida la seguridad mediante X-API-KEY en el header.
        """
        api_key = request.headers.get('X-API-KEY')
        
        # 1. Validación de Seguridad Manual (API Key)
        integracion = IntegracionErp.objects.filter(api_key=api_key, activo=True).first()
        if not integracion:
             return Response({"error": "Unauthorized / API Key inválida"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # DRF ya procesa el JSON en request.data
            empleados_data = request.data.get('empleados', [])
            
            # 2. Delegar al servicio (Lógica de negocio)
            creados, errores = IntegracionService.importar_empleados(empleados_data, api_key)
            
            # 3. Loguear resultado (Auditoría)
            LogIntegracion.objects.create(
                integracion=integracion,
                endpoint="/api/integraciones/erp/importar-empleados/",
                codigo_respuesta=201 if not errores else 206, 
                mensaje_respuesta=f"Procesados: {len(empleados_data)}. Creados: {creados}. Errores: {len(errores)}"
            )

            return Response({"creados": creados, "errores": errores}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # --- ACCIÓN 2: EXPORTAR NÓMINA (GET) ---
    # URL: /api/integraciones/erp/exportar_nomina/
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser], url_path='exportar-nomina')
    def exportar_nomina(self, request):
        """
        Genera un JSON con la data necesaria para el cálculo de nómina externo.
        """
        try:
            # Optimización de consulta (Join)
            empleados = Empleado.objects.select_related('puesto', 'unidad_org').all()
            
            data = []
            for emp in empleados:
                # Nota: Asegúrate de que tu modelo Empleado tenga el campo 'salario' 
                # o ajusta aquí para sacarlo del último contrato activo.
                salario_actual = getattr(emp, 'salario', 0) 
                
                data.append({
                    "id": emp.id,
                    "nombre": f"{emp.nombres} {emp.apellidos}",
                    "cargo": emp.puesto.nombre if emp.puesto else "S/N",
                    "departamento": emp.unidad_org.nombre if emp.unidad_org else "S/N",
                    "salario": float(salario_actual)
                })
            
            return Response({"datos": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- ACCIÓN 3: EXPORTAR ASISTENCIA (GET) ---
    # URL: /api/integraciones/erp/exportar_asistencia/
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser], url_path='exportar-asistencia')
    def exportar_asistencia(self, request):
        """
        Devuelve los últimos 50 registros de asistencia para sincronización.
        """
        try:
            eventos = EventoAsistencia.objects.select_related('empleado').order_by('-registrado_el')[:50]
            
            data = [{
                "fecha": ev.registrado_el,
                "empleado": f"{ev.empleado.nombres} {ev.empleado.apellidos}",
                "tipo": ev.get_tipo_display()
            } for ev in eventos]

            return Response({"eventos": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebhookViewSet(viewsets.ModelViewSet):
    queryset = Webhook.objects.all().order_by('nombre')
    serializer_class = WebhookSerializer
    permission_classes = [IsAdminUser]


class LogIntegracionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogIntegracion.objects.select_related('integracion', 'webhook').all().order_by('-fecha')
    serializer_class = LogIntegracionSerializer
    permission_classes = [IsAdminUser]