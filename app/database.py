import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.ENV == "development",
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def init_db() -> None:
    logger.info("Initializing database")

    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized")


def health_check() -> bool:
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return True

    except Exception:
        logger.exception("Database health check failed")
        return False

    finally:
        db.close()

