"""
Main Streamlit Application for Local Food Wastage Management System
FIXED VERSION - All syntax errors resolved
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.database.connection import DatabaseManager
from src.analysis.sql_queries import FoodWastageAnalyzer
from config.settings import STREAMLIT_CONFIG

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
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
    }
    .metric-container {
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .contact-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class FoodManagementApp:
    """Main Streamlit Application Class"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analyzer = FoodWastageAnalyzer()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'Dashboard'
        if 'filters' not in st.session_state:
            st.session_state.filters = {}
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
    
    def check_database_connection(self):
        """Check database connection and show status"""
        try:
            conn = self.db.get_connection()
            if conn is None:
                st.error("❌ Database connection failed! Please check your database setup.")
                st.stop()
            conn.close()
            return True
        except Exception as e:
            st.error(f"❌ Database error: {e}")
            st.stop()
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        st.sidebar.markdown("## 🍽️ Navigation")
        
        pages = {
            "🏠 Dashboard": "dashboard",
            "🏢 Providers": "providers", 
            "👥 Receivers": "receivers",
            "🍽️ Food Listings": "food_listings",
            "📊 Analytics": "analytics",
            "📋 Claims": "claims",
            "🗺️ Geographic View": "geographic",
            "⚙️ Admin Panel": "admin"
        }
        
        # Page selection
        selected_page = st.sidebar.selectbox(
            "Select Page",
            list(pages.keys()),
            index=0
        )
        
        st.session_state.current_page = pages[selected_page]
        
        # Database status
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 System Status")
        
        try:
            # Get basic system metrics
            total_providers = self.db.get_row_count('providers')
            total_receivers = self.db.get_row_count('receivers')
            total_food_items = self.db.get_row_count('food_listings')
            total_claims = self.db.get_row_count('claims')
            
            st.sidebar.metric("Providers", f"{total_providers:,}")
            st.sidebar.metric("Receivers", f"{total_receivers:,}")
            st.sidebar.metric("Food Items", f"{total_food_items:,}")
            st.sidebar.metric("Claims", f"{total_claims:,}")
            
        except Exception as e:
            st.sidebar.error(f"Error loading metrics: {e}")
        
        # Refresh button
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Refresh Data"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        st.sidebar.markdown(f"*Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}*")
    
    def render_main_header(self):
        """Render the main application header"""
        st.markdown('<h1 class="main-header">🍽️ Local Food Wastage Management System</h1>', unsafe_allow_html=True)
        
        # System overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            # Get system metrics
            system_metrics = self.analyzer.query_15_comprehensive_system_metrics()
            
            if system_metrics is not None and not system_metrics.empty:
                for _, row in system_metrics.iterrows():
                    if row['metric_name'] == 'Total Active Providers':
                        col1.metric("🏢 Active Providers", f"{row['metric_value']:,}")
                    elif row['metric_name'] == 'Total Active Receivers':
                        col2.metric("👥 Active Receivers", f"{row['metric_value']:,}")
                    elif row['metric_name'] == 'Total Food Items Listed':
                        col3.metric("🍽️ Food Items", f"{row['metric_value']:,}")
                    elif row['metric_name'] == 'Successful Claims':
                        col4.metric("✅ Success Rate", f"{row['percentage']:.1f}%" if row['percentage'] else "N/A")
            
        except Exception as e:
            st.warning(f"Could not load system metrics: {e}")
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.header("📊 System Overview Dashboard")
        
        # Quick insights
        try:
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                st.subheader("🏆 Top Performing Providers")
                top_providers = self.analyzer.query_9_successful_providers()
                if top_providers is not None and not top_providers.empty:
                    top_5 = top_providers.head(5)[['provider_name', 'provider_type', 'successful_claims', 'success_rate_percentage']]
                    st.dataframe(top_5, use_container_width=True)
                else:
                    st.info("No provider data available")
            
            with insights_col2:
                st.subheader("🎯 Claim Status Distribution")
                claim_status = self.analyzer.query_10_claim_status_distribution()
                if claim_status is not None and not claim_status.empty:
                    # Filter out TOTAL row for pie chart
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
            
            # Food type distribution
            st.subheader("🥗 Food Type Analysis")
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
        """Render the providers management page"""
        st.header("🏢 Food Providers Management")
        
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
                COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as successful_claims
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
                
                # Display options
                display_cols = ['name', 'type', 'city', 'total_food_items', 'total_quantity', 'total_claims', 'successful_claims']
                if show_contact:
                    display_cols.insert(3, 'contact')
                    display_cols.insert(3, 'address')
                
                # Format the dataframe for display
                display_df = providers_data[display_cols].copy()
                
                st.dataframe(display_df, use_container_width=True)
                
                # Provider statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                stat_col1.metric("Total Providers", len(providers_data))
                stat_col2.metric("Total Food Items", f"{providers_data['total_food_items'].sum():,}")
                stat_col3.metric("Total Quantity", f"{providers_data['total_quantity'].sum():,}")
                stat_col4.metric("Avg Success Rate", f"{(providers_data['successful_claims'].sum() / max(providers_data['total_claims'].sum(), 1) * 100):.1f}%")
                
                # Contact information section
                if show_contact:
                    st.subheader("📞 Provider Contact Directory")
                    
                    for _, provider in providers_data.iterrows():
                        with st.expander(f"📧 {provider['name']} ({provider['type']})"):
                            st.markdown(f"**Address:** {provider['address']}")
                            st.markdown(f"**City:** {provider['city']}")
                            st.markdown(f"**Contact:** {provider['contact']}")
                            st.markdown(f"**Food Items Listed:** {provider['total_food_items']}")
                            st.markdown(f"**Total Quantity:** {provider['total_quantity']:,}")
                            if provider['total_claims'] > 0:
                                success_rate = (provider['successful_claims'] / provider['total_claims']) * 100
                                st.markdown(f"**Success Rate:** {success_rate:.1f}% ({provider['successful_claims']}/{provider['total_claims']})")
            else:
                st.info("No providers found with the selected filters.")
        
        except Exception as e:
            st.error(f"Error loading providers: {e}")
    
    def render_receivers_page(self):
        """Render the receivers management page"""
        st.header("👥 Food Receivers Management")
        
        # Filters
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.subheader("🔍 Filters")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        try:
            # Get filter options
            cities = self.db.fetch_dataframe("SELECT DISTINCT city FROM receivers ORDER BY city")
            receiver_types = self.db.fetch_dataframe("SELECT DISTINCT type FROM receivers ORDER BY type")
            
            with filter_col1:
                selected_city = st.selectbox(
                    "Select City",
                    ["All"] + (cities['city'].tolist() if cities is not None else [])
                )
            
            with filter_col2:
                selected_type = st.selectbox(
                    "Select Receiver Type",
                    ["All"] + (receiver_types['type'].tolist() if receiver_types is not None else [])
                )
            
            with filter_col3:
                min_claims = st.number_input("Minimum Claims", min_value=0, value=0)
        
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Get top receivers data
            top_receivers = self.analyzer.query_4_top_food_claimers()
            
            if top_receivers is not None and not top_receivers.empty:
                # Apply filters
                filtered_data = top_receivers.copy()
                
                if selected_city != "All":
                    filtered_data = filtered_data[filtered_data['city'] == selected_city]
                if selected_type != "All":
                    filtered_data = filtered_data[filtered_data['receiver_type'] == selected_type]
                if min_claims > 0:
                    filtered_data = filtered_data[filtered_data['total_claims'] >= min_claims]
                
                st.subheader(f"📊 Active Receivers ({len(filtered_data)} receivers)")
                
                if not filtered_data.empty:
                    # Display data
                    display_cols = ['receiver_name', 'receiver_type', 'city', 'total_claims', 'completed_claims', 
                                   'success_rate_percentage', 'total_food_received']
                    
                    st.dataframe(
                        filtered_data[display_cols],
                        use_container_width=True,
                        column_config={
                            "success_rate_percentage": st.column_config.ProgressColumn(
                                "Success Rate %",
                                help="Percentage of successful claims",
                                min_value=0,
                                max_value=100,
                            ),
                        }
                    )
                    
                    # Statistics
                    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                    
                    stat_col1.metric("Active Receivers", len(filtered_data))
                    stat_col2.metric("Total Claims", f"{filtered_data['total_claims'].sum():,}")
                    stat_col3.metric("Food Received", f"{filtered_data['total_food_received'].sum():,}")
                    avg_success = filtered_data['success_rate_percentage'].mean()
                    stat_col4.metric("Avg Success Rate", f"{avg_success:.1f}%")
                    
                    # Top performers visualization
                    st.subheader("🏆 Top 10 Receivers by Food Received")
                    top_10 = filtered_data.head(10)
                    
                    fig = px.bar(
                        top_10,
                        x='receiver_name',
                        y='total_food_received',
                        color='success_rate_percentage',
                        color_continuous_scale='RdYlGn',
                        title="Food Received by Top Receivers",
                        text='total_food_received'
                    )
                    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Contact information
                    st.subheader("📞 Receiver Contact Information")
                    
                    for _, receiver in filtered_data.head(20).iterrows():
                        with st.expander(f"📧 {receiver['receiver_name']} ({receiver['receiver_type']})"):
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
                    st.info("No receivers found with the selected filters.")
            else:
                st.info("No receiver data available.")
                
        except Exception as e:
            st.error(f"Error loading receivers: {e}")
    
    # Placeholder methods for other pages
    def render_food_listings_page(self):
        st.info("🚧 Food Listings page is under development. Coming soon!")
    
    def render_analytics_page(self):
        st.info("🚧 Analytics page is under development. Coming soon!")
    
    def render_claims_page(self):
        st.info("🚧 Claims page is under development. Coming soon!")
    
    def render_geographic_page(self):
        st.info("🚧 Geographic page is under development. Coming soon!")
    
    def render_admin_page(self):
        st.info("🚧 Admin page is under development. Coming soon!")
    
    def run(self):
        """Main application runner"""
        # Check database connection
        self.check_database_connection()
        
        # Render sidebar
        self.render_sidebar()
        
        # Render main header
        self.render_main_header()
        
        # Render current page
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
        st.markdown("*Local Food Wastage Management System - Reducing waste, feeding communities* 🌱")

# Application entry point
if __name__ == "__main__":
    app = FoodManagementApp()
    app.run()