# MasterSound API

API REST para gestión de clientes y facturación con persistencia en SQLite.

## Características

- ✅ CRUD completo de clientes
- ✅ CRUD completo de facturas
- ✅ Relación cliente-factura con validación
- ✅ Paginación en endpoints de listado
- ✅ Persistencia en SQLite
- ✅ Tests automatizados (10/10)

## Estructura

```
MasterSound/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── database.py    # SQLAlchemy + modelos
│   ├── main.py        # API FastAPI
│   └── models.py      # Pydantic schemas
└── tests/
    └── test_api.py    # Tests de integración
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python src/main.py
```

API disponible en: `http://localhost:8000`

## Endpoints

### Clientes

- `GET /customers` - Listar clientes (paginado)
- `GET /customers/{id}` - Obtener cliente
- `POST /customers` - Crear cliente
- `PUT /customers/{id}` - Actualizar cliente
- `DELETE /customers/{id}` - Eliminar cliente

### Facturación

- `GET /invoices` - Listar facturas (paginado)
- `GET /invoices/{id}` - Obtener factura
- `POST /invoices` - Crear factura
- `PUT /invoices/{id}` - Actualizar factura
- `DELETE /invoices/{id}` - Eliminar factura
- `GET /customers/{id}/invoices` - Facturas de un cliente

## Licencia

MIT
