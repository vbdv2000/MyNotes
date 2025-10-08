from slowapi import Limiter
from slowapi.util import get_remote_address

# Crear el limitador basado en la IP del cliente
limiter = Limiter(key_func=get_remote_address)

# Configuración de límites por endpoint
AUTH_LIMIT = "5/minute"  # Límite de intentos de login
CREATE_LIMIT = "30/minute"  # Límite de creación de recursos
READ_LIMIT = "60/minute"  # Límite de lectura de recursos
