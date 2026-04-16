# Mastersound

Este repositorio contiene el proyecto Mastersound.

## Descripción
MasterSound es un sistema de gestión para una tienda de electrónica que maneja:
- Inventario de productos (componentes, altavoces, relojes, etc.)
- Gestión de caja (ventas, pagos, facturación)
- Control de stock (entrada/salida de mercancía)
- Gestión de pedidos (clientes, proveedores, seguimiento)
- Configuración de precios y descuentos

## Tecnología
- **Backend**: FastAPI (Python)
- **Base de datos**: SQLite (por defecto, extensible)
- **Frontend**: (Opcional, API-first)

## Estructura del proyecto
```
mastersound/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app principal
│   ├── models.py        # Modelos de datos (SQLAlchemy/Pydantic)
│   ├── schemas.py       # Esquemas de API
│   ├── crud.py          # Operaciones CRUD
│   ├── database.py      # Configuración DB
│   └── api/
│       ├── v1/
│       │   ├── __init__.py
│       │   ├── products.py
│       │   ├── sales.py
│       │   ├── orders.py
│       │   └── stock.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
└── .env.example
```

## Features implementadas
- [ ] API de productos (CRUD)
- [ ] API de ventas (caja)
- [ ] API de pedidos
- [ ] API de stock
- [ ] Autenticación (opcional)

## Cómo ejecutar
### Instalación
```bash
pip install -r requirements.txt
```
### Ejecución
```bash
uvicorn src.main:app --reload
```

## Base de datos
SQLite por defecto en `./data/mastersound.db`.

## Configuración
Copiar `.env.example` a `.env` y ajustar valores.

## Datos de inventario
El proyecto no incluye un archivo CSV de inventario inicial. Se debe crear `data/inventory.csv` con los campos: `id, name, description, category, brand, model, price, stock, status`.

## Contribución
1. Crear rama feature/
2. Hacer commit de cambios
3. Abrir PR a main

## Notas
- Proyectos en `/home/canfron/proyectos/repos/mastersound/`
- Estado actual: recuperación de sesión corrompida

## Todo
Ver `Todo.md` para la lista de características planificadas.
