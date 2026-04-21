# Tareas completadas

## ✅ Migración a SQLite con SQLAlchemy

### Completado
- [x] Modelo `Customer` con campos: id, name, email, phone, address, created_at
- [x] Modelo `Invoice` con campos: id, customer_id, invoice_number, date, total, status, items, created_at
- [x] Relación entre clientes y facturas (cascade delete)
- [x] Endpoints CRUD de clientes: GET /customers, GET /customers/{id}, POST /customers, PUT /customers/{id}, DELETE /customers/{id}
- [x] Endpoints CRUD de facturas: GET /invoices, GET /invoices/{id}, POST /invoices, PUT /invoices/{id}, DELETE /invoices/{id}
- [x] Endpoint GET /customers/{id}/invoices para listar facturas de un cliente
- [x] Paginación en listados (skip/limit)
- [x] Validación de existencia de cliente antes de crear factura
- [x] Tests: 10/10 pasando
- [x] Base de datos SQLite: `mastersound.db`
- [x] Commit y push a GitHub: `canfron/MasterSound`

### Archivos creados/modificados
- `src/models.py` - Modelos Pydantic para requests/responses
- `src/database.py` - Configuración SQLAlchemy con modelos SQL
- `src/main.py` - API FastAPI con endpoints CRUD
- `tests/test_api.py` - Tests para clientes y facturas
- `requirements.txt` - Dependencias (fastapi, uvicorn, pydantic, sqlalchemy)
- `README.md` - Documentación del proyecto

### Estado
**Fase 3 completada**: API con persistencia en SQLite lista para producción.
