from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.apps import apps
from notificaciones.models import Notificacion

# Traemos el modelo de Usuario
User = get_user_model()

# --- HELPER: Enviar a todos los jefes (Superusuarios) ---
def notificar_superusuarios(titulo, mensaje, tipo='info', link=None):
    jefes = User.objects.filter(is_superuser=True)
    msgs = []
    for jefe in jefes:
        msgs.append(Notificacion(
            usuario=jefe,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            link=link  # <--- CORREGIDO: Usamos el argumento que recibimos
        ))
    Notificacion.objects.bulk_create(msgs)

# 1. EMPLEADOS
@receiver(post_save, sender='empleados.Empleado')
def aviso_nuevo_empleado(sender, instance, created, **kwargs):
    if created:
        notificar_superusuarios(
            titulo="🎉 Nuevo Ingreso",
            mensaje=f"Se ha contratado a {instance}...",
            tipo='success',
            # 👇 AQUÍ ESTÁ EL TRUCO: Le decimos "Cuando salgas de aquí, vuelve a notificaciones"
            link=f"/detalles/empleados/empleado/{instance.id}/?next=/notificaciones/"
        )

# 2. SOLICITUDES
@receiver(post_save, sender='solicitudes.SolicitudAusencia')
def aviso_nueva_solicitud(sender, instance, created, **kwargs):
    if created:
        notificar_superusuarios(
            titulo="📄 Nueva Solicitud",
            mensaje=f"{instance.empleado} solicita...",
            tipo='info',
            # 👇 Truco aplicado
            link=f"/detalles/solicitudes/solicitudausencia/{instance.id}/?next=/notificaciones/"
        )

# 3. USUARIOS
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def aviso_nuevo_usuario(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        notificar_superusuarios(
            titulo="👤 Usuario Registrado",
            mensaje=f"Usuario {instance.email} creado...",
            tipo='warning',
            # 👇 Truco aplicado
            link=f"/detalles/usuarios/usuario/{instance.id}/?next=/notificaciones/"
        )