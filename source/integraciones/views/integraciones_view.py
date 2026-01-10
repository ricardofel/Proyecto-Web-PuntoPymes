import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder

# IMPORTANTE: Importamos los modelos de otras apps
# Si tus apps se llaman diferente, avísame.
from empleados.models import Empleado
from asistencia.models import EventoAsistencia

# --- 1. ENDPOINT: EXPORTAR NÓMINA (GET) ---
@require_http_methods(["GET"])
def exportar_nomina_api(request):
    """
    Genera un JSON con la lista de empleados y sus datos básicos.
    """
    try:
        empleados = Empleado.objects.all()
        data = []
        
        for emp in empleados:
            item = {
                "id": emp.id,
                "cedula": getattr(emp, 'cedula', 'S/N'),
                "nombre_completo": f"{emp.nombres} {emp.apellidos}",
                "email": emp.email,
                # Usamos getattr para evitar errores si el campo no existe
                "cargo": str(emp.puesto) if emp.puesto else "Sin Cargo",
                "salario_base": float(getattr(emp, 'salario', 0.00) or 0.00),
            }
            data.append(item)
        
        return JsonResponse({
            "sistema": "Talent Track",
            "modulo": "Nomina",
            "total_registros": len(data),
            "datos": data
        }, encoder=DjangoJSONEncoder)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --- 2. ENDPOINT: IMPORTAR EMPLEADOS (POST) ---
@csrf_exempt 
@require_http_methods(["POST"])
def importar_empleados_api(request):
    try:
        body = json.loads(request.body)
        lista_empleados = body.get('empleados', [])
        creados = 0
        errores = []

        for item in lista_empleados:
            try:
                # 👇 AQUÍ ESTÁ EL CAMBIO CLAVE:
                # Asignamos IDs fijos (1) para cumplir con las reglas de la BD.
                # Asegúrate de tener creada al menos una Empresa, Unidad y Puesto en el Admin.
                Empleado.objects.create(
                    nombres=item.get('nombres'),
                    apellidos=item.get('apellidos'),
                    cedula=item.get('cedula', '0000000000'),
                    email=item.get('email', ''),
                    fecha_ingreso=item.get('fecha_ingreso'),
                    fecha_nacimiento=item.get('fecha_nacimiento'),
                    
                    # --- CAMPOS OBLIGATORIOS (Foreign Keys) ---
                    empresa_id=1,      # Asigna a la primera empresa
                    unidad_org_id=1,   # Asigna a la primera unidad/departamento
                    puesto_id=1        # Asigna al primer puesto
                )
                creados += 1
            except Exception as e:
                errores.append(f"Error con {item.get('nombres', '?')}: {str(e)}")

        return JsonResponse({
            "estado": "procesado",
            "creados": creados,
            "errores": errores
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)


# --- 3. ENDPOINT: EVENTOS DE ASISTENCIA (GET) ---
@require_http_methods(["GET"])
def exportar_asistencia_api(request):
    """
    Exporta los últimos 50 eventos de asistencia.
    """
    try:
        eventos = EventoAsistencia.objects.all().order_by('-registrado_el')[:50]
        data = []

        for ev in eventos:
            data.append({
                "id": ev.id,
                "empleado": f"{ev.empleado.nombres} {ev.empleado.apellidos}",
                "tipo": ev.get_tipo_display(),
                "fecha_hora": ev.registrado_el,
                "origen": ev.origen
            })

        return JsonResponse({
            "total": len(data),
            "eventos": data
        }, encoder=DjangoJSONEncoder)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)