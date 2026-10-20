import sys
import os

# Ensure the root project directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest


@pytest.fixture(scope="session", autouse=True)
def _init_db():
    """Create schema and seed demo data so tests do not depend on a pre-existing DB file."""
    from backend.app.core.database import Base, engine
    from backend.app.data.seed import seed_database
    import backend.app.models.models  # noqa: F401  (register models)

    Base.metadata.create_all(bind=engine)
    seed_database()
