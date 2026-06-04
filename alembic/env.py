import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

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
    Helper function to dynamically inject a real environment variable 
    if your alembic.ini contains a generic default placeholder.
    """
    # If you use a variable named DATABASE_URL in a .env file, it will load it here
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Fetch configuration section
    ini_section = config.get_section(config.config_ini_section, {})

    # Overwrite the configuration url string dynamically with our helper
    ini_section["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()