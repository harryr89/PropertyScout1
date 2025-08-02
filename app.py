import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Property Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

if 'property_calculator' not in st.session_state:
    from utils.calculations import PropertyCalculator
    st.session_state.property_calculator = PropertyCalculator()

if 'property_scorer' not in st.session_state:
    from utils.scoring import PropertyScorer
    st.session_state.property_scorer = PropertyScorer()

# Cache data retrieval for better performance
@st.cache_data
def get_cached_properties():
    """Cached method to retrieve properties data for better performance"""
    return st.session_state.data_manager.get_properties()

# Main title and description
st.title("🏠 Property Analytics Dashboard")
st.markdown("**Comprehensive UK Property Investment Analysis Platform**")
st.markdown("Analyze, compare, and track your UK property investment portfolio with real-time market data and advanced analytics.")

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
st.sidebar.markdown("---")

# Quick stats in sidebar with error handling
properties_df = get_cached_properties()

if not properties_df.empty:
    st.sidebar.subheader("📊 Portfolio Summary")
    
    try:
        # Basic validation - ensure price column is numeric
        if 'price' in properties_df.columns:
            properties_df['price'] = pd.to_numeric(properties_df['price'], errors='coerce')
        
        total_properties = len(properties_df)
        total_value = properties_df['price'].sum() if 'price' in properties_df.columns else 0
        avg_price = properties_df['price'].mean() if 'price' in properties_df.columns else 0
        total_monthly_rent = properties_df['monthly_rent'].sum() if 'monthly_rent' in properties_df.columns else 0
        
        st.sidebar.metric("Total Properties", total_properties)
        st.sidebar.metric("Portfolio Value", f"£{total_value:,.0f}" if total_value > 0 else "N/A")
        st.sidebar.metric("Average Property Price", f"£{avg_price:,.0f}" if avg_price > 0 else "N/A")
        st.sidebar.metric("Monthly Rental Income", f"£{total_monthly_rent:,.0f}" if total_monthly_rent > 0 else "N/A")
        
        # Calculate portfolio metrics with error handling
        portfolio_roi = 0
        portfolio_cap_rate = 0
        
        try:
            for _, prop in properties_df.iterrows():
                metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                portfolio_roi += metrics.get('roi', 0)
                portfolio_cap_rate += metrics.get('cap_rate', 0)
            
            if total_properties > 0:
                avg_roi = portfolio_roi / total_properties
                avg_cap_rate = portfolio_cap_rate / total_properties
                
                st.sidebar.metric("Average ROI", f"{avg_roi:.1f}%" if avg_roi > 0 else "N/A")
                st.sidebar.metric("Average Cap Rate", f"{avg_cap_rate:.1f}%" if avg_cap_rate > 0 else "N/A")
        except (ValueError, KeyError, ZeroDivisionError):
            st.sidebar.metric("Average ROI", "N/A")
            st.sidebar.metric("Average Cap Rate", "N/A")
            
    except Exception as e:
        st.sidebar.warning("Error calculating portfolio metrics")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Quick Links")
st.sidebar.page_link("pages/1_Property_Input.py", label="➕ Add Properties")
st.sidebar.page_link("pages/2_Financial_Calculator.py", label="🧮 Financial Calculator")
st.sidebar.page_link("pages/3_Deal_Comparison.py", label="⚖️ Compare Deals")
st.sidebar.page_link("pages/4_Market_Analysis.py", label="📈 Market Analysis")
st.sidebar.page_link("pages/5_Performance_Tracking.py", label="📊 Performance Tracking")
st.sidebar.page_link("pages/6_Live_Property_Search.py", label="🔍 Live Property Search")

