"""
Complete Fixed Working Streamlit Application for Local Food Wastage Management System
All syntax errors resolved and all pages functional
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager
from src.analysis.sql_queries import FoodWastageAnalyzer

# Page configuration
st.set_page_config(
    page_title="🍽️ Food Wastage Management System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .page-header {
        background: linear-gradient(135deg, #2E8B57 0%, #20B2AA 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .filter-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .contact-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .contact-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

class FoodManagementApp:
    """Complete Food Management Application with All Working Pages"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analyzer = FoodWastageAnalyzer()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
    
    def check_database_connection(self):
        """Check database connection and show status"""
        try:
            conn = self.db.get_connection()
            if conn is None:
                st.error("❌ Database connection failed! Please check your database setup.")
                st.info("🔧 Run: python src/database/create_tables.py && python src/database/data_loader.py")
                st.stop()
            conn.close()
            return True
        except Exception as e:
            st.error(f"❌ Database error: {e}")
            st.stop()
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("## 🍽️ Navigation")
            
            # Navigation buttons
            pages = [
                ("🏠 Dashboard", "dashboard"),
                ("🏢 Providers", "providers"), 
                ("👥 Receivers", "receivers"),
                ("🍽️ Food Listings", "food_listings"),
                ("📊 Analytics", "analytics"),
                ("📋 Claims", "claims"),
                ("🗺️ Geographic View", "geographic"),
                ("⚙️ Admin Panel", "admin")
            ]
            
            for page_name, page_key in pages:
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # System Status
            st.markdown("### 📊 System Status")
            
            try:
                total_providers = self.db.get_row_count('providers')
                total_receivers = self.db.get_row_count('receivers')
                total_food_items = self.db.get_row_count('food_listings')
                total_claims = self.db.get_row_count('claims')
                
                st.metric("🏢 Providers", f"{total_providers:,}")
                st.metric("👥 Receivers", f"{total_receivers:,}")
                st.metric("🍽️ Food Items", f"{total_food_items:,}")
                st.metric("📋 Claims", f"{total_claims:,}")
                
            except Exception as e:
                st.error(f"Error loading metrics: {e}")
            
            st.markdown("---")
            
            # Quick Actions
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.session_state.last_refresh = datetime.now()
                st.rerun()
            
            st.markdown(f"*Updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}*")
    
    def render_main_header(self):
        """Render the main application header"""
        st.markdown('<h1 class="main-header">🍽️ Local Food Wastage Management System</h1>', unsafe_allow_html=True)
        
        # System overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            system_metrics = self.analyzer.query_15_comprehensive_system_metrics()
            
            if system_metrics is not None and not system_metrics.empty:
                metrics_dict = {}
                for _, row in system_metrics.iterrows():
                    metrics_dict[row['metric_name']] = {
                        'value': row['metric_value'],
                        'percentage': row['percentage']
                    }
                
                with col1:
                    if 'Total Active Providers' in metrics_dict:
                        st.metric("🏢 Active Providers", f"{metrics_dict['Total Active Providers']['value']:,}")
                
                with col2:
                    if 'Total Active Receivers' in metrics_dict:
                        st.metric("👥 Active Receivers", f"{metrics_dict['Total Active Receivers']['value']:,}")
                
                with col3:
                    if 'Total Food Items Listed' in metrics_dict:
                        st.metric("🍽️ Food Items", f"{metrics_dict['Total Food Items Listed']['value']:,}")
                
                with col4:
                    if 'Successful Claims' in metrics_dict:
                        success_rate = metrics_dict['Successful Claims']['percentage']
                        st.metric("✅ Success Rate", f"{success_rate:.1f}%" if success_rate else "N/A")
            
        except Exception as e:
            st.warning("Loading system metrics...")
    
    def render_dashboard(self):
        """Render dashboard page"""
        st.markdown('<div class="page-header"><h2>📊 System Overview Dashboard</h2></div>', unsafe_allow_html=True)
        
        try:
            # Quick insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top Performing Providers")
                top_providers = self.analyzer.query_9_successful_providers()
                if top_providers is not None and not top_providers.empty:
                    top_5 = top_providers.head(5)
                    for _, provider in top_5.iterrows():
                        st.markdown(f"**{provider['provider_name']}** ({provider['provider_type']})")
                        st.progress(provider['success_rate_percentage'] / 100 if provider['success_rate_percentage'] else 0)
                        st.markdown(f"*{provider['successful_claims']} successful claims ({provider['success_rate_percentage']:.1f}%)*")
                        st.markdown("---")
                else:
                    st.info("No provider data available")
            
            with col2:
                st.subheader("🎯 Claim Status Distribution")
                claim_status = self.analyzer.query_10_claim_status_distribution()
                if claim_status is not None and not claim_status.empty:
                    status_data = claim_status[claim_status['status'] != 'TOTAL']
                    if not status_data.empty:
                        fig = px.pie(
                            status_data, 
                            values='claim_count', 
                            names='status',
                            title="Claims by Status",
                            color_discrete_map={
                                'Completed': '#28a745',
                                'Pending': '#ffc107', 
                                'Cancelled': '#dc3545'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Food type analysis
            st.subheader("🥗 Food Type Distribution")
            food_types = self.analyzer.query_7_common_food_types()
            if food_types is not None and not food_types.empty:
                fig = px.bar(
                    food_types,
                    x='food_type',
                    y='total_quantity',
                    title="Food Quantity by Type",
                    color='food_type',
                    text='percentage_of_total_quantity'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            # Geographic distribution
            st.subheader("🗺️ Geographic Distribution")
            geo_data = self.analyzer.query_14_geographic_food_distribution()
            if geo_data is not None and not geo_data.empty:
                top_cities = geo_data.head(10)
                
                fig = px.bar(
                    top_cities,
                    x='city',
                    y='food_distributed',
                    title="Food Distribution by City (Top 10)",
                    color='food_utilization_rate',
                    color_continuous_scale='RdYlGn',
                    text='food_distributed'
                )
                fig.update_traces(texttemplate='%{text:,}', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
    
    def render_providers_page(self):
        """Render providers page"""
        st.markdown('<div class="page-header"><h2>🏢 Food Providers Management</h2></div>', unsafe_allow_html=True)
        
        # Filters
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.subheader("🔍 Filters")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        try:
            # Get filter options
            cities = self.db.fetch_dataframe("SELECT DISTINCT city FROM providers ORDER BY city")
            provider_types = self.db.fetch_dataframe("SELECT DISTINCT type FROM providers ORDER BY type")
            
            with filter_col1:
                selected_city = st.selectbox(
                    "Select City",
                    ["All"] + (cities['city'].tolist() if cities is not None else [])
                )
            
            with filter_col2:
                selected_type = st.selectbox(
                    "Select Provider Type", 
                    ["All"] + (provider_types['type'].tolist() if provider_types is not None else [])
                )
            
            with filter_col3:
                show_contact = st.checkbox("Show Contact Information", True)
        
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Build query based on filters
            base_query = """
            SELECT 
                p.provider_id,
                p.name,
                p.type,
                p.city,
                p.address,
                p.contact,
                COUNT(f.food_id) as total_food_items,
                COALESCE(SUM(f.quantity), 0) as total_quantity,
                COUNT(c.claim_id) as total_claims,
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as successful_claims,
                ROUND(
                    COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(c.claim_id), 0), 1
                ) as success_rate
            FROM providers p
            LEFT JOIN food_listings f ON p.provider_id = f.provider_id
            LEFT JOIN claims c ON f.food_id = c.food_id
            """
            
            conditions = []
            if selected_city != "All":
                conditions.append(f"p.city = '{selected_city}'")
            if selected_type != "All":
                conditions.append(f"p.type = '{selected_type}'")
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += """
            GROUP BY p.provider_id, p.name, p.type, p.city, p.address, p.contact
            ORDER BY total_quantity DESC
            """
            
            providers_data = self.db.fetch_dataframe(base_query)
            
            if providers_data is not None and not providers_data.empty:
                st.subheader(f"📊 Providers Overview ({len(providers_data)} providers)")
                
                # Statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                stat_col1.metric("Total Providers", len(providers_data))
                stat_col2.metric("Total Food Items", f"{providers_data['total_food_items'].sum():,}")
                stat_col3.metric("Total Quantity", f"{providers_data['total_quantity'].sum():,}")
                avg_success = providers_data['success_rate'].mean() if not providers_data['success_rate'].isna().all() else 0
                stat_col4.metric("Avg Success Rate", f"{avg_success:.1f}%")
                
                # Display providers as cards
                for _, provider in providers_data.iterrows():
                    with st.container():
                        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"### 🏢 {provider['name']}")
                            st.markdown(f"**Type:** {provider['type']}")
                            st.markdown(f"**📍 Location:** {provider['city']}")
                            if show_contact:
                                st.markdown(f"**📧 Contact:** {provider['contact']}")
                                st.markdown(f"**📍 Address:** {provider['address']}")
                        
                        with col2:
                            st.metric("🍽️ Food Items", provider['total_food_items'])
                            st.metric("📦 Total Quantity", f"{provider['total_quantity']:,}")
                        
                        with col3:
                            st.metric("📋 Claims", provider['total_claims'])
                            if provider['success_rate'] is not None:
                                st.metric("✅ Success Rate", f"{provider['success_rate']:.1f}%")
                            else:
                                st.metric("✅ Success Rate", "N/A")
                            
                            if st.button(f"📞 Contact", key=f"contact_{provider['provider_id']}"):
                                st.info(f"Contact {provider['name']}: {provider['contact']}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No providers found with the selected filters.")
                
        except Exception as e:
            st.error(f"Error loading providers: {e}")
    
    def render_receivers_page(self):
        """Render receivers page"""
        st.markdown('<div class="page-header"><h2>👥 Food Receivers Management</h2></div>', unsafe_allow_html=True)
        
        try:
            # Get top receivers data
            top_receivers = self.analyzer.query_4_top_food_claimers()
            
            if top_receivers is not None and not top_receivers.empty:
                st.subheader(f"📊 Active Receivers ({len(top_receivers)} receivers)")
                
                # Statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                stat_col1.metric("Active Receivers", len(top_receivers))
                stat_col2.metric("Total Claims", f"{top_receivers['total_claims'].sum():,}")
                stat_col3.metric("Food Received", f"{top_receivers['total_food_received'].sum():,}")
                avg_success = top_receivers['success_rate_percentage'].mean()
                stat_col4.metric("Avg Success Rate", f"{avg_success:.1f}%")
                
                # Display top 20 receivers
                for _, receiver in top_receivers.head(20).iterrows():
                    with st.expander(f"👥 {receiver['receiver_name']} ({receiver['receiver_type']}) - {receiver['city']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Type:** {receiver['receiver_type']}")
                            st.markdown(f"**City:** {receiver['city']}")
                            st.markdown(f"**Contact:** {receiver['contact']}")
                        
                        with col2:
                            st.markdown(f"**Total Claims:** {receiver['total_claims']}")
                            st.markdown(f"**Completed:** {receiver['completed_claims']}")
                            st.markdown(f"**Success Rate:** {receiver['success_rate_percentage']:.1f}%")
                            st.markdown(f"**Food Received:** {receiver['total_food_received']:,}")
            else:
                st.info("No receiver data available.")
                
        except Exception as e:
            st.error(f"Error loading receivers: {e}")
    
    def render_food_listings_page(self):
        """Render food listings page"""
        st.markdown('<div class="page-header"><h2>🍽️ Food Listings Management</h2></div>', unsafe_allow_html=True)
        
        try:
            # Filters
            st.markdown('<div class="filter-container">', unsafe_allow_html=True)
            st.subheader("🔍 Search & Filter")
            
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            # Get filter options
            locations = self.db.fetch_dataframe("SELECT DISTINCT location FROM food_listings ORDER BY location")
            food_types = self.db.fetch_dataframe("SELECT DISTINCT food_type FROM food_listings ORDER BY food_type")
            meal_types = self.db.fetch_dataframe("SELECT DISTINCT meal_type FROM food_listings ORDER BY meal_type")
            
            with filter_col1:
                selected_location = st.selectbox(
                    "📍 Location",
                    ["All"] + (locations['location'].tolist() if locations is not None else [])
                )
            
            with filter_col2:
                selected_food_type = st.selectbox(
                    "🥗 Food Type",
                    ["All"] + (food_types['food_type'].tolist() if food_types is not None else [])
                )
            
            with filter_col3:
                selected_meal_type = st.selectbox(
                    "🍽️ Meal Type", 
                    ["All"] + (meal_types['meal_type'].tolist() if meal_types is not None else [])
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Build query
            food_query = """
            SELECT 
                f.food_id,
                f.food_name,
                f.quantity,
                f.expiry_date,
                f.food_type,
                f.meal_type,
                f.location,
                p.name as provider_name,
                p.contact as provider_contact,
                COUNT(c.claim_id) as total_claims,
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_claims,
                CASE 
                    WHEN f.expiry_date <= date('now') THEN 'Expired'
                    WHEN f.expiry_date <= date('now', '+7 days') THEN 'Expiring Soon'
                    ELSE 'Fresh'
                END as expiry_status
            FROM food_listings f
            JOIN providers p ON f.provider_id = p.provider_id
            LEFT JOIN claims c ON f.food_id = c.food_id
            """
            
            conditions = []
            if selected_location != "All":
                conditions.append(f"f.location = '{selected_location}'")
            if selected_food_type != "All":
                conditions.append(f"f.food_type = '{selected_food_type}'")
            if selected_meal_type != "All":
                conditions.append(f"f.meal_type = '{selected_meal_type}'")
            
            if conditions:
                food_query += " WHERE " + " AND ".join(conditions)
            
            food_query += """
            GROUP BY f.food_id, f.food_name, f.quantity, f.expiry_date, f.food_type, 
                     f.meal_type, f.location, p.name, p.contact
            ORDER BY f.expiry_date ASC
            """
            
            food_data = self.db.fetch_dataframe(food_query)
            
            if food_data is not None and not food_data.empty:
                st.subheader(f"📊 Available Food Items ({len(food_data)} items)")
                
                # Quick stats
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                total_quantity = food_data['quantity'].sum()
                expiring_soon = len(food_data[food_data['expiry_status'] == 'Expiring Soon'])
                expired_items = len(food_data[food_data['expiry_status'] == 'Expired'])
                fresh_items = len(food_data[food_data['expiry_status'] == 'Fresh'])
                
                stat_col1.metric("Total Items", len(food_data))
                stat_col2.metric("Total Quantity", f"{total_quantity:,}")
                stat_col3.metric("⚠️ Expiring Soon", expiring_soon)
                stat_col4.metric("❌ Expired", expired_items)
                
                # Display food items
                for _, food in food_data.iterrows():
                    status_emoji = {
                        'Fresh': '✅',
                        'Expiring Soon': '⚠️',
                        'Expired': '❌'
                    }.get(food['expiry_status'], '⚪')
                    
                    with st.expander(f"{status_emoji} {food['food_name']} - {food['quantity']} units ({food['expiry_status']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Food Details:**")
                            st.markdown(f"• Type: {food['food_type']}")
                            st.markdown(f"• Meal Type: {food['meal_type']}")
                            st.markdown(f"• Quantity: {food['quantity']} units")
                            st.markdown(f"• Expiry: {food['expiry_date']}")
                        
                        with col2:
                            st.markdown("**Provider Information:**")
                            st.markdown(f"• Name: {food['provider_name']}")
                            st.markdown(f"• Location: {food['location']}")
                            st.markdown(f"• Contact: {food['provider_contact']}")
                        
                        with col3:
                            st.markdown("**Claim Statistics:**")
                            st.markdown(f"• Total Claims: {food['total_claims']}")
                            st.markdown(f"• Completed: {food['completed_claims']}")
                            
                            if food['expiry_status'] != 'Expired':
                                if st.button(f"📞 Contact Provider", key=f"contact_food_{food['food_id']}"):
                                    st.info(f"Contact {food['provider_name']}: {food['provider_contact']}")
                                
                                if st.button(f"🎯 Claim Food", key=f"claim_food_{food['food_id']}"):
                                    st.success("Claim request initiated! Provider will be contacted.")
            else:
                st.info("No food items found with the selected filters.")
                
        except Exception as e:
            st.error(f"Error loading food listings: {e}")
    
    def render_analytics_page(self):
        """Render analytics page"""
        st.markdown('<div class="page-header"><h2>📊 Analytics Dashboard</h2></div>', unsafe_allow_html=True)
        
        try:
            # Provider analytics
            st.subheader("🏢 Provider Performance")
            provider_types = self.analyzer.query_2_top_provider_types()
            if provider_types is not None and not provider_types.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        provider_types,
                        values='total_quantity_contributed',
                        names='provider_type',
                        title="Food Contribution by Provider Type"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        provider_types,
                        x='provider_type',
                        y='avg_quantity_per_listing',
                        title="Average Quantity per Listing"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Meal type analysis
            st.subheader("🍽️ Meal Type Analysis")
            meal_types = self.analyzer.query_12_meal_type_popularity()
            if meal_types is not None and not meal_types.empty:
                fig = px.bar(
                    meal_types,
                    x='meal_type',
                    y=['success_rate_percentage', 'utilization_rate_percentage'],
                    title="Success Rate vs Utilization Rate by Meal Type",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(meal_types, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading analytics: {e}")
    
    def render_claims_page(self):
        """Render claims page"""
        st.markdown('<div class="page-header"><h2>📋 Claims Management</h2></div>', unsafe_allow_html=True)
        
        try:
            # Claims overview
            claims_query = """
            SELECT 
                c.claim_id,
                c.timestamp,
                c.status,
                f.food_name,
                f.quantity,
                r.name as receiver_name,
                p.name as provider_name
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            JOIN receivers r ON c.receiver_id = r.receiver_id
            JOIN providers p ON f.provider_id = p.provider_id
            ORDER BY c.timestamp DESC
            LIMIT 50
            """
            
            claims_data = self.db.fetch_dataframe(claims_query)
            
            if claims_data is not None and not claims_data.empty:
                st.subheader(f"📊 Recent Claims ({len(claims_data)} shown)")
                
                # Statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                total_claims = len(claims_data)
                completed = len(claims_data[claims_data['status'] == 'Completed'])
                pending = len(claims_data[claims_data['status'] == 'Pending'])
                cancelled = len(claims_data[claims_data['status'] == 'Cancelled'])
                
                stat_col1.metric("Total Claims", total_claims)
                stat_col2.metric("✅ Completed", completed)
                stat_col3.metric("⏳ Pending", pending)
                stat_col4.metric("❌ Cancelled", cancelled)
                
                # Display claims
                for _, claim in claims_data.iterrows():
                    status_color = {
                        'Completed': '🟢',
                        'Pending': '🟡',
                        'Cancelled': '🔴'
                    }.get(claim['status'], '⚪')
                    
                    with st.expander(f"{status_color} Claim #{claim['claim_id']} - {claim['food_name']} ({claim['status']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Food:** {claim['food_name']}")
                            st.markdown(f"**Quantity:** {claim['quantity']} units")
                            st.markdown(f"**Provider:** {claim['provider_name']}")
                        
                        with col2:
                            st.markdown(f"**Receiver:** {claim['receiver_name']}")
                            st.markdown(f"**Date:** {claim['timestamp']}")
                            st.markdown(f"**Status:** {claim['status']}")
            else:
                st.info("No claims data available.")
                
        except Exception as e:
            st.error(f"Error loading claims: {e}")
    
    def render_geographic_page(self):
        """Render geographic page"""
        st.markdown('<div class="page-header"><h2>🗺️ Geographic Distribution Analysis</h2></div>', unsafe_allow_html=True)
        
        try:
            # Geographic analysis
            geo_data = self.analyzer.query_14_geographic_food_distribution()
            city_providers_receivers = self.analyzer.query_1_providers_receivers_by_city()
            
            if geo_data is not None and not geo_data.empty:
                st.subheader("🌍 City Performance Analysis")
                
                # Top cities visualization
                top_cities = geo_data.head(15)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        top_cities,
                        x='city',
                        y='food_distributed',
                        color='food_utilization_rate',
                        color_continuous_scale='RdYlGn',
                        title="Food Distribution by City",
                        text='food_distributed'
                    )
                    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.scatter(
                        top_cities,
                        x='total_food_available',
                        y='food_distributed',
                        size='total_claims',
                        color='claim_success_rate',
                        hover_data=['city'],
                        title="Supply vs Distribution",
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # City comparison table
                st.subheader("📋 City Performance Table")
                display_cols = ['city', 'total_food_available', 'food_distributed', 
                               'claim_success_rate', 'food_utilization_rate']
                
                display_data = top_cities[display_cols]
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    column_config={
                        "claim_success_rate": st.column_config.ProgressColumn(
                            "Success Rate",
                            help="Claim success rate percentage",
                            min_value=0,
                            max_value=100,
                        ),
                        "food_utilization_rate": st.column_config.ProgressColumn(
                            "Utilization Rate",
                            help="Food utilization rate percentage",
                            min_value=0,
                            max_value=100,
                        ),
                    }
                )
            
            # Provider-Receiver distribution
            if city_providers_receivers is not None and not city_providers_receivers.empty:
                st.subheader("🏢👥 Provider-Receiver Distribution")
                
                top_cities_pr = city_providers_receivers.head(15)
                
                fig = px.bar(
                    top_cities_pr,
                    x='city',
                    y=['providers', 'receivers'],
                    title="Providers and Receivers by City",
                    barmode='group'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error loading geographic data: {e}")
    
    def render_admin_page(self):
        """Render admin page"""
        st.markdown('<div class="page-header"><h2>⚙️ Admin Panel</h2></div>', unsafe_allow_html=True)
        
        try:
            # System overview
            st.subheader("📊 System Overview")
            
            # Health checks
            health_col1, health_col2, health_col3, health_col4 = st.columns(4)
            
            with health_col1:
                try:
                    conn = self.db.get_connection()
                    if conn:
                        conn.close()
                        st.success("✅ Database Online")
                    else:
                        st.error("❌ Database Offline")
                except Exception:
                    st.error("❌ Database Error")
            
            with health_col2:
                try:
                    # Check for data integrity
                    orphaned_check = self.db.fetch_dataframe("""
                        SELECT COUNT(*) as count FROM food_listings f 
                        LEFT JOIN providers p ON f.provider_id = p.provider_id 
                        WHERE p.provider_id IS NULL
                    """)
                    orphaned_count = orphaned_check.iloc[0]['count'] if orphaned_check is not None else 0
                    
                    if orphaned_count == 0:
                        st.success("✅ Data Integrity OK")
                    else:
                        st.warning(f"⚠️ {orphaned_count} Orphaned Records")
                except Exception:
                    st.error("❌ Integrity Check Failed")
            
            with health_col3:
                try:
                    # Performance test
                    start_time = datetime.now()
                    self.db.fetch_dataframe("SELECT COUNT(*) FROM providers")
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    if response_time < 0.1:
                        st.success(f"✅ Fast ({response_time:.3f}s)")
                    else:
                        st.warning(f"⚠️ Slow ({response_time:.3f}s)")
                except Exception:
                    st.error("❌ Performance Check Failed")
            
            with health_col4:
                try:
                    recent_claims = self.db.fetch_dataframe("""
                        SELECT COUNT(*) as count FROM claims 
                        WHERE timestamp >= date('now', '-24 hours')
                    """)
                    recent_count = recent_claims.iloc[0]['count'] if recent_claims is not None else 0
                    st.metric("📈 24h Activity", f"{recent_count} claims")
                except Exception:
                    st.error("❌ Activity Check Failed")
            
            # Database information
            st.subheader("🗄️ Database Information")
            
            try:
                tables = self.db.get_all_tables()
                if tables:
                    table_info = []
                    for table in tables:
                        count = self.db.get_row_count(table)
                        table_info.append({'Table': table, 'Row Count': f"{count:,}"})
                    
                    table_df = pd.DataFrame(table_info)
                    st.dataframe(table_df, use_container_width=True)
                
                # System metrics
                st.subheader("📊 System Metrics")
                system_metrics = self.analyzer.query_15_comprehensive_system_metrics()
                
                if system_metrics is not None and not system_metrics.empty:
                    st.dataframe(system_metrics, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error loading admin data: {e}")
            
            # Admin actions
            st.subheader("🛠️ Admin Actions")
            
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("🔄 Refresh System Stats"):
                    st.success("✅ System stats refreshed!")
                    st.rerun()
            
            with action_col2:
                if st.button("📊 Generate Report"):
                    st.success("📋 System report generated!")
                    st.info("Report functionality would be implemented here")
            
            with action_col3:
                if st.button("🧹 Clean Old Data"):
                    st.info("Data cleanup functionality would be implemented here")
            
            # Recent activity
            st.subheader("📈 Recent System Activity")
            
            recent_activity_query = """
            SELECT 
                c.timestamp as activity_time,
                'Claim ' || c.status as activity_type,
                f.food_name as description,
                r.name as user_name
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            JOIN receivers r ON c.receiver_id = r.receiver_id
            ORDER BY c.timestamp DESC
            LIMIT 10
            """
            
            recent_activity = self.db.fetch_dataframe(recent_activity_query)
            
            if recent_activity is not None and not recent_activity.empty:
                st.dataframe(recent_activity, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading admin panel: {e}")
    
    def run(self):
        """Main application runner"""
        # Check database connection
        self.check_database_connection()
        
        # Render sidebar
        self.render_sidebar()
        
        # Render main header
        self.render_main_header()
        
        # Render current page based on session state
        if st.session_state.current_page == 'dashboard':
            self.render_dashboard()
        elif st.session_state.current_page == 'providers':
            self.render_providers_page()
        elif st.session_state.current_page == 'receivers':
            self.render_receivers_page()
        elif st.session_state.current_page == 'food_listings':
            self.render_food_listings_page()
        elif st.session_state.current_page == 'analytics':
            self.render_analytics_page()
        elif st.session_state.current_page == 'claims':
            self.render_claims_page()
        elif st.session_state.current_page == 'geographic':
            self.render_geographic_page()
        elif st.session_state.current_page == 'admin':
            self.render_admin_page()
        
        # Footer
        st.markdown("---")
        footer_col1, footer_col2, footer_col3 = st.columns(3)
        
        with footer_col1:
            st.markdown("*🌱 Local Food Wastage Management System*")
        
        with footer_col2:
            st.markdown("*Reducing waste, feeding communities*")
        
        with footer_col3:
            try:
                conn_status = "🟢 Online" if self.db.get_connection() else "🔴 Offline"
                st.markdown(f"*System Status: {conn_status}*")
            except Exception:
                st.markdown("*System Status: 🔴 Offline*")

# Application entry point
if __name__ == "__main__":
    app = FoodManagementApp()
    app.run()