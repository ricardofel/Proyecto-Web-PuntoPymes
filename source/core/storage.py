import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Ruta base para almacenamiento privado:
# BASE_DIR / private_media
PRIVATE_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "private_media")

# Crear automáticamente el directorio de almacenamiento privado si no existe.
if not os.path.exists(PRIVATE_MEDIA_ROOT):
    os.makedirs(PRIVATE_MEDIA_ROOT, exist_ok=True)


class PrivateMediaStorage(FileSystemStorage):
    """
    Storage personalizado para archivos privados.

    - Almacena los archivos fuera del directorio /media/.
    - No expone una URL pública para acceso directo.
    """

    def __init__(self, location=None, base_url=None):
        # Si no se especifica una ubicación, se usa PRIVATE_MEDIA_ROOT.
        if location is None:
            location = PRIVATE_MEDIA_ROOT

        # base_url=None evita que Django genere URLs públicas automáticamente.
        super().__init__(location, base_url)


# Instancia reutilizable para asignar directamente en modelos (storage=private_storage)
private_storage = PrivateMediaStorage()
