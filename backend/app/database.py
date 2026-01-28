from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.db_utils import clean_database_url_for_asyncpg

settings = get_settings()

# Track database type for configuration
is_sqlite = settings.database_url.startswith("sqlite://")

# Configure engine based on database type
if is_sqlite:
    # SQLite for easy local development (no PostgreSQL required)
    db_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL - clean URL and detect SSL requirement
    db_url, ssl_required = clean_database_url_for_asyncpg(settings.database_url)
    
    if ssl_required:
        engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            connect_args={"ssl": "require"}
        )
    else:
        engine = create_async_engine(db_url, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Alias for backwards compatibility with attendance scheduler
# TODO: Update attendance_scheduler.py to use AsyncSessionLocal directly,
# then remove this alias
async_session_maker = AsyncSessionLocal


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
