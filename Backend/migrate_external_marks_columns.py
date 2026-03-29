"""
Database migration script to add new columns to external_marks and semester_results tables.
Run this script to update the database schema after updating the models.

Usage: python migrate_external_marks_columns.py
"""

from sqlalchemy import Column, String, Float, Integer, text
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.models.external_marks import ExternalMarks
from app.models.semester_result import SemesterResult
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_columns_to_external_marks(session: Session):
    """Add new columns to external_marks table"""
    try:
        # Check if columns already exist
        inspector_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'external_marks' 
        AND column_name IN ('batch', 'branch', 'section', 'rollno')
        """
        
        existing_columns = session.execute(text(inspector_query)).fetchall()
        existing_col_names = [col[0] for col in existing_columns]
        
        # Add columns if they don't exist
        if 'batch' not in existing_col_names:
            logger.info("Adding 'batch' column to external_marks table...")
            session.execute(text("ALTER TABLE external_marks ADD COLUMN batch VARCHAR(20)"))
            
        if 'branch' not in existing_col_names:
            logger.info("Adding 'branch' column to external_marks table...")
            session.execute(text("ALTER TABLE external_marks ADD COLUMN branch VARCHAR(20)"))
            
        if 'section' not in existing_col_names:
            logger.info("Adding 'section' column to external_marks table...")
            session.execute(text("ALTER TABLE external_marks ADD COLUMN section VARCHAR(5)"))
            
        if 'rollno' not in existing_col_names:
            logger.info("Adding 'rollno' column to external_marks table...")
            session.execute(text("ALTER TABLE external_marks ADD COLUMN rollno VARCHAR(20)"))
            
        session.commit()
        logger.info("✓ external_marks table migration completed successfully")
        
    except Exception as e:
        logger.error(f"✗ Error migrating external_marks table: {e}")
        session.rollback()
        raise


def add_columns_to_semester_results(session: Session):
    """Add new columns to semester_results table"""
    try:
        # Check if columns already exist
        inspector_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'semester_results' 
        AND column_name IN ('batch', 'branch', 'section', 'rollno', 'cgpa')
        """
        
        existing_columns = session.execute(text(inspector_query)).fetchall()
        existing_col_names = [col[0] for col in existing_columns]
        
        # Add columns if they don't exist
        if 'batch' not in existing_col_names:
            logger.info("Adding 'batch' column to semester_results table...")
            session.execute(text("ALTER TABLE semester_results ADD COLUMN batch VARCHAR(20)"))
            
        if 'branch' not in existing_col_names:
            logger.info("Adding 'branch' column to semester_results table...")
            session.execute(text("ALTER TABLE semester_results ADD COLUMN branch VARCHAR(20)"))
            
        if 'section' not in existing_col_names:
            logger.info("Adding 'section' column to semester_results table...")
            session.execute(text("ALTER TABLE semester_results ADD COLUMN section VARCHAR(5)"))
            
        if 'rollno' not in existing_col_names:
            logger.info("Adding 'rollno' column to semester_results table...")
            session.execute(text("ALTER TABLE semester_results ADD COLUMN rollno VARCHAR(20)"))
            
        if 'cgpa' not in existing_col_names:
            logger.info("Adding 'cgpa' column to semester_results table...")
            session.execute(text("ALTER TABLE semester_results ADD COLUMN cgpa FLOAT"))
            
        session.commit()
        logger.info("✓ semester_results table migration completed successfully")
        
    except Exception as e:
        logger.error(f"✗ Error migrating semester_results table: {e}")
        session.rollback()
        raise


def main():
    """Run all migrations"""
    logger.info("========================================")
    logger.info("Database Migration: External Marks Schema")
    logger.info("========================================")
    
    # Create session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Get database URL from config
    try:
        from app.core.config import Settings
        settings = Settings()
        database_url = settings.DATABASE_URL
    except:
        logger.error("Could not load config. Make sure you're running from the project root.")
        return
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        logger.info("\n1. Migrating external_marks table...")
        add_columns_to_external_marks(session)
        
        logger.info("\n2. Migrating semester_results table...")
        add_columns_to_semester_results(session)
        
        logger.info("\n========================================")
        logger.info("✓ All migrations completed successfully!")
        logger.info("========================================\n")
        
    except Exception as e:
        logger.error(f"\n✗ Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
