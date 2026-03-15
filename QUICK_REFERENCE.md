# 📌 Quick Reference - Comandos & Endpoints

## 🚀 Comandos Django

```bash
# Desarrollo
python manage.py runserver                          # Iniciar servidor
python manage.py runserver 0.0.0.0:8000            # En la red
python manage.py shell                             # Consola Python

# Base de datos
python manage.py makemigrations                    # Preparar migraciones
python manage.py makemigrations catalog            # Específica
python manage.py migrate                           # Aplicar migraciones
python manage.py migrate --fake                    # Sin aplicar SQL
python manage.py dbshell                           # Consola SQL

# Admin
python manage.py createsuperuser                   # Crear admin
python manage.py changepassword username           # Cambiar contraseña

# Archivos
python manage.py collectstatic --noinput           # Recopilar static
python manage.py clean                             # Limpiar __pycache__

# Testing
python manage.py test                              # Todas las pruebas
python manage.py test catalog                      # App específica
python manage.py test catalog.tests.TestClass      # Clase específica

# Otros
python manage.py check                             # Verificar proyecto
python manage.py show_urls                         # Ver rutas
python manage.py graph_models -a -o model_graph.png
```

---

## 🌐 Endpoints API

### Búsqueda y Listado

```
GET  /api/products/
     Retorna: Lista paginada de productos
     Query params: q, category, min_price, max_price, on_sale, ordering, page
     
GET  /api/products/{id}/
     Retorna: Detalle completo de un producto
```

### Endpoints Especiales

```
GET  /api/products/categories/
     Retorna: Lista de categorías disponibles
     Formato: [{"id": 1, "name": "Café", "slug": "cafe"}, ...]

GET  /api/products/price_range/
     Retorna: Rango min-max de precios
     Formato: {"min_price": 10.00, "max_price": 50.00}

GET  /api/products/on_sale/
     Retorna: Productos en oferta (máx 12)
     Formato: Igual a /api/products/ pero solo ofertas

GET  /api/products/{id}/recommended/
     Retorna: 6 productos recomendados para el ID
     Formato: Lista de productos
```

---

## 📍 Rutas Frontend

```
GET  /productos/
     Página de búsqueda con filtros
     Template: catalog/product_search.html

GET  /producto/<slug>/
     Detalle del producto con carrusel
     Template: catalog/product_detail.html
     Ejemplo: /producto/cafe-espresso-premium/
```

---

## 🔍 Ejemplos de Búsqueda API

```bash
# Todos los productos
curl http://localhost:8000/api/products/

# Búsqueda por texto
curl "http://localhost:8000/api/products/?q=espresso"

# Filtro por categoría (ID 1)
curl "http://localhost:8000/api/products/?category=1"

# Rango de precio
curl "http://localhost:8000/api/products/?min_price=20&max_price=50"

# Solo ofertas
curl "http://localhost:8000/api/products/?on_sale=true"

# Ordenar más caro primero
curl "http://localhost:8000/api/products/?ordering=-price"

# Página 2
curl "http://localhost:8000/api/products/?page=2"

# Combinar todos
curl "http://localhost:8000/api/products/?q=cafe&category=1&min_price=15&max_price=45&on_sale=false&ordering=name&page=1"

# Pretty print
curl "http://localhost:8000/api/products/?q=cafe" | python -m json.tool
```

---

## 🎨 JavaScript / Alpine.js

```javascript
// En Alpine Data
x-data="searchFilters()"

// Métodos disponibles
.fetchProducts()          // Llamar API
.clearFilters()           // Limpiar búsqueda
.goToPage(n)              // Ir a página
.handleCategoryChange()   // Cambiar categoría
.loadCategories()         // Cargar categorías

// En template
x-model="filters.q"            // Binding de búsqueda
@input.debounce="fetchProducts()  // Ejecutar con delay
x-text="hijos"                 // Mostrar contenido
x-for="(item, index) in items" // Iterar
x-if="condition"               // Condicional
:src="image.image"             // Propiedades dinámicas
@click="method()"              // Click handler
```

---

## 📊 Modelos Django

### ProductImage
```python
ProductImage.objects.create(
    product=product_obj,
    image='ruta/imagen.jpg',
    alt_text='Descripción',
    order=0,
    is_primary=True
)

# Queries útiles
ProductImage.objects.filter(is_primary=True)
ProductImage.objects.filter(product_id=1).order_by('order')
ProductImage.objects.filter(product__category_id=1)
```

### Product
```python
# Propriedad calculada
product.current_price  # Retorna precio normal o promocional

# Queries útiles
Product.objects.filter(availability=True)
Product.objects.filter(on_sale=True)
Product.objects.prefetch_related('images')
Product.objects.select_related('category')
```

---

## 🗄️ Queryset Útiles

