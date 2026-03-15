# Guía de Solución de Bugs - Ecommerce App

## Problemas Solucionados

### 1. ❌ BUG: Stock No Se Resta Después de Compra
**Problema:** Al completar una compra, el stock del producto no se actualizaba.

**Causa:** El webhook de Stripe estaba usando `session.payment_intent` en lugar de `session.id`, lo que causaba que la orden nunca se marcara como pagada correctamente.

**Solución Implementada:**
- ✅ Cambiar `order.stripe_id = session.payment_intent` por `order.stripe_id = session.id`
- ✅ Agregar logging detallado en el webhook
- ✅ Mejorar el signal de actualización de stock con validaciones

**Archivo:** `payment/webhooks.py` línea 47

```python
# ❌ ANTES (INCORRECTO)
order.stripe_id = session.payment_intent  # payment_intent es None

# ✅ DESPUÉS (CORRECTO)
order.stripe_id = session.id
```

---

### 2. ❌ BUG: Email No Se Envía
**Problema:** Los clientes no reciben confirmación de compra por email.

**Causa:** 
- La tarea Celery podría fallar silenciosamente sin reintentos
- No hay fallback si Redis no está disponible
- Sin manejo de errores ni logging

**Soluciones Implementadas:**
- ✅ Mejorar `orders/tasks.py` con Try/Except y reintentos automáticos
- ✅ Crear servicio de email con fallback sincrónico `orders/email_service.py`
- ✅ Agregar logging detallado
- ✅ Configurar reintentos exponenciales en Celery

**Archivos:** 
- `orders/tasks.py` - Tareas Celery mejoradas
- `orders/email_service.py` - Nuevo servicio con fallback

```python
# Ahora con reintentos automáticos
@shared_task(bind=True, max_retries=3)
def order_created(self, order_id):
    # ... con try/except y logging
```

---

### 3. ❌ ERROR: PostgreSQL en Railway
**Error:** "invalid length of startup packet" y corrupción de BD

**Soluciones Implementadas:**
- ✅ Mejorar configuración de SSL para PostgreSQL
- ✅ Agregar middleware para cerrar conexiones correctamente
- ✅ Configurar timeouts de conexión
- ✅ Agregar reintentos de conexión en Celery

**Archivos Afectados:**
- `core/settings.py` - Configuración de BD mejorada
- `core/middleware.py` - Nuevo middleware para conexiones

---

## Cambios Realizados

### Nueva Estructura de Archivos

```
orders/
├── email_service.py      ✨ NUEVO - Servicio de email con fallback
├── validators.py         ✨ NUEVO - Validadores de stock
├── management/          ✨ NUEVO - Comandos personalizados
│   ├── commands/
│   │   └── fix_stock_issues.py
```

```
core/
├── middleware.py        ✨ NUEVO - Middleware personalizado
└── settings.py         ✏️ MEJORADO
```

---

## Validaciones Añadidas

### Stock Validation
- Validar stock antes de crear orden
- Mostrar mensajes de error claros al usuario
- Usar transacciones para integridad de datos

**Uso en `orders/views.py`:**
```python
# Validar stock antes de crear orden
from orders.validators import validate_cart_stock

validate_cart_stock(cart)  # Lanza StockValidationError si hay problemas
```

---

## Configuración de Email

### Fallback Automático
El sistema intenta enviar asyncrónicamente vía Celery, pero si falla, automáticamente cambia a envío sincrónico:

```python
from orders.email_service import send_order_confirmation_email

send_order_confirmation_email(order_id)
# Intenta Celery → Si falla → Intenta sincrónico
```

---

## Configuración de Celery Mejorada

```python
# core/settings.py
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_TIME_LIMIT = 30 * 60
```

---

## Logging Mejorado

Nuevo sistema de logging que registra:
- Errores de stock
- Intentos de email
- Errores de webhook
- Conexiones a BD

**Ubicación:** `logs/django.log`

**Configuración en:** `core/settings.py`

---

## Para Railway

### Verificación Antes de Deploy

```bash
# 1. Verificar variables de entorno
python manage.py shell
>>> import os
>>> print(os.environ.get('REDIS_URL'))
>>> print(os.environ.get('DATABASE_URL'))

# 2. Ejecutar migraciones
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Recopilar archivos estáticos
python manage.py collectstatic

# 5. Testear tarea Celery (opcional)
celery -A core worker -l info
```

### Variables de Entorno Necesarias

```env
SECRET_KEY=xxxx
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
EMAIL_HOST_USER=xxxx
EMAIL_HOST_PASSWORD=xxxx
STRIPE_PUBLISHABLE_KEY=pk_xxx
STRIPE_SECRET_KEY=sk_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

---

## Testing de Cambios

### 1. Test de Stock
```bash
python manage.py shell
>>> from shop.models import Product
>>> p = Product.objects.first()
>>> p.stock = 10
>>> p.save()
# Realizar compra en el navegador
>>> p.refresh_from_db()
>>> print(p.stock)  # Debería ser 9
```

### 2. Test de Email
```bash
python manage.py shell
>>> from orders.models import Order
>>> from orders.email_service import send_order_confirmation_sync
>>> order = Order.objects.first()
>>> send_order_confirmation_sync(order.id)
```

### 3. Test de Webhook
```bash
# Usar Stripe CLI para simular webhook
stripe listen --forward-to localhost:8000/payment/stripe-webhook/
stripe trigger payment_intent.succeeded
```

---

## Checklist de Verificación

- [ ] Stock se resta correctamente después de pago
- [ ] Emails se envían a clientes
- [ ] Sistema usa Redis/Celery cuando está disponible
- [ ] Sistema usa fallback sincrónico cuando Redis no está disponible
- [ ] Logging regis todos los errores importantes
- [ ] PostgreSQL en Railway funciona sin errores
- [ ] Webhook de Stripe actualiza ordenes correctamente
- [ ] Validación de stock antes de pago
- [ ] Mensajes de error claros para usuario

---

## Comandos Útiles

```bash
# Ver logs
tail -f logs/django.log

# Ejecutar Celery worker
celery -A core worker -l info

# Ejecutar Celery beat (para tareas programadas)
celery -A core beat -l info

# Validar configuración
python manage.py check

# Ejecutar tests
python manage.py test

# Comando personalizado para reparar stock
python manage.py fix_stock_issues --dry-run
```

---

## Notas Importantes

1. **Redis es Opcional:** Si Redis no está disponible, el sistema funcionará en modo fallback con envío sincrónico de emails.

2. **Transactions:** Se agregó `transaction.atomic()` en la creación de ordenes para asegurar integridad.

3. **Logging:** Todos los procesos críticos se registran en `logs/django.log`.

4. **SSL en PostgreSQL:** Configurado para Railway automáticamente basado en `DEBUG`.

5. **CSRF:** Configurado para aceptar requests de Railway sin problemas.

---

## Próximos Pasos Opcionales

1. Agregar autenticación de usuarios para historial de pedidos
2. Crear notificación de bajo stock para administradores
3. Implementar webhook de reembolsos de Stripe
4. Agregar panel de administración mejorado para órdenes
5. Implementar descuentos/cupones
