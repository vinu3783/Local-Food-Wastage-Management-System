"""
Create database tables for Local Food Wastage Management System
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager

class TableCreator:
    """Handles database table creation"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
    def create_providers_table(self):
        """Create providers table"""
        query = """
        CREATE TABLE IF NOT EXISTS providers (
            provider_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            contact TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        return self.db.execute_query(query)
        
    def create_receivers_table(self):
        """Create receivers table"""
        query = """
        CREATE TABLE IF NOT EXISTS receivers (
            receiver_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            city TEXT NOT NULL,
            contact TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        return self.db.execute_query(query)
        
    def create_food_listings_table(self):
        """Create food_listings table"""
        query = """
        CREATE TABLE IF NOT EXISTS food_listings (
            food_id INTEGER PRIMARY KEY,
            food_name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            expiry_date DATE NOT NULL,
            provider_id INTEGER NOT NULL,
            provider_type TEXT NOT NULL,
            location TEXT NOT NULL,
            food_type TEXT NOT NULL CHECK (food_type IN ('Vegetarian', 'Non-Vegetarian', 'Vegan')),
            meal_type TEXT NOT NULL CHECK (meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snacks')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
        )
        """
        return self.db.execute_query(query)
        
    def create_claims_table(self):
        """Create claims table"""
        query = """
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY,
            food_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('Pending', 'Completed', 'Cancelled')),
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (food_id) REFERENCES food_listings (food_id),
            FOREIGN KEY (receiver_id) REFERENCES receivers (receiver_id)
        )
        """
        return self.db.execute_query(query)
        
    def create_indexes(self):
        """Create indexes for better query performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_providers_city ON providers(city)",
            "CREATE INDEX IF NOT EXISTS idx_providers_type ON providers(type)",
            "CREATE INDEX IF NOT EXISTS idx_receivers_city ON receivers(city)",
            "CREATE INDEX IF NOT EXISTS idx_receivers_type ON receivers(type)",
            "CREATE INDEX IF NOT EXISTS idx_food_location ON food_listings(location)",
            "CREATE INDEX IF NOT EXISTS idx_food_type ON food_listings(food_type)",
            "CREATE INDEX IF NOT EXISTS idx_food_meal_type ON food_listings(meal_type)",
            "CREATE INDEX IF NOT EXISTS idx_food_expiry ON food_listings(expiry_date)",
            "CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)",
            "CREATE INDEX IF NOT EXISTS idx_claims_timestamp ON claims(timestamp)"
        ]
        
        for index_query in indexes:
            self.db.execute_query(index_query)
            
    def create_all_tables(self):
        """Create all tables and indexes"""
        print("Creating database tables...")
        print("="*40)
        
        try:
            # Create tables
            self.create_providers_table()
            print("✅ Providers table created")
            
            self.create_receivers_table()
            print("✅ Receivers table created")
            
            self.create_food_listings_table()
            print("✅ Food listings table created")
            
            self.create_claims_table()
            print("✅ Claims table created")
            
            # Create indexes
            self.create_indexes()
            print("✅ Indexes created")
            
            print("\n🎉 All tables created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
            
    def show_table_structure(self):
        """Display structure of all tables"""
        tables = ['providers', 'receivers', 'food_listings', 'claims']
        
        print("\n📋 DATABASE SCHEMA:")
        print("="*50)
        
        for table in tables:
            if self.db.table_exists(table):
                print(f"\n🔸 {table.upper()} TABLE:")
                structure = self.db.get_table_info(table)
                for column in structure:
                    print(f"  • {column[1]} ({column[2]})")
            else:
                print(f"\n❌ {table} table doesn't exist")
                
    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        tables = ['claims', 'food_listings', 'receivers', 'providers']  # Order matters due to foreign keys
        
        print("⚠️  Dropping all tables...")
        for table in tables:
            self.db.drop_table(table)
            print(f"🗑️  Dropped {table} table")

if __name__ == "__main__":
    creator = TableCreator()
    
    # Show existing tables
    existing_tables = creator.db.get_all_tables()
    if existing_tables:
        print(f"📋 Existing tables: {existing_tables}")
        
        # Ask user if they want to recreate tables
        response = input("\nTables already exist. Recreate them? (y/n): ").lower()
        if response == 'y':
            creator.drop_all_tables()
        else:
            print("Keeping existing tables.")
            creator.show_table_structure()
            exit()
    
    # Create all tables
    success = creator.create_all_tables()
    
    if success:
        creator.show_table_structure()
        
        # Show final status
        print(f"\n📊 DATABASE STATUS:")
        print(f"📁 Location: {creator.db.db_path}")
        print(f"📋 Tables: {creator.db.get_all_tables()}")
    else:
        print("❌ Failed to create database tables!")