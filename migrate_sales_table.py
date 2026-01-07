#!/usr/bin/env python3
"""
Migration script to add transaction_id to existing Sales table
Run this once if database already exists
"""

from app import app, get_db_connection
from mysql.connector import Error

def migrate_sales_table():
    """Add transaction_id column to Sales table"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("SHOW COLUMNS FROM Sales LIKE 'transaction_id'")
        result = cursor.fetchone()
        
        if result:
            print("transaction_id column already exists. No migration needed.")
            return True
        
        print("Adding transaction_id column...")
        
        # Add column
        cursor.execute("""
            ALTER TABLE Sales 
            ADD COLUMN transaction_id VARCHAR(50) NOT NULL DEFAULT '' AFTER id
        """)
        
        # Add index
        cursor.execute("""
            ALTER TABLE Sales 
            ADD INDEX idx_transaction (transaction_id)
        """)
        
        # Generate transaction IDs for existing records
        cursor.execute("""
            UPDATE Sales 
            SET transaction_id = CONCAT('TXN-LEGACY-', LPAD(id, 6, '0'))
            WHERE transaction_id = '' OR transaction_id IS NULL
        """)
        
        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"✓ Added transaction_id column")
        print(f"✓ Updated {cursor.rowcount} existing records")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"✗ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("Starting Sales table migration...")
    success = migrate_sales_table()
    if success:
        print("\n✓ You can now use the multiple books per transaction feature!")
    else:
        print("\n✗ Migration failed. Please check the error above.")
