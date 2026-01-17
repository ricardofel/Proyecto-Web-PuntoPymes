import requests
import json
from django.utils import timezone
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from integraciones.models import LogIntegracion
from integraciones.constants import EstadoIntegracion

# Importaciones condicionales para evitar ciclos si fuera necesario
from empleados.models import Empleado
from asistencia.models import EventoAsistencia

class IntegracionService:
    
    @staticmethod
    def probar_conexion_erp(erp):
        """Realiza un PING al ERP y actualiza su estado."""
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
        
        erp.save(update_fields=['estado_sincronizacion', 'fecha_ultima_sincronizacion'])
        
        # Logueamos el resultado
        LogIntegracion.objects.create(
            integracion=erp,
            endpoint=erp.url_api,
            codigo_respuesta=codigo,
            mensaje_respuesta=mensaje
        )
        return exito, mensaje

    @staticmethod
    def disparar_webhook(webhook, payload):
        """Envía datos a un webhook."""
        try:
            response = requests.post(
                webhook.url_destino, 
                json=payload, 
                timeout=5,
                headers={'Content-Type': 'application/json'}
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
            mensaje_respuesta=mensaje
        )
        return codigo

    @staticmethod
    @transaction.atomic
    def importar_empleados(lista_data, api_key):
        """Lógica de importación masiva de empleados."""
        creados = 0
        errores = []
        
        # Validar IDs por defecto (esto debería venir de configuración, pero por ahora protegemos)
        # Podríamos buscar la primera empresa activa en lugar de hardcodear ID=1
        
        for item in lista_data:
            try:
                # Usamos get_or_create para evitar duplicados por email
                email = item.get('email')
                if not email:
                    raise ValueError("Email es obligatorio")

                empleado, created = Empleado.objects.get_or_create(
                    email=email,
                    defaults={
                        'nombres': item.get('nombres'),
                        'apellidos': item.get('apellidos'),
                        'cedula': item.get('cedula', 'S/N'),
                        'fecha_ingreso': item.get('fecha_ingreso'),
                        # Asignamos valores por defecto seguros
                        'empresa_id': 1, 
                        'unidad_org_id': 1,
                        'puesto_id': 1
                    }
                )
                if created:
                    creados += 1
            except Exception as e:
                errores.append(f"Fila {item.get('nombres', '?')}: {str(e)}")
        
        return creados, errores