"""
Load cleaned data into database for Local Food Wastage Management System
"""
import pandas as pd
import sys
from pathlib import Path
import sqlite3

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager
from config.settings import PROCESSED_DATA_DIR

class DataLoader:
    """Handles loading cleaned data into database"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.processed_dir = PROCESSED_DATA_DIR
        
    def load_csv_to_dataframe(self, filename):
        """Load CSV file to pandas DataFrame"""
        filepath = self.processed_dir / filename
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return None
            
        try:
            df = pd.read_csv(filepath)
            print(f"✅ Loaded {filename}: {len(df)} records")
            return df
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return None
            
    def load_providers(self):
        """Load providers data into database"""
        df = self.load_csv_to_dataframe('providers_cleaned.csv')
        if df is None:
            return False
            
        try:
            # Clear existing data
            self.db.execute_query("DELETE FROM providers")
            
            # Prepare data for insertion
            data_tuples = []
            for _, row in df.iterrows():
                data_tuples.append((
                    int(row['provider_id']),
                    str(row['name']),
                    str(row['type']),
                    str(row['address']),
                    str(row['city']),
                    str(row['contact']) if pd.notna(row['contact']) else ''
                ))
            
            # Insert data
            insert_query = """
            INSERT INTO providers (provider_id, name, type, address, city, contact)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            success = self.db.execute_many(insert_query, data_tuples)
            
            if success:
                count = self.db.get_row_count('providers')
                print(f"✅ Providers loaded: {count} records")
                return True
            else:
                print("❌ Failed to load providers")
                return False
                
        except Exception as e:
            print(f"❌ Error loading providers: {e}")
            return False
            
    def load_receivers(self):
        """Load receivers data into database"""
        df = self.load_csv_to_dataframe('receivers_cleaned.csv')
        if df is None:
            return False
            
        try:
            # Clear existing data
            self.db.execute_query("DELETE FROM receivers")
            
            # Prepare data for insertion
            data_tuples = []
            for _, row in df.iterrows():
                data_tuples.append((
                    int(row['receiver_id']),
                    str(row['name']),
                    str(row['type']),
                    str(row['city']),
                    str(row['contact']) if pd.notna(row['contact']) else ''
                ))
            
            # Insert data
            insert_query = """
            INSERT INTO receivers (receiver_id, name, type, city, contact)
            VALUES (?, ?, ?, ?, ?)
            """
            
            success = self.db.execute_many(insert_query, data_tuples)
            
            if success:
                count = self.db.get_row_count('receivers')
                print(f"✅ Receivers loaded: {count} records")
                return True
            else:
                print("❌ Failed to load receivers")
                return False
                
        except Exception as e:
            print(f"❌ Error loading receivers: {e}")
            return False
            
    def load_food_listings(self):
        """Load food listings data into database"""
        df = self.load_csv_to_dataframe('food_listings_cleaned.csv')
        if df is None:
            return False
            
        try:
            # Clear existing data
            self.db.execute_query("DELETE FROM food_listings")
            
            # Prepare data for insertion
            data_tuples = []
            for _, row in df.iterrows():
                data_tuples.append((
                    int(row['food_id']),
                    str(row['food_name']),
                    int(row['quantity']),
                    str(row['expiry_date']),
                    int(row['provider_id']),
                    str(row['provider_type']),
                    str(row['location']),
                    str(row['food_type']),
                    str(row['meal_type'])
                ))
            
            # Insert data
            insert_query = """
            INSERT INTO food_listings 
            (food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            success = self.db.execute_many(insert_query, data_tuples)
            
            if success:
                count = self.db.get_row_count('food_listings')
                print(f"✅ Food listings loaded: {count} records")
                return True
            else:
                print("❌ Failed to load food listings")
                return False
                
        except Exception as e:
            print(f"❌ Error loading food listings: {e}")
            return False
            
    def load_claims(self):
        """Load claims data into database"""
        df = self.load_csv_to_dataframe('claims_cleaned.csv')
        if df is None:
            return False
            
        try:
            # Clear existing data
            self.db.execute_query("DELETE FROM claims")
            
            # Prepare data for insertion
            data_tuples = []
            for _, row in df.iterrows():
                data_tuples.append((
                    int(row['claim_id']),
                    int(row['food_id']),
                    int(row['receiver_id']),
                    str(row['status']),
                    str(row['timestamp'])
                ))
            
            # Insert data
            insert_query = """
            INSERT INTO claims (claim_id, food_id, receiver_id, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """
            
            success = self.db.execute_many(insert_query, data_tuples)
            
            if success:
                count = self.db.get_row_count('claims')
                print(f"✅ Claims loaded: {count} records")
                return True
            else:
                print("❌ Failed to load claims")
                return False
                
        except Exception as e:
            print(f"❌ Error loading claims: {e}")
            return False
            
    def load_all_data(self):
        """Load all cleaned data into database"""
        print("🚀 Loading all data into database...")
        print("="*50)
        
        # Check if processed files exist
        required_files = [
            'providers_cleaned.csv',
            'receivers_cleaned.csv', 
            'food_listings_cleaned.csv',
            'claims_cleaned.csv'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.processed_dir / file).exists():
                missing_files.append(file)
                
        if missing_files:
            print(f"❌ Missing processed files: {missing_files}")
            print("Please run data cleaning notebook first!")
            return False
        
        # Load data in correct order (respecting foreign key constraints)
        success_count = 0
        
        if self.load_providers():
            success_count += 1
            
        if self.load_receivers():
            success_count += 1
            
        if self.load_food_listings():
            success_count += 1
            
        if self.load_claims():
            success_count += 1
            
        print(f"\n📊 LOADING SUMMARY:")
        print(f"✅ Successfully loaded: {success_count}/4 tables")
        
        if success_count == 4:
            print("🎉 All data loaded successfully!")
            self.show_database_summary()
            return True
        else:
            print("⚠️  Some tables failed to load")
            return False
            
    def show_database_summary(self):
        """Show summary of loaded data"""
        print(f"\n📋 DATABASE SUMMARY:")
        print("="*30)
        
        tables = ['providers', 'receivers', 'food_listings', 'claims']
        
        for table in tables:
            count = self.db.get_row_count(table)
            print(f"📊 {table.capitalize()}: {count:,} records")
            
        # Show some basic statistics
        print(f"\n🔍 QUICK INSIGHTS:")
        
        # Provider types
        provider_types = self.db.fetch_dataframe("SELECT type, COUNT(*) as count FROM providers GROUP BY type ORDER BY count DESC")
        if provider_types is not None and not provider_types.empty:
            print(f"📈 Top provider types:")
            for _, row in provider_types.head(3).iterrows():
                print(f"   • {row['type']}: {row['count']} providers")
        
        # Food types
        food_types = self.db.fetch_dataframe("SELECT food_type, COUNT(*) as count FROM food_listings GROUP BY food_type ORDER BY count DESC")
        if food_types is not None and not food_types.empty:
            print(f"🍽️  Food types:")
            for _, row in food_types.iterrows():
                print(f"   • {row['food_type']}: {row['count']} items")
        
        # Claim status
        claim_status = self.db.fetch_dataframe("SELECT status, COUNT(*) as count FROM claims GROUP BY status ORDER BY count DESC")
        if claim_status is not None and not claim_status.empty:
            print(f"📋 Claim statuses:")
            for _, row in claim_status.iterrows():
                print(f"   • {row['status']}: {row['count']} claims")
                
    def verify_data_integrity(self):
        """Verify data integrity and foreign key relationships"""
        print(f"\n🔍 VERIFYING DATA INTEGRITY:")
        print("="*40)
        
        integrity_checks = []
        
        # Check 1: All food listings have valid provider IDs
        check1 = self.db.fetch_dataframe("""
            SELECT COUNT(*) as count 
            FROM food_listings f 
            LEFT JOIN providers p ON f.provider_id = p.provider_id 
            WHERE p.provider_id IS NULL
        """)
        
        if check1 is not None and check1.iloc[0]['count'] == 0:
            print("✅ All food listings have valid provider IDs")
            integrity_checks.append(True)
        else:
            print(f"❌ {check1.iloc[0]['count']} food listings have invalid provider IDs")
            integrity_checks.append(False)
        
        # Check 2: All claims have valid food IDs
        check2 = self.db.fetch_dataframe("""
            SELECT COUNT(*) as count 
            FROM claims c 
            LEFT JOIN food_listings f ON c.food_id = f.food_id 
            WHERE f.food_id IS NULL
        """)
        
        if check2 is not None and check2.iloc[0]['count'] == 0:
            print("✅ All claims have valid food IDs")
            integrity_checks.append(True)
        else:
            print(f"❌ {check2.iloc[0]['count']} claims have invalid food IDs")
            integrity_checks.append(False)
        
        # Check 3: All claims have valid receiver IDs
        check3 = self.db.fetch_dataframe("""
            SELECT COUNT(*) as count 
            FROM claims c 
            LEFT JOIN receivers r ON c.receiver_id = r.receiver_id 
            WHERE r.receiver_id IS NULL
        """)
        
        if check3 is not None and check3.iloc[0]['count'] == 0:
            print("✅ All claims have valid receiver IDs")
            integrity_checks.append(True)
        else:
            print(f"❌ {check3.iloc[0]['count']} claims have invalid receiver IDs")
            integrity_checks.append(False)
        
        # Check 4: No duplicate primary keys
        for table, pk_column in [('providers', 'provider_id'), ('receivers', 'receiver_id'), 
                                ('food_listings', 'food_id'), ('claims', 'claim_id')]:
            duplicate_check = self.db.fetch_dataframe(f"""
                SELECT {pk_column}, COUNT(*) as count 
                FROM {table} 
                GROUP BY {pk_column} 
                HAVING COUNT(*) > 1
            """)
            
            if duplicate_check is not None and duplicate_check.empty:
                print(f"✅ No duplicate {pk_column}s in {table}")
                integrity_checks.append(True)
            else:
                print(f"❌ Duplicate {pk_column}s found in {table}")
                integrity_checks.append(False)
        
        # Overall integrity status
        if all(integrity_checks):
            print(f"\n🎉 All integrity checks passed!")
            return True
        else:
            print(f"\n⚠️  Some integrity checks failed!")
            return False

if __name__ == "__main__":
    loader = DataLoader()
    
    # Check if database tables exist
    tables = loader.db.get_all_tables()
    if not tables:
        print("❌ No database tables found!")
        print("Please run 'python src/database/create_tables.py' first!")
        exit()
    
    print(f"📋 Found tables: {tables}")
    
    # Check if processed data exists
    if not PROCESSED_DATA_DIR.exists():
        print("❌ Processed data directory not found!")
        print("Please run the data cleaning notebook first!")
        exit()
    
    # Load all data
    success = loader.load_all_data()
    
    if success:
        # Verify data integrity
        loader.verify_data_integrity()
        
        print(f"\n🎉 Database setup completed successfully!")
        print(f"📁 Database location: {loader.db.db_path}")
        print(f"📊 Ready for SQL queries and analysis!")
    else:
        print(f"\n❌ Database setup failed!")
        print("Please check the error messages above.")