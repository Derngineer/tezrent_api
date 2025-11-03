#!/usr/bin/env python
"""Reset PostgreSQL database by dropping all tables"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def reset_database():
    """Drop all tables in the database"""
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"Found {len(tables)} tables to drop...")
            # Drop all tables
            table_names = ', '.join([f'"{table[0]}"' for table in tables])
            cursor.execute(f"DROP TABLE IF EXISTS {table_names} CASCADE")
            print("✅ All tables dropped successfully!")
        else:
            print("No tables found.")
        
        # Also drop sequences
        cursor.execute("""
            SELECT sequence_name FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """)
        sequences = cursor.fetchall()
        
        if sequences:
            print(f"Found {len(sequences)} sequences to drop...")
            for seq in sequences:
                cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq[0]}" CASCADE')
            print("✅ All sequences dropped!")

if __name__ == '__main__':
    print("🗑️  Resetting PostgreSQL database...")
    reset_database()
    print("\n✅ Database reset complete! Now run: python manage.py migrate")
