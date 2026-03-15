# Guía de Uso - Nuevas Funcionalidades

## 🚀 Comenzar Rápido

### 1. Preparar el Proyecto
```bash
cd Ecommerce-App

# Activar ambiente virtual
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (si no existe)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

### 2. Acceder a URLs

**Búsqueda de productos:**
```
http://localhost:8000/productos/
```

**Detalle de producto (ejemplo):**
```
http://localhost:8000/producto/cafe-espresso-premium/
```

**API REST:**
```
http://localhost:8000/api/products/
```

---

## 📸 Agregar Imágenes a Productos

### Opción 1: Admin Django (Recomendado)

1. Ir a: `http://localhost:8000/admin/`
2. Autenticarse con superusuario
3. Ir a "Catálogo" → "Imágenes de Productos"
4. Click en "Add Image"
5. Seleccionar producto
6. Subir imagen
7. Establecer orden (0 para primera)
8. Marcar "Es principal" para imagen destacada
9. **Guardar**

### Opción 2: Django Shell
```bash
python manage.py shell

from catalog.models import ProductImage
from shop.models import Product

product = Product.objects.first()

# Crear imagen
image = ProductImage.objects.create(
    product=product,
    image='products/2024/03/mi-imagen.jpg',  # Path relativo a media/
    alt_text='Descripción del producto',
    order=0,
    is_primary=True
)
```

### Opción 3: Upload programático
```python
from catalog.models import ProductImage
from shop.models import Product
from django.core.files.images import ImageFile

product = Product.objects.get(id=1)
image_path = open('path/to/image.jpg', 'rb')

ProductImage.objects.create(
    product=product,
    image=ImageFile(image_path),
    alt_text='Mi producto',
    order=0,
    is_primary=True
)
```

---

## 🔍 Usar la Búsqueda

### Desde el Frontend
1. Ir a `/productos/`
2. Escribir en el buscador (en tiempo real)
3. Usar filtros:
   - **Categoría:** Select dropdowns
   - **Rango de Precio:** Inputs numéricos
   - **Solo Ofertas:** Checkbox
4. Ordenar resultados
5. Navegar por páginas

### Desde la API
```bash
# Búsqueda simple
curl "http://localhost:8000/api/products/?q=cafe"

# Filtro por categoría (cambiar ID según necesidad)
curl "http://localhost:8000/api/products/?category=1"

# Rango de precio
curl "http://localhost:8000/api/products/?min_price=10&max_price=50"

# Solo ofertas
curl "http://localhost:8000/api/products/?on_sale=true"

# Ordenar por precio
curl "http://localhost:8000/api/products/?ordering=price"

# Combinar múltiples filtros
curl "http://localhost:8000/api/products/?q=cafe&category=1&min_price=10&max_price=50&page=1"

# Recomendados
curl "http://localhost:8000/api/products/1/recommended/"

# Categorías disponibles
curl "http://localhost:8000/api/products/categories/"

# Rango de precios
curl "http://localhost:8000/api/products/price_range/"
```

---

## 🖼️ Vista de Detalle

### Características del Carrusel
- **Navegación:** Flechas en los lados
- **Thumbnails:** Click en thumbnails para cambiar imagen
- **Zoom:** Click en icono de lupa (arriba-derecha)
- **Contador:** Muestra imagen actual y total
- **Mobile:** Swipe (preparado para implementar)

### Productos Recomendados
Se cargan automáticamente basados en:
- Misma categoría
- Precio similar (±20%)
- Excluyendo el producto actual

---

## 🎨 Personalizar Estilos

### Cambiar Colores de Marca

Editar `/shop/templates/layouts/base_tailwind.html`:

```html
<style>
    .coffee-brown {
        background-color: #6f4e37;  /* Cambiar este color */
    }
    
    .coffee-gold {
        color: #d4a574;  /* Cambiar este color */
    }
</style>
```

### Tailwind CSS Personalizado
Los estilos de Tailwind se cargan desde CDN. Para producción, compilar localmente:

```bash
npm install -D tailwindcss
npx tailwindcss init
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

---

## 📊 Consultas Útiles (Django Shell)

```bash
python manage.py shell
```

```python
from catalog.models import ProductImage
from shop.models import Product

# Contar imágenes
ProductImage.objects.count()

# Imágenes por producto
Product.objects.first().images.count()

# Productos sin imágenes
Product.objects.filter(images__isnull=True)

# Imagen principal de cada producto
ProductImage.objects.filter(is_primary=True)

# Productos en oferta
Product.objects.filter(on_sale=True)

# Precio más alto
Product.objects.order_by('-price').first()

# Por categoría
from shop.models import Category
cat = Category.objects.first()
cat.products.all()
```

---

## 🚨 Solucionar Problemas

### 1. La búsqueda no funciona
```bash
# Check API
curl http://localhost:8000/api/products/

# Revisar logs
python manage.py runserver --verbosity=3

# Verificar BD
python manage.py dbshell
# SELECT * FROM shop_product;
```

### 2. Las imágenes no se ven
```bash
# Ejecutar
python manage.py collectstatic --noinput

# Asegurar permisos
chmod -R 777 media/

# Verificar URL en admin
/admin/catalog/productimage/
```

### 3. Error "no module named catalog"
```bash
# Reinstalar
python manage.py migrate --run-syncdb

# Verificar installed apps
python -c "import django; django.setup(); from django.conf import settings; print(settings.INSTALLED_APPS)"
```

### 4. Productos sin imágenes no se ven
- Verificar campo `image` en modelo Product
- Es opcional, usará fallback si está vacío

---

## 🔄 Mantener Datos

### Backup de imágenes
```bash
# Comprimir media/
tar -czf media_backup.tar.gz media/

# Restaurar
tar -xzf media_backup.tar.gz
```

### Cleanup de imágenes sin usar
```python
# Django Shell
from catalog.models import ProductImage
from django.db.models import Q

# Encontrar imágenes de productos eliminados
ProductImage.objects.filter(product__isnull=True).delete()
```

---

## 📈 Monitoreo

### API Performance
```python
# Django Shell - Timing de queries
from django.test.utils import override_settings
from django.db import connection, reset_queries

@override_settings(DEBUG=True)
def test_performance():
    from catalog.views import ProductViewSet
    viewset = ProductViewSet()
    products = viewset.get_queryset()
    
    print(f"Queries: {len(connection.queries)}")
    for query in connection.queries:
        print(query['sql'][:100], f"- {query['time']}s")
```

---

## 🚀 Deploy a Producción

### En Railway:
```bash
# .env variables necesarias
DEBUG=False
ALLOWED_HOSTS=tu-app.railway.app
STRIPE_PUBLISHABLE_KEY=pk_live_...
# ... resto de variables

# Deploy
git push
```

### Verificaciones pre-deploy:
```bash
# Check
python manage.py check --deploy

# Collect static
python manage.py collectstatic --noinput

# Test
python manage.py test

# Run migrations
python manage.py migrate
```

---

## 💡 Tips & Tricks

1. **Performance:** Usar `?page_size=24` para cargar más items
2. **API:** Respuestas JSON limpias, perfectas para mobile apps
3. **Caché:** Implementar Redis para optimizar búsquedas
4. **Analytics:** Rastrear clicks en `/api/products/{id}/`
5. **SEO:** URLs amigables con slugs

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación en `IMPROVEMENTS.md`
2. Consultar logs: `python manage.py runserver --verbosity=2`
3. Debugger: Agregar `breakpoint()` en views.py

---

**¡Listo para usar! 🎉**
