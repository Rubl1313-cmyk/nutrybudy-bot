"""
Railway fix for migration 1.5.0
Add this to bot.py after migrations
"""
import asyncio
import logging
from database.db import get_session
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def fix_migration_150():
    """Force apply migration 1.5.0"""
    try:
        async with get_session() as session:
            # Check if columns exist
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND table_schema = 'public'
                AND column_name IN ('chest_cm', 'forearm_cm', 'calf_cm', 'shoulder_width_cm', 'hip_width_cm')
            """))
            existing = [row[0] for row in result.fetchall()]
            
            logger.info(f"Existing columns: {existing}")
            
            # Add missing columns
            columns = [
                ('chest_cm', 'chest_cm'),
                ('forearm_cm', 'forearm_cm'),
                ('calf_cm', 'calf_cm'),
                ('shoulder_width_cm', 'shoulder_width_cm'),
                ('hip_width_cm', 'hip_width_cm')
            ]
            
            for col_name, col_sql in columns:
                if col_name not in existing:
                    try:
                        await session.execute(text(f"ALTER TABLE users ADD COLUMN {col_sql} FLOAT"))
                        logger.info(f"Added column: {col_name}")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.warning(f"Column {col_name} already exists")
                        else:
                            logger.error(f"Error adding {col_name}: {e}")
                            raise
                else:
                    logger.info(f"Column {col_name} already exists")
            
            # Mark migration as applied
            await session.execute(text("""
                INSERT INTO schema_migrations (version, description, applied_at)
                VALUES ('1.5.0', 'Add advanced anthropometry fields (girths only)', CURRENT_TIMESTAMP)
                ON CONFLICT (version) DO NOTHING
            """))
            
            await session.commit()
            logger.info("Migration 1.5.0 fix completed!")
            
    except Exception as e:
        logger.error(f"Migration 1.5.0 fix failed: {e}")
        raise

# Add this to bot.py after run_migrations():
# await fix_migration_150()
