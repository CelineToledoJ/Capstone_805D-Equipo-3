# Tres en Uno - E-commerce de Cultivos Orgánicos

Plataforma de comercio electrónico para la venta de productos agrícolas orgánicos, desarrollada como proyecto de título.

## Descripción

Tres en Uno es un e-commerce que permite a clientes comprar productos orgánicos frescos directamente del productor. Incluye gestión de inventario, carrito de compras, procesamiento de pedidos y panel de administración.

## Funcionalidades Principales

### Para Clientes
- Registro e inicio de sesión
- Catálogo de productos con filtros por categoría
- Carrito de compras
- Proceso de checkout
- Historial de pedidos
- Recuperación de contraseña por email

### Para Administradores
- CRUD completo de productos y categorías
- Gestión de inventario (stock)
- Visualización de pedidos
- Panel de administración de Django

## Tecnologías

**Backend:**
- Python 3.11
- Django 5.1.3
- PostgreSQL
- Django REST Framework
- Simple JWT

**Frontend:**
- HTML5, CSS3, JavaScript
- Bootstrap 4
- jQuery

**Deployment:**
- Railway (hosting)
- WhiteNoise (archivos estáticos)

## Instalación Local

### Prerrequisitos
```bash
Python 3.11+
PostgreSQL
```

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/tres-en-uno.git
cd tres-en-uno
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear archivo `.env` en la raíz:
```env
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
DATABASE_URL=postgresql://usuario:password@localhost:5432/tresenuno
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app
```

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Recolectar archivos estáticos
```bash
python manage.py collectstatic
```

### 8. Ejecutar servidor
```bash
python manage.py runserver
```

Acceder a: `http://localhost:8000`

## Deployment en Railway

El proyecto está configurado para deployment automático en Railway.

**Variables de entorno requeridas:**
- `SECRET_KEY`
- `DATABASE_URL` (generada automáticamente por Railway)
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `ALLOWED_HOSTS`

## Estructura del Proyecto

```
tres-en-uno/
├── miapp/                  # Aplicación principal
│   ├── models.py          # Modelos (Producto, Cliente, Pedido, etc)
│   ├── views.py           # Vistas y lógica
│   ├── serializers.py     # Serializadores API REST
│   ├── admin.py           # Configuración admin
│   ├── templates/         # Templates HTML
│   └── static/            # CSS, JS, imágenes
├── tres_en_uno/           # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── Procfile              # Configuración Railway
└── README.md
```

## Modelos Principales

- **Cliente**: Usuarios del sistema
- **Producto**: Productos disponibles para venta
- **Categoria**: Categorías de productos
- **Carrito**: Carrito de compras temporal
- **Pedido**: Pedidos realizados
- **DetallePedido**: Ítems de cada pedido

## Credenciales de Prueba

**Admin:**
- Email: `ventas.tresenuno@gmail.com`
- Password: `[configurada en producción]`

## Configuración de Email

El proyecto usa Gmail para envío de correos. Configurar en `.env`:

```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
```

**Nota:** Usar "Contraseña de aplicación" de Google, no la contraseña normal.

## URLs Principales

- `/` - Inicio
- `/productos/` - Catálogo
- `/producto/<id>/` - Detalle de producto
- `/carrito/` - Carrito de compras
- `/checkout/` - Proceso de pago
- `/perfil/` - Perfil y pedidos del cliente
- `/admin/` - Panel de administración

## Equipo

- **Celine Toledo** - Project Manager & Full-Stack Developer
- **Benjamin Lobos** - Backend Lead & Database Architect  
- **Catalina Berrios** - Frontend Lead & UI/UX Designer

## Licencia

Este proyecto es parte de un proyecto de título académico.

## Problemas Conocidos

- Las imágenes deben estar en `miapp/static/img/productos/`
- Solo acepta transferencias bancarias (Webpay en desarrollo)
- Zonas de entrega limitadas (Coquimbo y Santiago)

## Estado del Proyecto

**Versión:** 1.0.0  
**Estado:** En producción  
**URL:** https://tresenunocultivos.cl

---

Desarrollado por el equipo Tres en Uno
