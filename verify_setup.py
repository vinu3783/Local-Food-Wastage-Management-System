"""
Verification script for Local Food Wastage Management System setup
Run this after completing Step 2 to verify everything is working correctly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager
from config.settings import DATABASE_PATH, PROCESSED_DATA_DIR

def test_database_connection():
    """Test if database connection works"""
    print("🔗 Testing Database Connection...")
    print("-" * 40)
    
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        
        if conn:
            print("✅ Database connection successful!")
            print(f"📁 Database location: {DATABASE_PATH}")
            
            # Test SQLite version
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            print(f"📊 SQLite version: {version}")
            
            conn.close()
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_tables_exist():
    """Test if all required tables exist"""
    print("\n📋 Testing Tables...")
    print("-" * 40)
    
    try:
        db = DatabaseManager()
        tables = db.get_all_tables()
        
        required_tables = ['providers', 'receivers', 'food_listings', 'claims']
        
        print(f"Found tables: {tables}")
        
        missing_tables = []
        for table in required_tables:
            if table in tables:
                print(f"✅ {table} table exists")
            else:
                print(f"❌ {table} table missing")
                missing_tables.append(table)
        
        if not missing_tables:
            print("🎉 All required tables exist!")
            return True
        else:
            print(f"⚠️  Missing tables: {missing_tables}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def test_data_counts():
    """Test data counts in all tables"""
    print("\n📊 Testing Data Counts...")
    print("-" * 40)
    
    try:
        db = DatabaseManager()
        tables = ['providers', 'receivers', 'food_listings', 'claims']
        
        total_records = 0
        for table in tables:
            if db.table_exists(table):
                count = db.get_row_count(table)
                print(f"📊 {table.capitalize()}: {count:,} records")
                total_records += count
            else:
                print(f"❌ {table} table not found")
                return False
        
        if total_records > 0:
            print(f"\n✅ Total records in database: {total_records:,}")
            return True
        else:
            print("❌ No data found in database!")
            return False
            
    except Exception as e:
        print(f"❌ Error checking data counts: {e}")
        return False

def test_sample_queries():
    """Test sample queries to verify data quality"""
    print("\n🔍 Testing Sample Queries...")
    print("-" * 40)
    
    try:
        db = DatabaseManager()
        
        # Test 1: Provider types
        print("🏪 Provider Types:")
        query1 = "SELECT type, COUNT(*) as count FROM providers GROUP BY type ORDER BY count DESC LIMIT 5"
        result1 = db.fetch_dataframe(query1)
        
        if result1 is not None and not result1.empty:
            for _, row in result1.iterrows():
                print(f"   • {row['type']}: {row['count']} providers")
            print("✅ Provider types query successful")
        else:
            print("❌ Provider types query failed")
            return False
        
        # Test 2: Food types
        print("\n🍽️  Food Types:")
        query2 = "SELECT food_type, COUNT(*) as count FROM food_listings GROUP BY food_type ORDER BY count DESC"
        result2 = db.fetch_dataframe(query2)
        
        if result2 is not None and not result2.empty:
            for _, row in result2.iterrows():
                print(f"   • {row['food_type']}: {row['count']} items")
            print("✅ Food types query successful")
        else:
            print("❌ Food types query failed")
            return False
        
        # Test 3: Claim statuses
        print("\n📋 Claim Statuses:")
        query3 = "SELECT status, COUNT(*) as count FROM claims GROUP BY status ORDER BY count DESC"
        result3 = db.fetch_dataframe(query3)
        
        if result3 is not None and not result3.empty:
            for _, row in result3.iterrows():
                print(f"   • {row['status']}: {row['count']} claims")
            print("✅ Claim statuses query successful")
        else:
            print("❌ Claim statuses query failed")
            return False
        
        # Test 4: Join query (foreign key test)
        print("\n🔗 Testing Foreign Key Relationships:")
        query4 = """
        SELECT p.name as provider_name, COUNT(f.food_id) as food_items 
        FROM providers p 
        LEFT JOIN food_listings f ON p.provider_id = f.provider_id 
        GROUP BY p.provider_id, p.name 
        ORDER BY food_items DESC 
        LIMIT 3
        """
        result4 = db.fetch_dataframe(query4)
        
        if result4 is not None and not result4.empty:
            print("   Top providers by food items:")
            for _, row in result4.iterrows():
                print(f"   • {row['provider_name']}: {row['food_items']} items")
            print("✅ Foreign key relationships working")
        else:
            print("❌ Foreign key test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error running sample queries: {e}")
        return False

def test_processed_files():
    """Test if processed CSV files exist"""
    print("\n📁 Testing Processed Files...")
    print("-" * 40)
    
    required_files = [
        'providers_cleaned.csv',
        'receivers_cleaned.csv',
        'food_listings_cleaned.csv',
        'claims_cleaned.csv'
    ]
    
    missing_files = []
    for file in required_files:
        filepath = PROCESSED_DATA_DIR / file
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✅ {file} exists ({size:,} bytes)")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if not missing_files:
        print("✅ All processed files exist!")
        return True
    else:
        print(f"⚠️  Missing files: {missing_files}")
        return False

def run_all_tests():
    """Run all verification tests"""
    print("🧪 RUNNING VERIFICATION TESTS")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Tables Exist", test_tables_exist),
        ("Data Counts", test_data_counts),
        ("Processed Files", test_processed_files),
        ("Sample Queries", test_sample_queries)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        try:
            if test_function():
                passed_tests += 1
            else:
                print(f"\n⚠️  {test_name} test failed!")
        except Exception as e:
            print(f"\n❌ {test_name} test error: {e}")
    
    # Final summary
    print("\n" + "=" * 50)
    print("🏁 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
        print("✅ Your setup is ready for Step 3: SQL Queries!")
        print("\nNext steps:")
        print("1. Proceed to create SQL queries")
        print("2. Build Streamlit application")
        print("3. Deploy your system")
    else:
        print(f"⚠️  TESTS PASSED: {passed_tests}/{total_tests}")
        print("\nIssues to fix:")
        if passed_tests < 2:
            print("• Run database setup scripts first")
        if passed_tests < 4:
            print("• Run data cleaning notebook")
        if passed_tests < 5:
            print("• Check database loading process")
        
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    
    if not success:
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Ensure you're in the project root directory")
        print("2. Check that all Step 2 scripts have been run")
        print("3. Verify CSV files are in data/raw/ folder")
        print("4. Run: python src/database/create_tables.py")
        print("5. Run: jupyter notebook (data cleaning)")
        print("6. Run: python src/database/data_loader.py")
    
    exit(0 if success else 1)