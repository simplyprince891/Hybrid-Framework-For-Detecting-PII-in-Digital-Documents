from .database import engine
from .models import Base
import sqlalchemy

def ensure_schema():
    """Ensure required schema changes are applied (add new columns if missing).

    This is a tiny, safe migration helper used in-development/tests to keep the
    DB schema in sync when columns are added during quick iterations.
    """
    # create missing tables
    Base.metadata.create_all(bind=engine)

    # ensure 'score' column exists on detections table (SQLite)
    try:
        with engine.connect() as conn:
            insp = sqlalchemy.inspect(conn)
            cols = [c['name'] for c in insp.get_columns('detections')] if insp.has_table('detections') else []
            # Add score column if missing
            if 'score' not in cols:
                conn.execute(sqlalchemy.text('ALTER TABLE detections ADD COLUMN score INTEGER'))
            # Add masked_value column if missing
            if 'masked_value' not in cols:
                conn.execute(sqlalchemy.text("ALTER TABLE detections ADD COLUMN masked_value VARCHAR"))
    except Exception:
        # best-effort: don't fail startup if migration can't be applied
        pass

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
