"""
SQL Queries for Local Food Wastage Management System Analysis
Contains all 15 analytical queries as per project requirements
"""
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager

class FoodWastageAnalyzer:
    """Handles all SQL queries and analysis for food wastage management"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
    # ==============================================================
    # FOOD PROVIDERS & RECEIVERS ANALYSIS (Queries 1-4)
    # ==============================================================
    
    def query_1_providers_receivers_by_city(self):
        """Query 1: How many food providers and receivers are there in each city?"""
        query = """
        SELECT 
            COALESCE(p.city, r.city) as city,
            COALESCE(provider_count, 0) as providers,
            COALESCE(receiver_count, 0) as receivers,
            COALESCE(provider_count, 0) + COALESCE(receiver_count, 0) as total_entities
        FROM (
            SELECT city, COUNT(*) as provider_count 
            FROM providers 
            GROUP BY city
        ) p
        FULL OUTER JOIN (
            SELECT city, COUNT(*) as receiver_count 
            FROM receivers 
            GROUP BY city
        ) r ON p.city = r.city
        ORDER BY total_entities DESC, city
        """
        return self.db.fetch_dataframe(query)
    
    def query_2_top_provider_types(self):
        """Query 2: Which type of food provider contributes the most food?"""
        query = """
        SELECT 
            p.type as provider_type,
            COUNT(DISTINCT p.provider_id) as number_of_providers,
            COUNT(f.food_id) as total_food_listings,
            SUM(f.quantity) as total_quantity_contributed,
            ROUND(AVG(f.quantity), 2) as avg_quantity_per_listing,
            ROUND(SUM(f.quantity) * 100.0 / (
                SELECT SUM(quantity) FROM food_listings
            ), 2) as percentage_of_total_quantity
        FROM providers p
        LEFT JOIN food_listings f ON p.provider_id = f.provider_id
        GROUP BY p.type
        ORDER BY total_quantity_contributed DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_3_provider_contacts_by_city(self):
        """Query 3: What is the contact information of food providers in a specific city?"""
        query = """
        SELECT 
            city,
            COUNT(*) as total_providers,
            GROUP_CONCAT(
                name || ' (' || type || ') - ' || contact, 
                '; '
            ) as provider_contacts
        FROM providers
        WHERE city IS NOT NULL AND contact IS NOT NULL
        GROUP BY city
        ORDER BY total_providers DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_4_top_food_claimers(self):
        """Query 4: Which receivers have claimed the most food?"""
        query = """
        SELECT 
            r.receiver_id,
            r.name as receiver_name,
            r.type as receiver_type,
            r.city,
            r.contact,
            COUNT(c.claim_id) as total_claims,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_claims,
            COUNT(CASE WHEN c.status = 'Pending' THEN 1 END) as pending_claims,
            COUNT(CASE WHEN c.status = 'Cancelled' THEN 1 END) as cancelled_claims,
            ROUND(
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 100.0 / 
                COUNT(c.claim_id), 2
            ) as success_rate_percentage,
            SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) as total_food_received
        FROM receivers r
        LEFT JOIN claims c ON r.receiver_id = c.receiver_id
        LEFT JOIN food_listings f ON c.food_id = f.food_id
        GROUP BY r.receiver_id, r.name, r.type, r.city, r.contact
        HAVING total_claims > 0
        ORDER BY total_food_received DESC, total_claims DESC
        LIMIT 20
        """
        return self.db.fetch_dataframe(query)
    
    # ==============================================================
    # FOOD LISTINGS & AVAILABILITY ANALYSIS (Queries 5-7)
    # ==============================================================
    
    def query_5_total_food_available(self):
        """Query 5: What is the total quantity of food available from all providers?"""
        query = """
        SELECT 
            COUNT(food_id) as total_food_items,
            SUM(quantity) as total_quantity_available,
            COUNT(DISTINCT provider_id) as contributing_providers,
            COUNT(DISTINCT location) as locations_covered,
            ROUND(AVG(quantity), 2) as avg_quantity_per_item,
            MIN(quantity) as min_quantity,
            MAX(quantity) as max_quantity,
            COUNT(CASE WHEN expiry_date > date('now') THEN 1 END) as items_not_expired,
            COUNT(CASE WHEN expiry_date <= date('now') THEN 1 END) as items_expired
        FROM food_listings
        """
        return self.db.fetch_dataframe(query)
    
    def query_6_food_listings_by_city(self):
        """Query 6: Which city has the highest number of food listings?"""
        query = """
        SELECT 
            location as city,
            COUNT(food_id) as total_listings,
            SUM(quantity) as total_quantity,
            COUNT(DISTINCT provider_id) as unique_providers,
            COUNT(DISTINCT food_type) as food_type_variety,
            COUNT(DISTINCT meal_type) as meal_type_variety,
            ROUND(AVG(quantity), 2) as avg_quantity_per_listing,
            ROUND(SUM(quantity) * 100.0 / (
                SELECT SUM(quantity) FROM food_listings
            ), 2) as percentage_of_total_food
        FROM food_listings
        GROUP BY location
        ORDER BY total_quantity DESC, total_listings DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_7_common_food_types(self):
        """Query 7: What are the most commonly available food types?"""
        query = """
        SELECT 
            food_type,
            COUNT(food_id) as number_of_listings,
            SUM(quantity) as total_quantity,
            ROUND(AVG(quantity), 2) as avg_quantity_per_listing,
            COUNT(DISTINCT provider_id) as providers_offering,
            COUNT(DISTINCT location) as cities_available,
            ROUND(COUNT(food_id) * 100.0 / (
                SELECT COUNT(*) FROM food_listings
            ), 2) as percentage_of_listings,
            ROUND(SUM(quantity) * 100.0 / (
                SELECT SUM(quantity) FROM food_listings
            ), 2) as percentage_of_total_quantity
        FROM food_listings
        GROUP BY food_type
        ORDER BY total_quantity DESC
        """
        return self.db.fetch_dataframe(query)
    
    # ==============================================================
    # CLAIMS & DISTRIBUTION ANALYSIS (Queries 8-10)
    # ==============================================================
    
    def query_8_claims_per_food_item(self):
        """Query 8: How many food claims have been made for each food item?"""
        query = """
        SELECT 
            f.food_id,
            f.food_name,
            f.quantity as available_quantity,
            f.food_type,
            f.meal_type,
            f.location,
            p.name as provider_name,
            COUNT(c.claim_id) as total_claims,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_claims,
            COUNT(CASE WHEN c.status = 'Pending' THEN 1 END) as pending_claims,
            COUNT(CASE WHEN c.status = 'Cancelled' THEN 1 END) as cancelled_claims,
            ROUND(
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(c.claim_id), 0), 2
            ) as claim_success_rate
        FROM food_listings f
        LEFT JOIN claims c ON f.food_id = c.food_id
        LEFT JOIN providers p ON f.provider_id = p.provider_id
        GROUP BY f.food_id, f.food_name, f.quantity, f.food_type, f.meal_type, f.location, p.name
        HAVING total_claims > 0
        ORDER BY total_claims DESC, completed_claims DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_9_successful_providers(self):
        """Query 9: Which provider has had the highest number of successful food claims?"""
        query = """
        SELECT 
            p.provider_id,
            p.name as provider_name,
            p.type as provider_type,
            p.city,
            p.contact,
            COUNT(DISTINCT f.food_id) as total_food_items_listed,
            COUNT(c.claim_id) as total_claims_received,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as successful_claims,
            COUNT(CASE WHEN c.status = 'Pending' THEN 1 END) as pending_claims,
            COUNT(CASE WHEN c.status = 'Cancelled' THEN 1 END) as cancelled_claims,
            ROUND(
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(c.claim_id), 0), 2
            ) as success_rate_percentage,
            SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) as total_food_distributed
        FROM providers p
        LEFT JOIN food_listings f ON p.provider_id = f.provider_id
        LEFT JOIN claims c ON f.food_id = c.food_id
        GROUP BY p.provider_id, p.name, p.type, p.city, p.contact
        HAVING total_claims_received > 0
        ORDER BY successful_claims DESC, total_food_distributed DESC
        LIMIT 15
        """
        return self.db.fetch_dataframe(query)
    
    def query_10_claim_status_distribution(self):
        """Query 10: What percentage of food claims are completed vs. pending vs. canceled?"""
        query = """
        WITH status_summary AS (
            SELECT 
                status,
                COUNT(*) as claim_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as percentage,
                COUNT(DISTINCT receiver_id) as unique_receivers,
                COUNT(DISTINCT food_id) as unique_food_items,
                MIN(timestamp) as earliest_claim,
                MAX(timestamp) as latest_claim,
                CASE status 
                    WHEN 'Completed' THEN 1 
                    WHEN 'Pending' THEN 2 
                    WHEN 'Cancelled' THEN 3 
                    ELSE 4
                END as sort_order
            FROM claims
            GROUP BY status
            
            UNION ALL
            
            SELECT 
                'TOTAL' as status,
                COUNT(*) as claim_count,
                100.0 as percentage,
                COUNT(DISTINCT receiver_id) as unique_receivers,
                COUNT(DISTINCT food_id) as unique_food_items,
                MIN(timestamp) as earliest_claim,
                MAX(timestamp) as latest_claim,
                5 as sort_order
            FROM claims
        )
        SELECT 
            status,
            claim_count,
            percentage,
            unique_receivers,
            unique_food_items,
            earliest_claim,
            latest_claim
        FROM status_summary
        ORDER BY sort_order
        """
        return self.db.fetch_dataframe(query)
    
    # ==============================================================
    # ANALYSIS & INSIGHTS (Queries 11-15)
    # ==============================================================
    
    def query_11_avg_food_per_receiver(self):
        """Query 11: What is the average quantity of food claimed per receiver?"""
        query = """
        SELECT 
            r.type as receiver_type,
            COUNT(DISTINCT r.receiver_id) as total_receivers,
            COUNT(c.claim_id) as total_claims,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_claims,
            SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) as total_food_received,
            ROUND(
                AVG(CASE WHEN c.status = 'Completed' THEN f.quantity END), 2
            ) as avg_food_per_completed_claim,
            ROUND(
                SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) * 1.0 / 
                NULLIF(COUNT(DISTINCT r.receiver_id), 0), 2
            ) as avg_food_per_receiver,
            ROUND(
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 1.0 / 
                NULLIF(COUNT(DISTINCT r.receiver_id), 0), 2
            ) as avg_successful_claims_per_receiver
        FROM receivers r
        LEFT JOIN claims c ON r.receiver_id = c.receiver_id
        LEFT JOIN food_listings f ON c.food_id = f.food_id
        GROUP BY r.type
        ORDER BY avg_food_per_receiver DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_12_meal_type_popularity(self):
        """Query 12: Which meal type is claimed the most?"""
        query = """
        SELECT 
            f.meal_type,
            COUNT(DISTINCT f.food_id) as total_food_items,
            SUM(f.quantity) as total_quantity_available,
            COUNT(c.claim_id) as total_claims,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_claims,
            COUNT(CASE WHEN c.status = 'Pending' THEN 1 END) as pending_claims,
            COUNT(CASE WHEN c.status = 'Cancelled' THEN 1 END) as cancelled_claims,
            SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) as total_quantity_claimed,
            ROUND(
                COUNT(c.claim_id) * 100.0 / 
                NULLIF(COUNT(DISTINCT f.food_id), 0), 2
            ) as claims_per_food_item_ratio,
            ROUND(
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(c.claim_id), 0), 2
            ) as success_rate_percentage,
            ROUND(
                SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) * 100.0 / 
                NULLIF(SUM(f.quantity), 0), 2
            ) as utilization_rate_percentage
        FROM food_listings f
        LEFT JOIN claims c ON f.food_id = c.food_id
        GROUP BY f.meal_type
        ORDER BY total_quantity_claimed DESC, total_claims DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_13_provider_food_donations(self):
        """Query 13: What is the total quantity of food donated by each provider?"""
        query = """
        SELECT 
            p.provider_id,
            p.name as provider_name,
            p.type as provider_type,
            p.city,
            COUNT(f.food_id) as total_food_items,
            SUM(f.quantity) as total_quantity_donated,
            ROUND(AVG(f.quantity), 2) as avg_quantity_per_item,
            COUNT(DISTINCT f.food_type) as food_type_variety,
            COUNT(DISTINCT f.meal_type) as meal_type_variety,
            COUNT(c.claim_id) as total_claims_received,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as successful_distributions,
            SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) as quantity_successfully_distributed,
            ROUND(
                SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) * 100.0 / 
                NULLIF(SUM(f.quantity), 0), 2
            ) as distribution_efficiency_percentage
        FROM providers p
        LEFT JOIN food_listings f ON p.provider_id = f.provider_id
        LEFT JOIN claims c ON f.food_id = c.food_id
        GROUP BY p.provider_id, p.name, p.type, p.city
        HAVING total_food_items > 0
        ORDER BY total_quantity_donated DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_14_geographic_food_distribution(self):
        """Query 14: Geographic analysis of food distribution patterns"""
        query = """
        SELECT 
            f.location as city,
            COUNT(DISTINCT p.provider_id) as total_providers,
            COUNT(DISTINCT f.food_id) as total_food_listings,
            SUM(f.quantity) as total_food_available,
            COUNT(c.claim_id) as total_claims,
            COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_claims,
            SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) as food_distributed,
            COUNT(DISTINCT c.receiver_id) as unique_receivers_served,
            ROUND(
                COUNT(c.claim_id) * 1.0 / NULLIF(COUNT(DISTINCT f.food_id), 0), 2
            ) as avg_claims_per_food_item,
            ROUND(
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(c.claim_id), 0), 2
            ) as claim_success_rate,
            ROUND(
                SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) * 100.0 / 
                NULLIF(SUM(f.quantity), 0), 2
            ) as food_utilization_rate
        FROM food_listings f
        LEFT JOIN providers p ON f.provider_id = p.provider_id
        LEFT JOIN claims c ON f.food_id = c.food_id
        GROUP BY f.location
        ORDER BY food_distributed DESC, total_food_available DESC
        """
        return self.db.fetch_dataframe(query)
    
    def query_15_comprehensive_system_metrics(self):
        """Query 15: Comprehensive system performance metrics"""
        query = """
        SELECT 
            'System Overview' as metric_category,
            'Total Active Providers' as metric_name,
            COUNT(DISTINCT p.provider_id) as metric_value,
            NULL as percentage
        FROM providers p
        INNER JOIN food_listings f ON p.provider_id = f.provider_id
        
        UNION ALL
        
        SELECT 
            'System Overview' as metric_category,
            'Total Active Receivers' as metric_name,
            COUNT(DISTINCT r.receiver_id) as metric_value,
            NULL as percentage
        FROM receivers r
        INNER JOIN claims c ON r.receiver_id = c.receiver_id
        
        UNION ALL
        
        SELECT 
            'Food Availability' as metric_category,
            'Total Food Items Listed' as metric_name,
            COUNT(*) as metric_value,
            NULL as percentage
        FROM food_listings
        
        UNION ALL
        
        SELECT 
            'Food Availability' as metric_category,
            'Total Quantity Available' as metric_name,
            SUM(quantity) as metric_value,
            NULL as percentage
        FROM food_listings
        
        UNION ALL
        
        SELECT 
            'Claims Performance' as metric_category,
            'Total Claims Made' as metric_name,
            COUNT(*) as metric_value,
            NULL as percentage
        FROM claims
        
        UNION ALL
        
        SELECT 
            'Claims Performance' as metric_category,
            'Successful Claims' as metric_name,
            COUNT(*) as metric_value,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as percentage
        FROM claims 
        WHERE status = 'Completed'
        
        UNION ALL
        
        SELECT 
            'Distribution Efficiency' as metric_category,
            'Food Successfully Distributed' as metric_name,
            SUM(f.quantity) as metric_value,
            ROUND(SUM(f.quantity) * 100.0 / (SELECT SUM(quantity) FROM food_listings), 2) as percentage
        FROM claims c
        INNER JOIN food_listings f ON c.food_id = f.food_id
        WHERE c.status = 'Completed'
        
        ORDER BY metric_category, metric_name
        """
        return self.db.fetch_dataframe(query)
    
    # ==============================================================
    # UTILITY METHODS
    # ==============================================================
    
    def run_all_queries(self, save_results=True):
        """Run all 15 queries and optionally save results"""
        print("🔍 Running all 15 analytical queries...")
        print("="*60)
        
        queries = [
            ("Query 1: Providers & Receivers by City", self.query_1_providers_receivers_by_city),
            ("Query 2: Top Provider Types", self.query_2_top_provider_types),
            ("Query 3: Provider Contacts by City", self.query_3_provider_contacts_by_city),
            ("Query 4: Top Food Claimers", self.query_4_top_food_claimers),
            ("Query 5: Total Food Available", self.query_5_total_food_available),
            ("Query 6: Food Listings by City", self.query_6_food_listings_by_city),
            ("Query 7: Common Food Types", self.query_7_common_food_types),
            ("Query 8: Claims per Food Item", self.query_8_claims_per_food_item),
            ("Query 9: Successful Providers", self.query_9_successful_providers),
            ("Query 10: Claim Status Distribution", self.query_10_claim_status_distribution),
            ("Query 11: Average Food per Receiver", self.query_11_avg_food_per_receiver),
            ("Query 12: Meal Type Popularity", self.query_12_meal_type_popularity),
            ("Query 13: Provider Food Donations", self.query_13_provider_food_donations),
            ("Query 14: Geographic Distribution", self.query_14_geographic_food_distribution),
            ("Query 15: System Metrics", self.query_15_comprehensive_system_metrics)
        ]
        
        results = {}
        
        for query_name, query_func in queries:
            try:
                print(f"📊 Executing: {query_name}")
                result = query_func()
                
                if result is not None and not result.empty:
                    results[query_name] = result
                    print(f"✅ {query_name}: {len(result)} rows returned")
                    
                    # Show sample results
                    print(f"📋 Sample results:")
                    print(result.head(3).to_string(index=False))
                    print()
                else:
                    print(f"⚠️  {query_name}: No data returned")
                    
            except Exception as e:
                print(f"❌ Error in {query_name}: {e}")
                
        print(f"🎉 Query execution completed!")
        print(f"✅ Successful queries: {len(results)}/15")
        
        return results
    
    def get_quick_insights(self):
        """Get quick insights from key queries"""
        print("🔎 QUICK INSIGHTS SUMMARY")
        print("="*40)
        
        try:
            # Total system metrics
            metrics = self.query_15_comprehensive_system_metrics()
            if metrics is not None:
                print("📊 SYSTEM OVERVIEW:")
                for _, row in metrics.iterrows():
                    if row['percentage'] is not None:
                        print(f"   • {row['metric_name']}: {row['metric_value']:,} ({row['percentage']}%)")
                    else:
                        print(f"   • {row['metric_name']}: {row['metric_value']:,}")
                print()
            
            # Top provider types
            providers = self.query_2_top_provider_types()
            if providers is not None:
                print("🏢 TOP PROVIDER TYPES:")
                for _, row in providers.head(3).iterrows():
                    print(f"   • {row['provider_type']}: {row['total_quantity_contributed']:,} units ({row['percentage_of_total_quantity']}%)")
                print()
            
            # Claim success rates
            status_dist = self.query_10_claim_status_distribution()
            if status_dist is not None:
                print("📋 CLAIM SUCCESS RATES:")
                for _, row in status_dist.iterrows():
                    if row['status'] != 'TOTAL':
                        print(f"   • {row['status']}: {row['claim_count']:,} claims ({row['percentage']}%)")
                print()
                
        except Exception as e:
            print(f"❌ Error generating insights: {e}")

if __name__ == "__main__":
    analyzer = FoodWastageAnalyzer()
    
    # Test database connection
    if analyzer.db.get_connection() is None:
        print("❌ Database connection failed!")
        exit()
        
    print("✅ Database connected successfully!")
    
    # Get quick insights
    analyzer.get_quick_insights()
    
    # Ask user if they want to run all queries
    response = input("\nRun all 15 queries? (y/n): ").lower()
    if response == 'y':
        results = analyzer.run_all_queries()
        print(f"\n🎉 Analysis completed! {len(results)} queries executed successfully.")
    else:
        print("Individual queries can be run using the analyzer methods.")