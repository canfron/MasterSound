# MasterSound v2.0 — Gestión Completa de Tienda

API REST + Frontend SPA para gestión integral de tienda de música e instrumentos (MasterSound), con persistencia en SQLite.

## Características

### API Backend

- ✅ CRUD completo de **6 entidades**: clientes, facturas, productos, categorías, proveedores, stock
- ✅ **Pedidos** a proveedores con control de stock automático
- ✅ Dashboard con estadísticas en tiempo real (ingresos, stock bajo, totales)
- ✅ Paginación en todos los listados
- ✅ Búsqueda y filtros por servidor (productos, facturas, clientes)
- ✅ Relación cliente-factura con validación de existencia
- ✅ Control de stock: entradas, salidas y ajustes con registro histórico
- ✅ Persistencia en SQLite (SQLAlchemy, migraciones automáticas)
- ✅ Tests automatizados (10/10 pasando)

### Frontend SPA

- ✅ **Responsive**: sidebar colapsable, tablas adaptivas, mobile cards para <640px
- ✅ **Dashboard** con 6 KPIs (clientes, facturas, pendientes, productos, ingresos del mes, stock bajo)
- ✅ **Panel doble** en dashboard: últimas facturas + alertas de stock bajo
- ✅ **Exportar CSV** desde cada sección (clientes, facturas, productos, categorías, proveedores, stock)
- ✅ **Contadores** de items en tiempo real en cada panel
- ✅ **Búsqueda global** en barra superior
- ✅ **Filtros avanzados** (por categoría, estado, proveedor, stock bajo)
- ✅ **Atajos de teclado**: Ctrl+N (nuevo registro), Ctrl+S (buscar), Escape (cerrar modal)
- ✅ **Auto-refresh** del dashboard cada 2 minutos
- ✅ **Indicador online/offline** en el dashboard
- ✅ **Validación visual** de formularios (campos rojos/verdes al perder foco)
- ✅ **Modal** elegante con animaciones
- ✅ **Notificaciones toast** (éxito, error, info)
- ✅ **Indicadores de carga** con spinner
- ✅ **Formas de pago** integradas al crear facturas con productos

## Estructura

```
MasterSound/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── src/
│   ├── __init__.py
│   ├── database.py       # SQLAlchemy + modelos SQL (7 tablas)
│   ├── main.py           # API FastAPI (~30 endpoints)
│   └── models.py         # Pydantic schemas + DashboardStats
├── static/
│   └── index.html        # SPA frontend (~1171 líneas, sin dependencias JS)
├── tests/
│   └── test_api.py       # Tests de integración
└── Todo.md               # Registro de tareas completadas
```

### Base de datos

```
categories       → Categorías de productos
suppliers        → Proveedores
products         → Productos (con stock, precio, código)
customers        → Clientes
invoices         → Facturas (con items en JSON)
orders           → Pedidos a proveedores
order_items      → Items de pedido
stock_moves      → Historial de movimientos de stock
```

## Instalación

```bash
# Entorno de producción
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Desarrollo

```bash
python -m pip install -r requirements-dev.txt
```

## Ejecución

```bash
source .venv/bin/activate
python src/main.py
```

La API está disponible en `http://localhost:8000`.

- Documentación Swagger interactiva: **http://localhost:8000/api/docs**
- Alternativa (ReDoc): **http://localhost:8000/api/redoc**
- Frontend SPA: **http://localhost:8000/static**
- Health check (root): **http://localhost:8000/**

## Endpoints

### Dashboard

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`  | `/dashboard/stats` | Estadísticas globales (KPIs, facturas recientes, stock bajo) |

### Categorías

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`    | `/categories`        | Listar categorías (`skip`/`limit`) |
| `GET`    | `/categories/{cid}`  | Obtener categoría |
| `POST`   | `/categories`        | Crear categoría |
| `PUT`    | `/categories/{cid}`  | Actualizar categoría |
| `DELETE` | `/categories/{cid}`  | Eliminar categoría |

