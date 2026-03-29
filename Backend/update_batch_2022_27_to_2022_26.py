"""
Script to update batch values from 2022-27 to 2022-26 in the database.

This updates the academic table batch column.
Run this once to update all student batch records.
"""

from app.core.database import SessionLocal
from app.models.academic import Academic
from sqlalchemy import func

def update_batch_2022_27_to_2022_26():
    """Update all students with batch 2022-27 to 2022-26"""
    
    db = SessionLocal()
    try:
        # Check current state
        print("=== CURRENT STATE ===")
        batches = db.query(Academic.batch, func.count(Academic.batch)).group_by(Academic.batch).all()
        for batch, count in batches:
            print(f"Batch {batch}: {count} students")
        
        # Count records to update
        records_to_update = db.query(Academic).filter(Academic.batch == "2022-27").count()
        
        if records_to_update == 0:
            print("\n✓ No records with batch 2022-27 found. Already updated!")
            return
        
        print(f"\n=== UPDATING ===")
        print(f"Found {records_to_update} student records with batch 2022-27")
        print(f"Updating to batch 2022-26...")
        
        # Update all records
        db.query(Academic).filter(Academic.batch == "2022-27").update(
            {Academic.batch: "2022-26"}
        )
        db.commit()
        
        print(f"✓ Successfully updated {records_to_update} records!")
        
        # Verify update
        print("\n=== VERIFICATION ===")
        batches = db.query(Academic.batch, func.count(Academic.batch)).group_by(Academic.batch).all()
        for batch, count in batches:
            print(f"Batch {batch}: {count} students")
        
        # Show sample of updated records
        print("\n=== SAMPLE OF UPDATED RECORDS ===")
        students = db.query(Academic).filter(Academic.batch == "2022-26").limit(5).all()
        for a in students:
            print(f"Student ID: {a.sid:3d} | Batch: {a.batch} | Branch: {a.branch} | Section: {a.section}")
            
        print("\n✓ Batch update completed successfully!")
        print("\nNext steps:")
        print("1. Restart the backend server (Uvicorn)")
        print("2. Open browser and press Ctrl+Shift+Delete to clear cache")
        print("3. Login and check Admin → Students page")
        print("4. You should now see batch 2022-26")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error updating batch: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_batch_2022_27_to_2022_26()
