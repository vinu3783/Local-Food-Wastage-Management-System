"""
Database connection and management for Local Food Wastage Management System
"""
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import DATABASE_PATH, DATABASE_DIR

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.ensure_database_directory()
        
    def ensure_database_directory(self):
        """Create database directory if it doesn't exist"""
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None
            
    def execute_query(self, query, params=None):
        """Execute a single query"""
        conn = self.get_connection()
        if conn is None:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            conn.close()
            
    def execute_many(self, query, data_list):
        """Execute query with multiple parameter sets"""
        conn = self.get_connection()
        if conn is None:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.executemany(query, data_list)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error executing batch query: {e}")
            return False
        finally:
            conn.close()
            
    def fetch_dataframe(self, query, params=None):
        """Fetch query results as pandas DataFrame"""
        conn = self.get_connection()
        if conn is None:
            return None
            
        try:
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print(f"Error fetching dataframe: {e}")
            return None
        finally:
            conn.close()
            
    def table_exists(self, table_name):
        """Check if table exists in database"""
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,))
        return len(result) > 0 if result else False
        
    def get_table_info(self, table_name):
        """Get table schema information"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
        
    def get_all_tables(self):
        """Get list of all tables in database"""
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        result = self.execute_query(query)
        return [row[0] for row in result] if result else []
        
    def drop_table(self, table_name):
        """Drop a table if it exists"""
        query = f"DROP TABLE IF EXISTS {table_name}"
        return self.execute_query(query)
        
    def get_row_count(self, table_name):
        """Get number of rows in a table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.execute_query(query)
        return result[0][0] if result else 0

# Test the database connection
if __name__ == "__main__":
    print("Testing Database Connection...")
    print("="*40)
    
    db = DatabaseManager()
    
    # Test connection
    conn = db.get_connection()
    if conn:
        print("✅ Database connection successful!")
        print(f"📁 Database location: {db.db_path}")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"📊 SQLite version: {version}")
        
        conn.close()
    else:
        print("❌ Database connection failed!")
        
    # Check existing tables
    tables = db.get_all_tables()
    if tables:
        print(f"📋 Existing tables: {tables}")
    else:
        print("📋 No tables found - ready for setup!")
        
    print("\nDatabase manager ready for use!")