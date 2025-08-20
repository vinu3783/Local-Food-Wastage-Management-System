"""
Debug script to fix the food_listings table issue
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager

def debug_food_table():
    """Debug the food_listings table"""
    print("🔍 DEBUGGING FOOD_LISTINGS TABLE")
    print("=" * 40)
    
    db = DatabaseManager()
    
    # Check if table exists
    if not db.table_exists('food_listings'):
        print("❌ food_listings table doesn't exist!")
        print("Run: python src/database/create_tables.py")
        return False
    
    # Check table structure
    print("📋 Table structure:")
    structure = db.get_table_info('food_listings')
    for column in structure:
        print(f"   • {column[1]} ({column[2]})")
    
    # Check row count
    count = db.get_row_count('food_listings')
    print(f"\n📊 Total rows in food_listings: {count}")
    
    if count == 0:
        print("❌ No data in food_listings table!")
        print("Run: python src/database/data_loader.py")
        return False
    
    # Check first few rows
    print("\n📄 Sample data:")
    sample = db.fetch_dataframe("SELECT * FROM food_listings LIMIT 3")
    if sample is not None and not sample.empty:
        print(sample.to_string())
    else:
        print("❌ Cannot fetch sample data")
        return False
    
    # Test the specific query that's failing
    print("\n🧪 Testing food_type query:")
    try:
        result = db.fetch_dataframe("SELECT food_type, COUNT(*) as count FROM food_listings GROUP BY food_type")
        if result is not None and not result.empty:
            print("✅ Query works! Results:")
            print(result.to_string())
            return True
        else:
            print("❌ Query returns empty result")
            return False
    except Exception as e:
        print(f"❌ Query failed with error: {e}")
        return False

def quick_fix():
    """Quick fix for common issues"""
    print("\n🛠️ ATTEMPTING QUICK FIX")
    print("=" * 30)
    
    db = DatabaseManager()
    
    # Check if processed files exist
    from config.settings import PROCESSED_DATA_DIR
    
    food_file = PROCESSED_DATA_DIR / 'food_listings_cleaned.csv'
    if not food_file.exists():
        print("❌ food_listings_cleaned.csv not found!")
        print("Please run the data cleaning notebook first!")
        return False
    
    # Try to reload just the food_listings table
    try:
        import pandas as pd
        
        print("📁 Loading food_listings_cleaned.csv...")
        df = pd.read_csv(food_file)
        print(f"✅ Loaded {len(df)} records from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Clear and reload food_listings table
        print("\n🔄 Reloading food_listings table...")
        db.execute_query("DELETE FROM food_listings")
        
        # Prepare data
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
        
        success = db.execute_many(insert_query, data_tuples)
        
        if success:
            count = db.get_row_count('food_listings')
            print(f"✅ Food listings reloaded: {count} records")
            
            # Test the query again
            result = db.fetch_dataframe("SELECT food_type, COUNT(*) as count FROM food_listings GROUP BY food_type")
            if result is not None and not result.empty:
                print("✅ Food types query now works!")
                print(result.to_string())
                return True
            else:
                print("❌ Query still fails")
                return False
        else:
            print("❌ Failed to reload data")
            return False
            
    except Exception as e:
        print(f"❌ Quick fix failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 DEBUGGING FOOD_LISTINGS ISSUE")
    print("=" * 50)
    
    # First, debug the issue
    success = debug_food_table()
    
    if not success:
        # Try quick fix
        success = quick_fix()
    
    if success:
        print("\n🎉 ISSUE FIXED!")
        print("Run verification again: python verify_setup.py")
    else:
        print("\n💡 MANUAL STEPS NEEDED:")
        print("1. Check if data cleaning notebook completed successfully")
        print("2. Verify food_listings_cleaned.csv exists in data/processed/")
        print("3. Run: python src/database/data_loader.py")
        print("4. Run verification again")