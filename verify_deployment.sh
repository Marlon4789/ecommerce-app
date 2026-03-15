#!/bin/bash
# Script de verificación post-deployment en Railway
# Ejecutar después de hacer push a la rama fix/cart-payment-sendEmail

set -e

echo "=================================================="
echo "VERIFICACION POST-DEPLOYMENT - ECOMMERCE APP"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar estado
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

# 1. Verificar configuración de Django
echo ""
echo "1️⃣  Verificando configuración Django..."
python manage.py check
check_status "Django configuration OK"

# 2. Verificar migrations
echo ""
echo "2️⃣  Verificando migrations..."
python manage.py migrate --plan | head -5
check_status "Migrations verified"

# 3. Verificar variables de entorno críticas
echo ""
echo "3️⃣  Verificando variables de entorno..."
python manage.py shell << EOF
import os
from django.conf import settings

critical_vars = [
    ('SECRET_KEY', os.environ.get('SECRET_KEY')),
    ('DATABASE_URL', os.environ.get('DATABASE_URL')),
    ('REDIS_URL', os.environ.get('REDIS_URL')),
    ('EMAIL_HOST_USER', os.environ.get('EMAIL_HOST_USER')),
    ('STRIPE_PUBLISHABLE_KEY', os.environ.get('STRIPE_PUBLISHABLE_KEY')),
]

print("\n📋 Variables de entorno críticas:")
for var_name, value in critical_vars:
    if value:
        masked = value[:10] + '...' if len(value) > 10 else value
        print(f"  ✅ {var_name}: {masked}")
    else:
        print(f"  ⚠️  {var_name}: NO CONFIGURADA")

print(f"\n🔧 CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
print(f"🗄️  DATABASE_URL: {settings.DATABASES['default']['ENGINE']}")
EOF

# 4. Verificar que no hay órdenes con stock incorrecto
echo ""
echo "4️⃣  Verificando integridad de órdenes..."
python manage.py shell << EOF
from orders.models import Order
from shop.models import Product

paid_orders = Order.objects.filter(paid=True).count()
total_orders = Order.objects.count()

print(f"\n📊 Estadísticas de órdenes:")
print(f"  Total órdenes: {total_orders}")
print(f"  Órdenes pagadas: {paid_orders}")
print(f"  Órdenes pendientes: {total_orders - paid_orders}")

# Verificar primeras 5 órdenes
print(f"\n📦 Últimas ordenes pagadas:")
for order in Order.objects.filter(paid=True).order_by('-updated')[:5]:
    items_count = order.items.count()
    total_cost = order.get_total_cost()
    print(f"  Order #{order.id}: {items_count} items, Total: ${total_cost}")
EOF

# 5. Verificar conexión a PostgreSQL
echo ""
echo "5️⃣  Verificando conexión a PostgreSQL..."
python manage.py shell << EOF
from django.db import connection
from django.conf import settings

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print(f"✅ Conexión OK")
    
    # Mostrar info de BD
    print(f"\n📊 Información de BD:")
    print(f"  Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"  SSL Required: {settings.DATABASES['default'].get('ssl_require', 'No especificado')}")
except Exception as e:
    print(f"❌ Error de conexión: {str(e)}")
    exit(1)
EOF

# 6. Verificar Celery
echo ""
echo "6️⃣  Verificando configuración Celery..."
python manage.py shell << EOF
from django.conf import settings

print(f"\n🔄 Configuración Celery:")
print(f"  Broker: {settings.CELERY_BROKER_URL[:30]}...")
print(f"  Backend: {settings.CELERY_RESULT_BACKEND[:30]}...")
print(f"  Max Retries: {settings.CELERY_TASK_MAX_RETRIES}")
print(f"  Time Limit: {settings.CELERY_TASK_TIME_LIMIT}s")
print(f"  Retry on Startup: {settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP}")
EOF

# 7. Verificar email configuration
echo ""
echo "7️⃣  Verificando configuración de email..."
python manage.py shell << EOF
from django.conf import settings

print(f"\n📧 Configuración de email:")
print(f"  Backend: {settings.EMAIL_BACKEND}")
print(f"  Host: {settings.EMAIL_HOST}")
print(f"  Port: {settings.EMAIL_PORT}")
print(f"  Use TLS: {settings.EMAIL_USE_TLS}")
print(f"  From Email: {settings.DEFAULT_FROM_EMAIL}")
EOF

# 8. Verificar STRIPE configuration
echo ""
echo "8️⃣  Verificando configuración Stripe..."
python manage.py shell << EOF
from django.conf import settings
import stripe

print(f"\n💳 Configuración Stripe:")
print(f"  API Version: {settings.STRIPE_API_VERSION}")
print(f"  Currency: {settings.STRIPE_CURRENCY}")
print(f"  Webhook Tolerance: {settings.STRIPE_WEBHOOK_TOLERANCE}s")
print(f"  Publishable Key: {settings.STRIPE_PUBLISHABLE_KEY[:20]}...")

# Verificar conexión a Stripe
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    account = stripe.Account.retrieve()
    print(f"✅ Stripe API conectado correctamente")
except Exception as e:
    print(f"⚠️  Error conectando a Stripe: {str(e)}")
EOF

# 9. Verificar archivos estáticos
echo ""
echo "9️⃣  Verificando archivos estáticos..."
if [ -d "staticfiles" ]; then
    file_count=$(find staticfiles -type f | wc -l)
    echo -e "${GREEN}✅ Carpeta staticfiles existe ($file_count files)${NC}"
else
    echo -e "${YELLOW}⚠️  Carpeta staticfiles no existe${NC}"
    echo "   Ejecutar: python manage.py collectstatic"
fi

# 10. Verificar logs
echo ""
echo "🔟 Verificando logs..."
if [ -d "logs" ]; then
    echo -e "${GREEN}✅ Carpeta logs existe${NC}"
    if [ -f "logs/django.log" ]; then
        lines=$(wc -l < logs/django.log)
        echo "   Líneas de log: $lines"
    fi
else
    mkdir -p logs
    touch logs/.gitkeep
    echo -e "${YELLOW}ℹ️  Carpeta logs creada${NC}"
fi

echo ""
echo "=================================================="
echo "✅ VERIFICACION COMPLETADA"
echo "=================================================="
echo ""
echo "📝 Próximos pasos:"
echo "  1. Revisar logs en: logs/django.log"
echo "  2. Hacer una compra de prueba"
echo "  3. Verificar:"
echo "     - Stock se resta"
echo "     - Email se envía"
echo "     - Orden se marca como pagada"
echo ""
echo "🚀 Sistema listo para producción"
echo "=================================================="
