import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder

from empleados.models import Empleado
from asistencia.models import EventoAsistencia
from integraciones.models import IntegracionErp, LogIntegracion
from integraciones.services.integracion_service import IntegracionService

@require_http_methods(["GET"])
def exportar_nomina_api(request):
    try:
        # OPTIMIZACIÓN: select_related para traer puesto y unidad en la misma consulta
        empleados = Empleado.objects.select_related('puesto', 'unidad_org').all()
        
        data = []
        for emp in empleados:
            data.append({
                "id": emp.id,
                "nombre": f"{emp.nombres} {emp.apellidos}",
                "cargo": emp.puesto.nombre if emp.puesto else "S/N", # Sin DB hit extra
                "departamento": emp.unidad_org.nombre if emp.unidad_org else "S/N",
                "salario": float(emp.salario)
            })
        
        return JsonResponse({"datos": data}, encoder=DjangoJSONEncoder)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt 
@require_http_methods(["POST"])
def importar_empleados_api(request):
    api_key = request.headers.get('X-API-KEY')
    
    # 1. Validación API Key (simplificada)
    integracion = IntegracionErp.objects.filter(api_key=api_key, activo=True).first()
    if not integracion:
         return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        body = json.loads(request.body)
        empleados_data = body.get('empleados', [])
        
        # 2. Delegar al servicio
        creados, errores = IntegracionService.importar_empleados(empleados_data, api_key)
        
        # 3. Loguear resultado
        LogIntegracion.objects.create(
            integracion=integracion,
            endpoint="/api/v1/importar/",
            codigo_respuesta=201 if not errores else 206, # 206 Partial Content
            mensaje_respuesta=f"Creados: {creados}. Errores: {len(errores)}"
        )

        return JsonResponse({"creados": creados, "errores": errores})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@require_http_methods(["GET"])
def exportar_asistencia_api(request):
    try:
        # OPTIMIZACIÓN: Traer datos del empleado de una vez
        eventos = EventoAsistencia.objects.select_related('empleado').order_by('-registrado_el')[:50]
        
        data = [{
            "fecha": ev.registrado_el,
            "empleado": f"{ev.empleado.nombres} {ev.empleado.apellidos}", # Sin DB hit extra
            "tipo": ev.get_tipo_display()
        } for ev in eventos]

        return JsonResponse({"eventos": data}, encoder=DjangoJSONEncoder)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)