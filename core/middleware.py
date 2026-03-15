"""
Middleware personalizado para la aplicación Ecommerce.
Proporciona utilidades de logging, validación y seguridad.
"""

import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class HeaderLoggingMiddleware(MiddlewareMixin):
    """
    Middleware que registra información de headers críticos para debugging.
    """
    
    def process_request(self, request):
        """Log de requests importantes"""
        if request.method == 'POST':
            # Log de POST requests para debugging
            logger.debug(
                f"POST Request: {request.path} "
                f"from {request.META.get('REMOTE_ADDR')}"
            )
        return None
    
    def process_response(self, request, response):
        """Log de respuestas críticas"""
        if response.status_code >= 400:
            logger.warning(
                f"Status {response.status_code}: {request.method} {request.path}"
            )
        return response


class DatabaseConnectionMiddleware(MiddlewareMixin):
    """
    Middleware que asegura que las conexiones a BD se cierren correctamente.
    Útil para evitar problemas en Railway con conexiones PostgreSQL.
    """
    
    def process_response(self, request, response):
        """Asegurar cierre de conexiones al final del request"""
        from django.db import connection
        connection.close()
        return response
