from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from svitlogram.database.models import Base
from config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    The run_migrations_offline function is used to run migrations when the database
    is not available. It will receive as arguments the SQLAlchemy URL and a list of
    tables that are missing in the target database; it will then emit a series of
    CREATE TABLE statements for each missing table, along with optional ALTER TABLE
    statements to make changes that aren't handled by Alembic's autogenerate support. 
    
    :return: None
    :doc-author: Trelent
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    The run_migrations_online function is a convenience function that allows you to run migrations against an existing database connection.
    It will create the context and run all the migrations in order, applying them to the current database connection.
    
    
    :return: None
    :doc-author: Trelent
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
    