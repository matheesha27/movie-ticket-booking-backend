import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Securely load local .env variables if the package is installed locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 1. Keep your Base import
from app.database.session import Base

# 2. Keep your model imports so Alembic registers them
from app.modules.auth import *
from app.modules.movies.model import *
from app.modules.cinemas.model import *
from app.modules.seats.model import *
from app.modules.bookings.model import *

# 3. Correctly assign the metadata object
target_metadata = Base.metadata

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url():
    """
    Looks for DATABASE_URL in the system environment first (Render / .env).
    If it doesn't exist, it falls back to the alembic.ini placeholder.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Render/Supabase provides strings starting with postgres://
        # SQLAlchemy 1.4+ strictly requires postgresql:// and our explicit driver
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif database_url.startswith("postgresql://") and "+psycopg2" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return database_url

    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # FORCED SCHEMA FIX: Tells Alembic exactly where to build the version table
        version_table_schema="public",
    )

    with context.begin_transaction():
        # FORCED SCHEMA FIX: Tells PostgreSQL to search the public schema for this session
        context.execute("SET search_path TO public, extensions;")
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    ini_section = config.get_section(config.config_ini_section, {})
    ini_section["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # FORCED SCHEMA FIX: Forces the active connection session to target 'public'
        connection.execute(sa.text("SET search_path TO public, extensions;"))

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # FORCED SCHEMA FIX: Ensures the alembic_version table is locked to public
            version_table_schema="public"
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
