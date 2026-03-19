#!/usr/bin/env python3
"""Database migration script - creates all tables including new ones.

Usage: python scripts/migrate.py (run from project root)
   or:  cd .. && python -m backend.scripts.migrate
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path so 'backend.' imports work
PROJECT_ROOT = Path(__file__).parent.parent.parent  # scripts -> backend -> project_root
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.core.config import settings
from backend.core.database import Base
from backend.models import (
    Job,
    JobCache,
    Profile,
    Experience,
    Education,
    Project,
    Certification,
    Resume,
    Application,
    ApplicationTimeline,
    Email,
    EmailTemplate,
    User,
    AIModelConfig,
    ScrapeRun,
)


async def run_migration():
    db_url = str(settings.DATABASE_URL)
    print(f"Connecting to: {db_url[:60]}...")
    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        # Detect database type and get existing tables
        try:
            # PostgreSQL
            r = await conn.run_sync(
                lambda sc: sc.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                )
            )
            existing = {row[0] for row in r.fetchall()}
            db_type = "postgresql"
        except Exception:
            try:
                # SQLite
                r = await conn.run_sync(
                    lambda sc: sc.execute(
                        text("SELECT name FROM sqlite_master WHERE type='table'")
                    )
                )
                existing = {row[0] for row in r.fetchall()}
                db_type = "sqlite"
            except Exception as e:
                print(f"Could not detect database type: {e}")
                return

        print(
            f"Database: {db_type}, Existing tables ({len(existing)}): {sorted(existing)}"
        )

        for table in Base.metadata.sorted_tables:
            if table.name not in existing:
                await conn.run_sync(table.create)
                print(f"  Created: {table.name}")
            else:
                # Check for missing columns
                await conn.run_sync(
                    _add_missing_columns, table, db_type
                )
                print(f"  Checked: {table.name}")

    await engine.dispose()
    print("\nMigration complete!")


def _add_missing_columns(sync_conn, table, db_type):
    """Add missing columns to existing table."""
    if db_type == "sqlite":
        pragma = f"PRAGMA table_info({table.name})"
    else:
        # PostgreSQL - query information_schema
        pragma = f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = '{table.name}'
        """

    try:
        result = sync_conn.execute(text(pragma))
        if db_type == "sqlite":
            existing_cols = {row[1] for row in result.fetchall()}
        else:
            existing_cols = {row[0] for row in result.fetchall()}
    except Exception:
        return

    for col in table.columns:
        if col.name not in existing_cols:
            col_type = str(col.type)
            col_def = f"{col.name} {col_type}"
            if col.default is not None:
                col_def += f" DEFAULT {col.default}"
            if not col.nullable:
                col_def += " NOT NULL"

            try:
                sync_conn.execute(
                    text(f"ALTER TABLE {table.name} ADD COLUMN {col_def}")
                )
                print(f"    + Added column: {table.name}.{col.name}")
            except Exception as e:
                print(f"    ! Could not add {table.name}.{col.name}: {e}")


if __name__ == "__main__":
    asyncio.run(run_migration())
