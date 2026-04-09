import os

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def _build_database_url() -> str:
    direct_url = os.getenv("KB_DATABASE_URL")
    if direct_url:
        return direct_url

    db_user = os.getenv("KB_DB_USER", "appuser")
    db_password = os.getenv("KB_DB_PASSWORD", "apppass")
    db_host = os.getenv("KB_DB_HOST", "postgres-db")
    db_port = os.getenv("KB_DB_PORT", "5432")
    db_name = os.getenv("KB_DB_NAME", "kb_db")
    return f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = _build_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def ensure_database_exists() -> None:
    db_name = os.getenv("KB_DB_NAME", "kb_db")
    db_user = os.getenv("KB_DB_USER", "appuser")
    db_password = os.getenv("KB_DB_PASSWORD", "apppass")
    db_host = os.getenv("KB_DB_HOST", "postgres-db")
    db_port = os.getenv("KB_DB_PORT", "5432")

    admin_dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    create_sql = f'CREATE DATABASE "{db_name}"'

    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(create_sql)