# Main content area
if properties_df.empty:
    # Empty state with guidance
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; border: 2px dashed #cccccc; border-radius: 10px; background-color: #f8f9fa;">
        <h3>🚀 Welcome to Your Property Analytics Dashboard</h3>
        <p style="font-size: 1.1em; color: #666;">
        Get started by adding your first property to begin analyzing your UK investment portfolio.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Quick Start Guide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📋 Input Your Properties**
            - Add property details manually
            - Import from CSV files
            - Search live UK property data
            """)
            
            st.markdown("""
            **📊 Analyze Performance**
            - Calculate ROI and Cap Rates
            - Track performance over time
            - Compare multiple properties
            """)
        
        with col2:
            st.markdown("""
            **📈 Market Analysis**
            - View market trends
            - Benchmark against comparables
            - Forecast future performance
            """)
            
            st.markdown("""
            **🔍 Find New Deals**
            - Search live UK property listings
            - Analyze investment potential
            - Import promising opportunities
            """)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add Your First Property", use_container_width=True):
                st.switch_page("pages/1_Property_Input.py")
        
        with col2:
            if st.button("🔍 Search UK Properties", use_container_width=True):
                st.switch_page("pages/6_Live_Property_Search.py")
        
        with col3:
            if st.button("🧮 Financial Calculator", use_container_width=True):
                st.switch_page("pages/2_Financial_Calculator.py")
        
        st.markdown("---")
        
        # Benefits section
        st.markdown("### 🏆 Platform Benefits")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 Investment Focus**
            - UK-specific property analysis
            - British pound calculations
            - Local market insights
            """)
        
        with col2:
            st.markdown("""
            **📊 Advanced Analytics**
            - Comprehensive financial metrics
            - Performance tracking
            - Risk assessment tools
            """)
        
        with col3:
            st.markdown("""
            **🔄 Live Data Integration**
            - Real-time property listings
            - Market trend analysis
            - Automated deal sourcing
            """)

