import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import get_settings
from app.core.db_utils import clean_database_url_for_asyncpg
from app.models import Base

settings = get_settings()
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Handle SQLite vs PostgreSQL
is_sqlite = settings.database_url.startswith("sqlite://")
if is_sqlite:
    db_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    ssl_required = False
else:
    # Clean database URL and detect SSL requirement for PostgreSQL
    db_url, ssl_required = clean_database_url_for_asyncpg(settings.database_url)

config.set_main_option("sqlalchemy.url", db_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Prepare connect_args based on database type
    connect_args = {}
    if is_sqlite:
        connect_args = {"check_same_thread": False}
    elif ssl_required:
        connect_args = {"ssl": "require"}
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = db_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async def run_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
