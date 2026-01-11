import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Definimos la ruta: Raíz del proyecto + 'private_media'
PRIVATE_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'private_media')

# === AUTOMATIZACIÓN ===
# Si la carpeta no existe, el sistema la crea automáticamente.
if not os.path.exists(PRIVATE_MEDIA_ROOT):
    os.makedirs(PRIVATE_MEDIA_ROOT, exist_ok=True)

class PrivateMediaStorage(FileSystemStorage):
    """
    Storage personalizado que guarda archivos en una carpeta protegida
    fuera del acceso público habitual (/media/).
    """
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = PRIVATE_MEDIA_ROOT
        # base_url=None evita que Django intente generar una URL pública automática
        super().__init__(location, base_url)

# Instancia lista para usar en los modelos
private_storage = PrivateMediaStorage()