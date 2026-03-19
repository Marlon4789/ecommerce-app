<div align="center">

# ☕ Kaboha Coffee

### E-Commerce de Productos de Café de Alta Gama

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.3-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=flat-square&logo=stripe&logoColor=white)](https://stripe.com)
[![Deploy](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)](https://railway.app)

**[🌐 Ver aplicación en vivo →](https://ecommerce-app-production-4a70.up.railway.app)**

</div>

---

## 📖 ¿Qué es Kaboha Coffee?

**Kaboha Coffee** es una tienda en línea completa para la venta de café de especialidad. Construida con tecnologías de nivel profesional, cuenta con una interfaz **dark luxury** elegante, gestión inteligente de inventario, pagos seguros con Stripe y notificaciones automáticas por correo al cliente.

> Proyecto Final — Tecnólogo ADSO · SENA

---

## ✨ Funcionalidades principales

| Funcionalidad | Descripción |
|---|---|
| 🛍️ **Catálogo inteligente** | Muestra solo productos con stock disponible. Oculta automáticamente los agotados |
| ⚠️ **Stock dinámico** | Indica "Pocas unidades" cuando el inventario es bajo, y oculta el producto cuando llega a cero |
| 🛒 **Carrito de compras** | Agrega, actualiza o elimina productos. Persiste entre sesiones |
| 💳 **Pagos con Stripe** | Checkout seguro y certificado PCI-DSS. La app nunca toca datos de tarjetas |
| 🔔 **Webhooks de Stripe** | Confirma pagos en tiempo real y actualiza órdenes automáticamente |
| 📧 **Email automático** | Envía confirmación de compra al cliente de forma asíncrona (Celery + Gmail) |
| 🔧 **Panel de administración** | Gestión completa de productos, stock, órdenes y pagos desde Django Admin |
| 🌙 **Dark Luxury UI** | Interfaz elegante con Bootstrap 5, CSS y JavaScript personalizado |

---

## 🖥️ Vista previa

```
Catálogo → Detalle de producto → Carrito → Stripe Checkout → Confirmación → Email al cliente
```

- **Stock suficiente** → badge verde `Disponible`
- **Stock bajo** → badge amarillo `Pocas unidades disponibles`
- **Sin stock** → producto oculto del frontend automáticamente

---

## 🏗️ Arquitectura del proyecto

```
ecommerce-app/
│
├── core/           # Configuración central de Django (settings, URLs globales)
├── shop/           # Lógica principal de la tienda y vistas
├── products/       # Catálogo de productos, modelos e inventario
├── cart/           # Carrito de compras con lógica de sesión
├── orders/         # Gestión de órdenes y estados de compra
├── payment/        # Integración con Stripe y manejo de webhooks
│
├── static/         # Archivos estáticos de desarrollo (CSS, JS, imágenes)
├── staticfiles/    # Archivos estáticos recopilados para producción
├── media/          # Imágenes de productos subidas
│
├── manage.py
├── requirements.txt
├── Procfile        # Configuración de procesos para Railway
└── runtime.txt     # Versión de Python para Railway
```

---

## ⚙️ Flujo de una compra

```
1. Usuario agrega productos al carrito
2. Hace clic en "Ir a pagar"
3. Django redirige a Stripe Checkout (pago externo y seguro)
4. Stripe procesa el pago y envía un webhook al servidor
5. Django valida la firma del webhook y actualiza la orden → estado "Pagado"
6. El stock de los productos comprados se descuenta automáticamente
7. Celery encola la tarea de envío de email (asíncrono, no bloquea al usuario)
8. Gmail SMTP envía el correo de confirmación al cliente
```

---

## 🛠️ Stack tecnológico

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | 3.12 | Lenguaje principal |
| **Django** | 5.1.4 | Framework web, ORM, admin |
| **PostgreSQL** | Latest | Base de datos en producción |
| **Celery** | 5.4.0 | Tareas asíncronas (emails) |
| **Redis** | 7.3.0 | Broker de mensajes para Celery |
| **Stripe** | 11.4.1 | Pasarela de pagos y webhooks |
| **Gunicorn** | 25.1.0 | Servidor WSGI de producción |
| **Whitenoise** | 6.12.0 | Archivos estáticos en producción |
| **python-decouple** | 3.8 | Variables de entorno |

### Frontend
| Tecnología | Uso |
|---|---|
| **Bootstrap 5** | Grid responsivo y componentes base |
| **CSS3 personalizado** | Tema dark luxury con paleta dorada |
| **JavaScript** | Lógica del carrito e interacciones |
| **Google Gemini IA** | Imágenes de productos generadas con IA |

### Infraestructura
| Servicio | Uso |
|---|---|
| **Railway** | Despliegue en la nube (app + DB + Redis) |
| **GitHub** | Control de versiones y CI/CD |
| **Gmail SMTP** | Envío de correos de confirmación |

---

## 🚀 Cómo correr el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/Marlon4789/Ecommerce-App.git
cd Ecommerce-App
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=tu_secret_key_de_django
DEBUG=True

DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/kaboha_coffee

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_de_gmail

REDIS_URL=redis://localhost:6379/0
```

> 💡 Necesitas tener PostgreSQL y Redis corriendo localmente, o puedes usar las URLs de Railway si ya tienes el proyecto desplegado.

### 5. Aplicar migraciones y crear superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Levantar el servidor de desarrollo

```bash
# Terminal 1 — servidor Django
python manage.py runserver

# Terminal 2 — worker de Celery (para emails)
celery -A core worker --loglevel=info

# Terminal 3 — (opcional) monitoreo de tareas Celery
celery -A core flower
```

### 7. Abrir en el navegador

```
Tienda:           http://localhost:8000
Panel de admin:   http://localhost:8000/admin
Flower (Celery):  http://localhost:5555
```

---

## 🌐 Despliegue en Railway

El proyecto está configurado para despliegue automático en [Railway](https://railway.app).

**Servicios en Railway:**
- App Django (Gunicorn)
- PostgreSQL (base de datos)
- Redis (broker de Celery)

El archivo `Procfile` define los procesos:

```
web: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A core worker --loglevel=info
```

Cada `push` a la rama `main` activa un nuevo despliegue automáticamente.

---

## 🔧 Panel de administración

Accede en `/admin` con tu superusuario para:

- 📦 **Productos** — crear, editar, subir imágenes y actualizar stock
- 📋 **Órdenes** — ver historial completo de compras y estados
- 💳 **Pagos** — revisar pagos procesados con Stripe
- 👥 **Usuarios** — gestión de cuentas

---

## 📁 Variables de entorno requeridas

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `DATABASE_URL` | URL de conexión a PostgreSQL |
| `STRIPE_PUBLIC_KEY` | Clave pública de Stripe |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe |
| `STRIPE_WEBHOOK_SECRET` | Secreto para validar webhooks de Stripe |
| `EMAIL_HOST_USER` | Correo Gmail para envío de notificaciones |
| `EMAIL_HOST_PASSWORD` | App Password de Gmail |
| `REDIS_URL` | URL de conexión a Redis |

> ⚠️ Nunca subas el archivo `.env` al repositorio. Está incluido en `.gitignore`.

---

## 📦 Dependencias principales

```
Django==5.1.4
celery==5.4.0
redis==7.3.0
stripe==11.4.1
psycopg2-binary==2.9.11
gunicorn==25.1.0
whitenoise==6.12.0
python-decouple==3.8
Pillow==11.0.0
djangorestframework==3.16.1
```

Ver lista completa en [`requirements.txt`](./requirements.txt).

---

## 🤝 Contribuir

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Haz tus cambios y un commit: `git commit -m "feat: agrega nueva funcionalidad"`
4. Sube la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-Marlon4789-181717?style=flat-square&logo=github)](https://github.com/Marlon4789/Ecommerce-App)
[![Railway](https://img.shields.io/badge/Live-Railway-0B0D0E?style=flat-square&logo=railway)](https://ecommerce-app-production-4a70.up.railway.app)



</div>