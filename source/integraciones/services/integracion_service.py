import requests
from django.utils import timezone
from django.db import transaction

from integraciones.models import LogIntegracion
from integraciones.constants import EstadoIntegracion

from empleados.models import Empleado, Puesto
from core.models import Empresa, UnidadOrganizacional


class IntegracionService:
    @staticmethod
    def probar_conexion_erp(erp):
        """
        Realiza una prueba de conectividad al ERP y actualiza su estado.
        """
        try:
            response = requests.get(erp.url_api, timeout=5)

            if 200 <= response.status_code < 500:
                erp.estado_sincronizacion = EstadoIntegracion.EXITOSO
                erp.fecha_ultima_sincronizacion = timezone.now()
                mensaje = f"Conexión exitosa. Tiempo: {response.elapsed.total_seconds()}s"
                codigo = response.status_code
                exito = True
            else:
                raise Exception(f"Error interno del servidor remoto: {response.status_code}")

        except Exception as e:
            erp.estado_sincronizacion = EstadoIntegracion.ERROR
            mensaje = f"Fallo de conexión: {str(e)}"[:200]
            codigo = 0
            exito = False

        erp.save(update_fields=["estado_sincronizacion", "fecha_ultima_sincronizacion"])

        LogIntegracion.objects.create(
            integracion=erp,
            endpoint=erp.url_api,
            codigo_respuesta=codigo,
            mensaje_respuesta=mensaje,
        )
        return exito, mensaje

    @staticmethod
    def disparar_webhook(webhook, payload):
        """
        Envía un POST a un webhook y registra el resultado.
        """
        try:
            response = requests.post(
                webhook.url_destino,
                json=payload,
                timeout=5,
                headers={"Content-Type": "application/json"},
            )
            codigo = response.status_code
            mensaje = f"Enviado. Respuesta: {response.text[:100]}"
        except Exception as e:
            codigo = 0
            mensaje = f"Error envío: {str(e)}"

        LogIntegracion.objects.create(
            webhook=webhook,
            endpoint=webhook.url_destino,
            codigo_respuesta=codigo,
            mensaje_respuesta=mensaje,
        )
        return codigo

    @staticmethod
    @transaction.atomic
    def importar_empleados(lista_data, api_key):
        """
        Importación masiva de empleados.

        Selecciona empresa/unidad/puesto por defecto de forma dinámica
        para evitar IDs hardcodeados.
        """
        creados = 0
        errores = []

        empresa_default = Empresa.objects.first()
        if not empresa_default:
            return 0, [
                "Error crítico: No existen empresas registradas en el sistema para asociar los empleados."
            ]

        unidad_default = UnidadOrganizacional.objects.filter(empresa=empresa_default).first()
        if not unidad_default:
            return 0, [
                f"Error crítico: La empresa '{empresa_default.nombre_comercial}' no tiene unidades organizacionales creadas."
            ]

        puesto_default = Puesto.objects.filter(empresa=empresa_default).first()
        if not puesto_default:
            return 0, [
                f"Error crítico: La empresa '{empresa_default.nombre_comercial}' no tiene puestos creados."
            ]

        for item in lista_data:
            try:
                email = item.get("email")
                if not email:
                    raise ValueError("Email es obligatorio")

                empleado, created = Empleado.objects.get_or_create(
                    email=email,
                    defaults={
                        "nombres": item.get("nombres"),
                        "apellidos": item.get("apellidos"),
                        "cedula": item.get("cedula", "S/N"),
                        "fecha_ingreso": item.get("fecha_ingreso"),
                        "empresa": empresa_default,
                        "unidad_org": unidad_default,
                        "puesto": puesto_default,
                    },
                )
                if created:
                    creados += 1
            except Exception as e:
                errores.append(f"Fila {item.get('nombres', '?')}: {str(e)}")

        return creados, errores