```python
# En Django Shell: python manage.py shell

from catalog.models import ProductImage
from shop.models import Product, Category

# Contar
ProductImage.objects.count()
Product.objects.filter(on_sale=True).count()

# Filtrar
Product.objects.filter(price__gt=20)  # Mayor que
Product.objects.filter(price__lt=30)  # Menor que
Product.objects.filter(price__range=[10, 50])
Product.objects.filter(name__icontains='cafe')

# Ordenar
Product.objects.order_by('price')
Product.objects.order_by('-created_date')

# Primero/Último
Product.objects.first()
Product.objects.last()

# Valores
Product.objects.values('name', 'price')
Product.objects.values_list('id', 'name')

# Aggregate
from django.db.models import Avg, Sum
Product.objects.aggregate(Avg('price'))

# Excluir
Product.objects.exclude(id=1)

# Combinaciones
Product.objects.filter(
    on_sale=True
).prefetch_related('images').order_by('-created_date')[:10]
```

---

## 🎯 Admin Django

```
URL: http://localhost:8000/admin/

Catálogo → Imágenes de Productos
  ├─ Agregar imagen
  ├─ Filtrar por producto/categoría
  └─ Buscar por alt_text

Shop → Productos
  ├─ Ver/editar productos
  └─ Relacionados con imágenes

Shop → Categorías
  └─ Gestionar categorías
```

---

## 📁 Estructura de Carpetas

```
Ecommerce-App/
├── catalog/                    # App nuevo
│   ├── migrations/
│   ├── templates/catalog/
│   │   ├── product_search.html     # Búsqueda
│   │   └── product_detail.html     # Detalle
│   ├── models.py               # ProductImage
│   ├── serializers.py          # DRF
│   ├── views.py                # ViewSets
│   ├── admin.py                # Admin
│   └── urls.py                 # Rutas
│
├── shop/
│   ├── templates/layouts/
│   │   └── base_tailwind.html      # Base mejorada
│   ├── models.py               # Product, Category
│   └── ...
│
├── core/
│   ├── settings.py             # INSTALLED_APPS, REST_FRAMEWORK
│   ├── urls.py                 # URLs del proyecto
│   └── ...
│
├── requirements.txt            # Dependencias
├── manage.py
├── IMPROVEMENTS.md             # Este cambio
├── USAGE_GUIDE.md             # Cómo usar
└── ARCHITECTURE.md            # Documentación técnica
```

---

## 🐛 Errores Comunes & Soluciones

```
ERROR: "No module named 'rest_framework'"
SOLUCIÓN: pip install djangorestframework

ERROR: ModuleNotFoundError: No module named 'catalog'
SOLUCIÓN: python manage.py migrate

ERROR: TemplateDoesNotExist
SOLUCIÓN: Verificar ruta en TEMPLATES['DIRS'] en settings

ERROR: 404 en /api/products/
SOLUCIÓN: Verificar core/urls.py include('catalog.urls')

ERROR: CORS error en navegador
SOLUCIÓN: Agregar dominio a CORS_ALLOWED_ORIGINS

ERROR: Imágenes no cargan (404)
SOLUCIÓN: python manage.py collectstatic --noinput
```

---

## 🧪 Testing

```bash
# Test unitario
python manage.py test catalog.tests

# Con coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# API test
python -m pytest catalog/tests/test_api.py -v
```

---

## 📱 URLs Útiles en Dev

```
Admin:              http://localhost:8000/admin/
Productos:          http://localhost:8000/productos/
Detalle Producto:   http://localhost:8000/producto/cafe-premium/
API Productos:      http://localhost:8000/api/products/
API Categorías:     http://localhost:8000/api/products/categories/
API Recomendados:   http://localhost:8000/api/products/1/recommended/
```

---

## 🔐 Configuración Importante

```python
# settings.py

# CORS (para requests desde frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# Media files (para imágenes)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

---

## 📊 Variables de Contexto (Templates)

```django
{% block content %}
    <!-- En product_search.html -->
    {{ cart }}              <!-- Carrito actual -->
    
    <!-- En product_detail.html -->
    {{ product }}           <!-- Objeto producto
    {{ images_json }}       <!-- Imágenes en JSON
    {{ images }}            <!-- QuerySet imágenes
    {{ discount_percentage }} <!-- % descuento
{% endblock %}
```

---

## 💾 Backup & Restore

```bash
# Backup
python manage.py dumpdata > backup.json
cp -r media/ media_backup/

# Restore
python manage.py loaddata backup.json
cp -r media_backup/ media/
```

---

## 🚀 Deploy Checklist

```
☐ python manage.py check --deploy
☐ python manage.py collectstatic --noinput
☐ Verificar .env variables
☐ python manage.py migrate
☐ Tests pasando
☐ DEBUG = False
☐ ALLOWED_HOSTS correcto
☐ CORS_ALLOWED_ORIGINS actualizado
☐ Media folder con permisos 755
☐ Static folder compilado
☐ Backup de BD realizado
```

---

**Última actualización: 14 Marzo 2026** ✨
