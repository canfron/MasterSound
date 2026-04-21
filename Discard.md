# Discard.md — Decisiones descartadas

## 1. Base de datos en memoria (dict)
**Motivo:** No persistía datos entre reinicios.
**Reemplazado por:** SQLite con SQLAlchemy.

## 2. Modelos Pydantic como única fuente de verdad
**Motivo:** No validaban contra DB.
**Reemplazado por:** SQLAlchemy ORM con Pydantic para serialización.

## 3. Endpoints sin paginación
**Motivo:** Ineficiente con grandes volúmenes.
**Reemplazado por:** Paginación con `skip` y `limit`.

## 4. Facturas sin validación de cliente
**Motivo:** Permitía crear facturas a clientes inexistentes.
**Reemplazado por:** Validación de relación cliente-factura.

## 5. Timestamps en UTC+0 sin timezone
**Motivo:** Inconsistencia horaria.
**Reemplazado por:** `datetime.now(timezone.utc)`.

---

**Estado:** ✅ Proyecto completo y documentado.
