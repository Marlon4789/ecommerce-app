#!/bin/bash
# Comandos Útiles Post-Fixes
# Use estos comandos para testing, debugging y deployment

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║          COMANDOS ÚTILES - ECOMMERCE APP (Post-Fixes)            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}1️⃣  VERIFICACIÓN RÁPIDA${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Validar Django:${NC}"
echo "$ python manage.py check"

echo -e "\n${YELLOW}Ver versión de packages:${NC}"
echo "$ python manage.py shell -c \"import django; print(f'Django: {django.VERSION}')\""

echo -e "\n${YELLOW}Verificar configuración Stripe:${NC}"
echo "$ python manage.py shell"
echo ">>> from django.conf import settings"
echo ">>> print(settings.STRIPE_CURRENCY)"
echo ">>> exit()"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}2️⃣  TESTING DE FUNCIONALIDAD${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Test de Stock:${NC}"
echo "$ python manage.py shell << 'EOF'"
echo "from shop.models import Product"
echo "p = Product.objects.first()"
echo "print(f'Stock actual: {p.stock}')"
echo "p.stock = 10"
echo "p.save()"
echo "EOF"

echo -e "\n${YELLOW}Test de Email (Sincrónico):${NC}"
echo "$ python manage.py shell << 'EOF'"
echo "from orders.models import Order"
echo "from orders.email_service import send_order_confirmation_sync"
echo "order = Order.objects.first()"
echo "result = send_order_confirmation_sync(order.id)"
echo "print(f'Email enviado: {result}')"
echo "EOF"

echo -e "\n${YELLOW}Test de Validador de Stock:${NC}"
echo "$ python manage.py shell << 'EOF'"
echo "from orders.validators import check_product_availability"
echo "result = check_product_availability(product_id=1, quantity=5)"
echo "print(result)"
echo "EOF"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}3️⃣  CELERY & REDIS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Iniciar Celery worker (desarrollo):${NC}"
echo "$ celery -A core worker -l info"

echo -e "\n${YELLOW}Iniciar Celery beat (scheduled tasks):${NC}"
echo "$ celery -A core beat -l info"

echo -e "\n${YELLOW}Monitorear Celery (en otra terminal):${NC}"
echo "$ celery -A core events"

echo -e "\n${YELLOW}Ver Redis connection:${NC}"
echo "$ python manage.py shell"
echo ">>> import redis"
echo ">>> r = redis.Redis.from_url('redis://localhost:6379/0')"
echo ">>> r.ping()"
echo "True"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}4️⃣  LOGGING & DEBUGGING${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Ver logs en tiempo real:${NC}"
echo "$ tail -f logs/django.log"

echo -e "\n${YELLOW}Buscar errores en logs:${NC}"
echo "$ grep ERROR logs/django.log"

echo -e "\n${YELLOW}Ver últimas 50 líneas de logs:${NC}"
echo "$ tail -50 logs/django.log"

echo -e "\n${YELLOW}Estadísticas de logs:${NC}"
echo "$ wc -l logs/django.log"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}5️⃣  STRIPE TESTING${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Usar Stripe CLI para testear webhook:${NC}"
echo "$ stripe listen --forward-to localhost:8000/payment/stripe-webhook/"

echo -e "\n${YELLOW}Simular payment_intent.succeeded event:${NC}"
echo "$ stripe trigger payment_intent.succeeded"

echo -e "\n${YELLOW}Ver eventos en tiempo real:${NC}"
echo "$ stripe events list"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}6️⃣  DATABASE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Hacer migraciones:${NC}"
echo "$ python manage.py makemigrations"
echo "$ python manage.py migrate"

echo -e "\n${YELLOW}Ver estado de migraciones:${NC}"
echo "$ python manage.py showmigrations"

echo -e "\n${YELLOW}Conexión a PostgreSQL (si en producción):${NC}"
echo "$ psql \$DATABASE_URL"

echo -e "\n${YELLOW}Estadísticas de BD (Python shell):${NC}"
echo "$ python manage.py shell"
echo ">>> from shop.models import Product"
echo ">>> from orders.models import Order"
echo ">>> print(f'Productos: {Product.objects.count()}')"
echo ">>> print(f'Ordenes: {Order.objects.count()}')"
echo ">>> print(f'Ordenes pagadas: {Order.objects.filter(paid=True).count()}')"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}7️⃣  ADMIN & MANTENIMIENTO${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Crear superusuario:${NC}"
echo "$ python manage.py createsuperuser"

echo -e "\n${YELLOW}Cambiar contraseña de usuario:${NC}"
echo "$ python manage.py changepassword username"

echo -e "\n${YELLOW}Limpiar sessions expiradas:${NC}"
echo "$ python manage.py clearsessions"

echo -e "\n${YELLOW}Recopilar archivos estáticos:${NC}"
echo "$ python manage.py collectstatic"

echo -e "\n${YELLOW}Comando personalizado - Reparar stock:${NC}"
echo "$ python manage.py fix_stock_issues --dry-run"
echo "$ python manage.py fix_stock_issues  # Ejecutar fix"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}8️⃣  GIT & DEPLOYMENT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Ver cambios:${NC}"
echo "$ git diff"
echo "$ git status"

echo -e "\n${YELLOW}Commit y push:${NC}"
echo "$ git add ."
echo "$ git commit -m 'fix: stock, email, y PostgreSQL en Railway'"
echo "$ git push origin fix/cart-payment-sendEmail"

echo -e "\n${YELLOW}Ver logs de cambios:${NC}"
echo "$ git log --oneline -10"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}9️⃣  DOCUMENTACIÓN${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Archivos de documentación:${NC}"
echo "• README_FIXES.md - Resumen ejecutivo"
echo "• CAMBIOS_DETALLADOS.md - Análisis línea por línea"
echo "• SOLUCION_BUGS.md - Documentación técnica"
echo "• .env.example - Variables de entorno"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔟 RAILWAY DEPLOYMENT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}En Railway Dashboard - Agregar variables de entorno:${NC}"
echo "SECRET_KEY=xxxx"
echo "DEBUG=False"
echo "DATABASE_URL=postgresql://..."
echo "REDIS_URL=redis://..."
echo "EMAIL_HOST_USER=xxxx"
echo "STRIPE_PUBLISHABLE_KEY=pk_xxx"
echo "STRIPE_SECRET_KEY=sk_xxx"
echo "STRIPE_WEBHOOK_SECRET=whsec_xxx"

echo -e "\n${YELLOW}Ejecutar en Railway console:${NC}"
echo "$ python manage.py migrate"
echo "$ python manage.py collectstatic"

echo -e "\n${YELLOW}Ver logs en Railway:${NC}"
echo "Railway Dashboard → Logs"

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ PARA MÁS AYUDA, VER:${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}\n"
echo "✨ README_FIXES.md - Start here!"
echo "📝 CAMBIOS_DETALLADOS.md - Technical deep dive"
echo "📚 SOLUCION_BUGS.md - Complete reference"
echo "🚀 verify_deployment.sh - Automated verification"
echo -e "\n"
