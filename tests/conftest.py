"""
Pytest configuration for MasterSound API tests.

Uses SQLite in-memory with StaticPool so the TestClient and all test fixtures
share the same ephemeral database. Main.py (and therefore database.py) is
patched before it is imported by any test file.
"""
import sys
import pytest


def _patch_database_engine():
    """Replace src.database engine with SQLite in-memory (StaticPool).

    Called before any test module imports main.py so the in-memory DB is
    shared across all TestClient requests.
    """
    # Remove cached modules so they will be re-imported with the new engine
    for mod in list(sys.modules.keys()):
        if mod.startswith("src.main") or mod.startswith("src.database") or mod.startswith("src.models"):
            del sys.modules[mod]

    # Import database so we can patch its engine before main.py uses it
    import src.database as db_module  # pyright: ignore [reportUnknownVariableType]

    # Patch the module attributes to use in-memory SQLite with StaticPool
    db_module.SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # pyright: ignore [reportAttributeAccessIssue]
    from sqlalchemy import create_engine
    db_module.engine = create_engine(  # pyright: ignore [reportAttributeAccessIssue]
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool,
    )
    db_module.SessionLocal = db_module.sessionmaker(  # pyright: ignore [reportAttributeAccessIssue]
        autocommit=False, autoflush=False, bind=db_module.engine
    )
    # Create tables on the new in-memory engine
    from src.database import Base
    Base.metadata.create_all(bind=db_module.engine)

    return db_module


@pytest.fixture(scope="session", autouse=True)
def configure_test_db():
    """Session-scoped fixture: runs once per pytest invocation, BEFORE any test module loads."""
    db_module = _patch_database_engine()
    yield


@pytest.fixture(autouse=True)
def clear_test_data():
    """Truncate all tables between tests for isolation."""
    import src.database as db_module
    SessionLocal = db_module.SessionLocal
    db = SessionLocal()
    try:
        tables = [db_module.StockMove, db_module.OrderItem, db_module.Order,
                  db_module.Invoice, db_module.Product, db_module.Supplier,
                  db_module.Customer, db_module.Category]
        for tbl in tables:
            db.execute(tbl.__table__.delete())
        db.commit()
    finally:
        db.close()