else:
    # Dashboard with data
    st.markdown("---")
    
    # Enhanced main metrics row with error handling
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        total_properties = len(properties_df)
        st.metric("Total Properties", total_properties)
    
    with col2:
        try:
            total_value = properties_df['price'].sum() if 'price' in properties_df.columns else 0
            st.metric("Portfolio Value", f"£{total_value:,.0f}" if total_value > 0 else "N/A")
        except (ValueError, KeyError):
            st.metric("Portfolio Value", "N/A")
    
    with col3:
        try:
            avg_monthly_rent = properties_df['monthly_rent'].mean() if 'monthly_rent' in properties_df.columns else 0
            st.metric("Avg Monthly Rent", f"£{avg_monthly_rent:,.0f}" if avg_monthly_rent > 0 else "N/A")
        except (ValueError, KeyError):
            st.metric("Avg Monthly Rent", "N/A")
    
    with col4:
        try:
            total_monthly_income = properties_df['monthly_rent'].sum() if 'monthly_rent' in properties_df.columns else 0
            st.metric("Total Monthly Income", f"£{total_monthly_income:,.0f}" if total_monthly_income > 0 else "N/A")
        except (ValueError, KeyError):
            st.metric("Total Monthly Income", "N/A")
    
    # Additional metrics: Average Cash-on-Cash Return and Total Portfolio Value
    with col5:
        try:
            # Calculate average cash-on-cash return using PropertyCalculator
            cash_on_cash_returns = []
            for _, prop in properties_df.iterrows():
                metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                coc_return = metrics.get('cash_on_cash_return', 0)
                if coc_return > 0:
                    cash_on_cash_returns.append(coc_return)
            
            avg_coc = sum(cash_on_cash_returns) / len(cash_on_cash_returns) if cash_on_cash_returns else 0
            st.metric("Avg Cash-on-Cash", f"{avg_coc:.1f}%" if avg_coc > 0 else "N/A")
        except (ValueError, KeyError, ZeroDivisionError):
            st.metric("Avg Cash-on-Cash", "N/A")
    
    with col6:
        try:
            # Total portfolio value (same as col2 but for consistency)
            total_portfolio_value = properties_df['price'].sum() if 'price' in properties_df.columns else 0
            st.metric("Total Portfolio Value", f"£{total_portfolio_value:,.0f}" if total_portfolio_value > 0 else "N/A")
        except (ValueError, KeyError):
            st.metric("Total Portfolio Value", "N/A")
    
    # Property type filter above charts
    st.markdown("---")
    
    # Filters section
    if 'property_type' in properties_df.columns:
        property_types = properties_df['property_type'].unique().tolist()
        selected_types = st.multiselect(
            "Filter by Property Type:",
            property_types,
            default=property_types,
            help="Select property types to include in charts and analysis"
        )
        
        # Apply filter to dataframe
        filtered_df = properties_df[properties_df['property_type'].isin(selected_types)] if selected_types else properties_df
    else:
        filtered_df = properties_df
        st.info("Property type data not available for filtering")
    
    # Charts and analysis
    st.subheader("📈 Portfolio Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Property value distribution with error handling
        try:
            if 'price' in filtered_df.columns and not filtered_df.empty:
                fig = px.histogram(
                    filtered_df, 
                    x='price', 
                    nbins=20,
                    title="Property Value Distribution",
                    labels={'price': 'Property Price (£)', 'count': 'Number of Properties'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Price data not available for visualization")
        except Exception as e:
            st.error("Error creating property value distribution chart")
    
    with col2:
        # Property type distribution with error handling
        try:
            if 'property_type' in filtered_df.columns and not filtered_df.empty:
                fig = px.pie(
                    filtered_df, 
                    names='property_type',
                    title="Property Type Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback chart if property_type not available
                if 'monthly_rent' in filtered_df.columns and not filtered_df.empty:
                    fig = px.bar(
                        filtered_df,
                        x='address',
                        y='monthly_rent',
                        title="Monthly Rent by Property"
                    )
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Property type or rent data not available for visualization")
        except Exception as e:
            st.error("Error creating property type distribution chart")
    
    # New visualization: ROI vs Price Scatter Plot
    st.markdown("---")
    try:
        # Calculate ROI for each property
        roi_data = []
        for _, prop in filtered_df.iterrows():
            try:
                metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                roi_data.append({
                    'address': prop.get('address', 'Unknown'),
                    'price': prop.get('price', 0),
                    'roi': metrics.get('roi', 0),
                    'property_type': prop.get('property_type', 'Unknown')
                })
            except Exception:
                continue
        
        if roi_data:
            roi_df = pd.DataFrame(roi_data)
            fig = px.scatter(
                roi_df,
                x='price',
                y='roi',
                color='property_type' if 'property_type' in roi_df.columns else None,
                title="ROI vs Price Scatter",
                labels={'price': 'Property Price (£)', 'roi': 'ROI (%)'},
                hover_data=['address']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Unable to calculate ROI data for scatter plot")
    except Exception as e:
        st.error("Error creating ROI vs Price scatter plot")
    
    # Recent properties table
    st.markdown("---")
    st.subheader("🏠 Recent Properties")
    
    # Show last 5 properties from filtered data
    recent_properties = filtered_df.tail(5) if not filtered_df.empty else pd.DataFrame()
    
    if not recent_properties.empty:
        display_columns = ['address', 'property_type', 'price', 'monthly_rent', 'bedrooms']
        available_columns = [col for col in display_columns if col in recent_properties.columns]
        
        if available_columns:
            display_data = recent_properties[available_columns].copy()
            
            # Format price and rent columns for better display
            if 'price' in display_data.columns:
                try:
                    display_data['price'] = display_data['price'].apply(lambda x: f"£{x:,.0f}" if pd.notnull(x) else "N/A")
                except:
                    pass
            
            if 'monthly_rent' in display_data.columns:
                try:
                    display_data['monthly_rent'] = display_data['monthly_rent'].apply(lambda x: f"£{x:,.0f}" if pd.notnull(x) else "N/A")
                except:
                    pass
            
            st.dataframe(display_data, use_container_width=True)
        else:
            st.dataframe(recent_properties, use_container_width=True)
    else:
        st.info("No properties match the current filter selection")
    
    # Data export functionality
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if not filtered_df.empty:
            # Convert dataframe to CSV for download
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Export Properties as CSV",
                data=csv_data,
                file_name=f"property_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No data available for export")
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add New Property", use_container_width=True):
            st.switch_page("pages/1_Property_Input.py")
    
    with col2:
        if st.button("⚖️ Compare Properties", use_container_width=True):
            st.switch_page("pages/3_Deal_Comparison.py")
    
    with col3:
        if st.button("📊 View Performance", use_container_width=True):
            st.switch_page("pages/5_Performance_Tracking.py")
    
    with col4:
        if st.button("🔍 Search New Deals", use_container_width=True):
            st.switch_page("pages/6_Live_Property_Search.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
🏠 Property Analytics Dashboard | Built for UK Property Investors | 
<a href="https://replit.com" target="_blank">Powered by Replit</a>
</div>
""", unsafe_allow_html=True)