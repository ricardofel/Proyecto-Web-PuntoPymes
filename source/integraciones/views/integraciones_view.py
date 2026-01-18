import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from django.core.serializers.json import DjangoJSONEncoder

from empleados.models import Empleado
from asistencia.models import EventoAsistencia


@require_safe
def exportar_nomina_api(request):
    """
    Exporta un JSON con empleados y datos básicos para nómina.
    Acceso de solo lectura (GET).
    """
    try:
        empleados = Empleado.objects.all()
        data = []

        for emp in empleados:
            item = {
                "id": emp.id,
                "cedula": getattr(emp, "cedula", "S/N"),
                "nombre_completo": f"{emp.nombres} {emp.apellidos}",
                "email": emp.email,
                "cargo": str(emp.puesto) if emp.puesto else "Sin Cargo",
                "salario_base": float(getattr(emp, "salario", 0.00) or 0.00),
            }
            data.append(item)

        return JsonResponse(
            {
                "sistema": "Talent Track",
                "modulo": "Nomina",
                "total_registros": len(data),
                "datos": data,
            },
            encoder=DjangoJSONEncoder,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def importar_empleados_api(request):
    """
    Importa empleados desde un JSON recibido por POST.
    Exento de CSRF para permitir integraciones externas (API).
    """
    try:
        body = json.loads(request.body)
        lista_empleados = body.get("empleados", [])
        creados = 0
        errores = []

        for item in lista_empleados:
            try:
                Empleado.objects.create(
                    nombres=item.get("nombres"),
                    apellidos=item.get("apellidos"),
                    cedula=item.get("cedula", "0000000000"),
                    email=item.get("email", ""),
                    fecha_ingreso=item.get("fecha_ingreso"),
                    fecha_nacimiento=item.get("fecha_nacimiento"),
                    empresa_id=1,
                    unidad_org_id=1,
                    puesto_id=1,
                )
                creados += 1
            except Exception as e:
                errores.append(f"Error con {item.get('nombres', '?')}: {str(e)}")

        return JsonResponse(
            {
                "estado": "procesado",
                "creados": creados,
                "errores": errores,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_safe
def exportar_asistencia_api(request):
    """
    Exporta los últimos 50 eventos de asistencia.
    Acceso de solo lectura (GET).
    """
    try:
        eventos = EventoAsistencia.objects.all().order_by("-registrado_el")[:50]
        data = []

        for ev in eventos:
            data.append(
                {
                    "id": ev.id,
                    "empleado": f"{ev.empleado.nombres} {ev.empleado.apellidos}",
                    "tipo": ev.get_tipo_display(),
                    "fecha_hora": ev.registrado_el,
                    "origen": ev.origen,
                }
            )

        return JsonResponse(
            {
                "total": len(data),
                "eventos": data,
            },
            encoder=DjangoJSONEncoder,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)