### Proveedores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`     | `/suppliers`        | Listar proveedores (`skip`/`limit`) |
| `GET`     | `/suppliers/{sid}`  | Obtener proveedor |
| `POST`    | `/suppliers`        | Crear proveedor |
| `PUT`     | `/suppliers/{sid}`  | Actualizar proveedor |
| `DELETE`  | `/suppliers/{sid}`  | Eliminar proveedor |

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`    | `/products`              | Listar productos (`skip`/`limit`, `category`, `supplier`, `search`, `low_stock`) |
| `GET`    | `/products/{pid}`        | Obtener producto |
| `POST`   | `/products`              | Crear producto |
| `PUT`    | `/products/{pid}`        | Actualizar producto |
| `DELETE` | `/products/{pid}`        | Eliminar producto |

> Filtros de listado: `?category=1&supplier=2&search=guitar&low_stock=true`

### Clientes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`     | `/customers`        | Listar clientes (`skip`/`limit`) |
| `GET`     | `/customers/search` | Buscar clientes por nombre/email (`?q=...`) |
| `GET`     | `/customers/{cid}`  | Obtener cliente |
| `POST`    | `/customers`        | Crear cliente |
| `PUT`     | `/customers/{cid}`  | Actualizar cliente |
| `DELETE`  | `/customers/{cid}`  | Eliminar cliente |

### Facturas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`     | `/invoices`            | Listar facturas (`skip`/`limit`, `status=pending|paid`) |
| `GET`     | `/invoices/{iid}`      | Obtener factura |
| `POST`    | `/invoices`            | Crear factura (con items) |
| `PUT`     | `/invoices/{iid}`      | Actualizar factura |
| `PUT`     | `/invoices/{iid}/status` | Cambiar estado (paid/pending) |
| `DELETE`  | `/invoices/{iid}`      | Eliminar factura |
| `GET`     | `/customers/{cid}/invoices` | Facturas de un cliente |

### Pedidos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`     | `/orders`             | Listar pedidos (`skip`/`limit`, `status`) |
| `GET`     | `/orders/{oid}`       | Obtener pedido |
| `POST`    | `/orders`             | Crear pedido (desconta stock al crear) |
| `PUT`     | `/orders/{oid}/status` | Actualizar estado (al recibir, actualiza stock + crea stock move) |
| `DELETE`  | `/orders/{oid}`       | Eliminar pedido |

### Stock

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`     | `/stock-moves`  | Listar movimientos (ordenado por fecha descendente) |
| `POST`    | `/stock-moves`  | Registrar movimiento (tipo: in/out/adjustment) |

## Modelos de datos principales

### Producto
```json
{
  "name": "Fender Stratocaster",
  "code": "FND-STRAT-001",
  "price": 1299.99,
  "category_id": 3,
  "supplier_id": 1,
  "stock": 15,
  "min_stock": 5,
  "description": "Guitarra eléctrica"
}
```

### Factura
```json
{
  "customer_id": 1,
  "invoice_number": "INV-20260501-2847",
  "date": "2026-05-01",
  "total": 2599.98,
  "status": "pending",
  "items": [
    { "product_id": 10, "quantity": 2, "unit_price": 1299.99, "total": 2599.98 }
  ]
}
```

### Movimiento de Stock
```json
{
  "product_id": 10,
  "quantity": 5,
  "type": "in",
  "reference": "PO-20260501-4821",
  "notes": "Reposición del proveedor"
}
```

### Pedido
```json
{
  "customer_id": 1,
  "supplier_id": 2,
  "order_number": "ORD-20260501-9372",
  "date": "2026-05-01",
  "total": 6500.00,
  "status": "pending",
  "items": [
    { "product_id": 10, "quantity": 5, "unit_price": 1299.99 }
  ],
  "notes": "Pedido mayorista"
}
```

## Frontend SPA — Funcionalidades

| Feature | Descripción |
|---------|-------------|
| Dashboard | 6 KPIs + últimas facturas + alertas stock bajo |
| Export CSV | Botón en cada sección para descargar datos |
| Contadores | Número de items en cada panel (badge actualizado) |
| Búsqueda global | Barra superior + búsqueda contextual |
| Filtros | Por estado, categoría, proveedor, stock bajo |
| Atajos | Ctrl+N = nuevo, Ctrl+S = buscar, Escape = cerrar modal |
| Auto-refresh | Dashboard se refresca cada 2 min |
| Conectividad | Indicador Online/Offline en el dashboard |
| Validación visual | Campos del formulario rojos/verdes al validar |
| Responsive | Sidebar colapsable + mobile cards <640px |
| Toasts | Notificaciones animadas (éxito, error, info) |
| Modals | Formularios en modal con animaciones |
| Paginación interna | skip/limit en llamadas API |

## Tests

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Tecnologías

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Base de datos**: SQLite
- **Frontend**: Vanilla HTML/CSS/JS (sin frameworks ni dependencias JS)
- **Testing**: pytest

## Licencia

MIT
