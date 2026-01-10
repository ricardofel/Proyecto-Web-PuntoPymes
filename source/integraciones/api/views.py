import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
from empleados.models import Empleado
from asistencia.models import EventoAsistencia
from integraciones.models import LogIntegracion, IntegracionErp # <--- IMPORTAR INTEGRACIONERP

# --- 1. EXPORTAR NÓMINA (GET) ---
# Esta puede quedar abierta o protegerse igual, para simplificar la dejaremos así o protegida si prefieres.
@require_http_methods(["GET"])
def exportar_nomina_api(request):
    endpoint_name = "/api/v1/nomina/exportar/"
    # ... (El código de exportación está bien, no es crítico para escritura) ...
    # (Mismo código que tenías arriba)
    try:
        empleados = Empleado.objects.all()
        data = []
        for emp in empleados:
            item = {
                "id": emp.id,
                "nombre_completo": f"{emp.nombres} {emp.apellidos}",
                "cargo": str(emp.puesto) if emp.puesto else "Sin Cargo",
                "salario_base": float(getattr(emp, 'salario', 0.00) or 0.00),
            }
            data.append(item)
        
        LogIntegracion.objects.create(
            endpoint=endpoint_name,
            codigo_respuesta=200,
            mensaje_respuesta=f"Exportación exitosa de {len(data)} empleados."
        )
        return JsonResponse({"datos": data}, encoder=DjangoJSONEncoder)

    except Exception as e:
        LogIntegracion.objects.create(endpoint=endpoint_name, codigo_respuesta=500, mensaje_respuesta=str(e))
        return JsonResponse({"error": str(e)}, status=500)

# --- 2. IMPORTAR EMPLEADOS (POST) - ¡AHORA BLINDADO! 🛡️ ---
@csrf_exempt 
@require_http_methods(["POST"])
def importar_empleados_api(request):
    endpoint_name = "/api/v1/empleados/importar/"
    
    # --- 🔒 INICIO SEGURIDAD: VERIFICAR API KEY ---
    api_key_recibida = request.headers.get('X-API-KEY')
    
    if not api_key_recibida:
        LogIntegracion.objects.create(
            endpoint=endpoint_name,
            codigo_respuesta=401,
            mensaje_respuesta="Intento de acceso sin API Key."
        )
        return JsonResponse({"error": "No autorizado. Falta API Key."}, status=401)
    
    # Buscamos si existe alguna integración activa con esa llave
    existe_permiso = IntegracionErp.objects.filter(api_key=api_key_recibida, activo=True).exists()
    
    if not existe_permiso:
        LogIntegracion.objects.create(
            endpoint=endpoint_name,
            codigo_respuesta=403,
            mensaje_respuesta=f"API Key inválida o inactiva: {api_key_recibida[:5]}***"
        )
        return JsonResponse({"error": "Credenciales inválidas o integración pausada."}, status=403)
    # --- 🔓 FIN SEGURIDAD ---

    try:
        body = json.loads(request.body)
        lista_empleados = body.get('empleados', [])
        creados = 0
        errores = []

        for item in lista_empleados:
            try:
                # Nota: Asegúrate de que existan empresa/unidad/puesto con ID 1 en tu DB
                # o el sistema fallará aquí.
                Empleado.objects.create(
                    nombres=item.get('nombres'),
                    apellidos=item.get('apellidos'),
                    cedula=item.get('cedula', '0000000000'),
                    email=item.get('email', ''), # El email es vital para que se cree el usuario automático
                    fecha_ingreso=item.get('fecha_ingreso'),
                    fecha_nacimiento=item.get('fecha_nacimiento'),
                    empresa_id=1, unidad_org_id=1, puesto_id=1 
                )
                creados += 1
            except Exception as e:
                errores.append(f"Error con {item.get('nombres', '?')}: {str(e)}")

        LogIntegracion.objects.create(
            integracion=IntegracionErp.objects.filter(api_key=api_key_recibida).first(), # Vinculamos el log a la integración real
            endpoint=endpoint_name,
            codigo_respuesta=201 if creados > 0 else 400,
            mensaje_respuesta=f"Creados: {creados}, Errores: {len(errores)}"
        )

        return JsonResponse({"estado": "procesado", "creados": creados, "errores": errores}, status=201)
        
    except json.JSONDecodeError:
        LogIntegracion.objects.create(endpoint=endpoint_name, codigo_respuesta=400, mensaje_respuesta="JSON inválido")
        return JsonResponse({"error": "JSON inválido"}, status=400)

# --- 3. EVENTOS ASISTENCIA ---
@require_http_methods(["GET"])
def exportar_asistencia_api(request):
    # (El código original está bien)
    endpoint_name = "/api/v1/asistencia/eventos/"
    try:
        eventos = EventoAsistencia.objects.all().order_by('-registrado_el')[:50]
        data = [{"empleado": str(ev.empleado), "tipo": ev.get_tipo_display(), "fecha": ev.registrado_el} for ev in eventos]
        
        LogIntegracion.objects.create(
            endpoint=endpoint_name,
            codigo_respuesta=200,
            mensaje_respuesta=f"Exportados {len(data)} eventos."
        )

        return JsonResponse({"eventos": data}, encoder=DjangoJSONEncoder)
    except Exception as e:
        LogIntegracion.objects.create(endpoint=endpoint_name, codigo_respuesta=500, mensaje_respuesta=str(e))
        return JsonResponse({"error": str(e)}, status=500)