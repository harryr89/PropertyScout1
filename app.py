import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from utils.data_manager import DataManager
from utils.calculations import PropertyCalculator
from utils.scoring import PropertyScorer

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'property_calculator' not in st.session_state:
    st.session_state.property_calculator = PropertyCalculator()
if 'property_scorer' not in st.session_state:
    st.session_state.property_scorer = PropertyScorer()

# Page configuration
st.set_page_config(
    page_title="Property Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main dashboard
st.title("🏠 Property Analytics Dashboard")
st.markdown("---")

# Sidebar with navigation info
st.sidebar.title("Navigation")
st.sidebar.markdown("""
**Available Pages:**
- 🏠 **Dashboard** (Current)
- 📊 **Property Input** - Add and manage properties
- 💰 **Financial Calculator** - Calculate key metrics
- 🔍 **Deal Comparison** - Compare investment opportunities
- 📈 **Market Analysis** - Analyze market trends
- 📊 **Performance Tracking** - Track investment performance
""")

# Get current data
properties_df = st.session_state.data_manager.get_properties()

# Dashboard metrics
if not properties_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_properties = len(properties_df)
        st.metric("Total Properties", total_properties)
    
    with col2:
        avg_price = properties_df['price'].mean()
        st.metric("Average Price", f"${avg_price:,.0f}")
    
    with col3:
        if 'roi' in properties_df.columns:
            avg_roi = properties_df['roi'].mean()
            st.metric("Average ROI", f"{avg_roi:.1f}%")
        else:
            st.metric("Average ROI", "N/A")
    
    with col4:
        if 'cap_rate' in properties_df.columns:
            avg_cap_rate = properties_df['cap_rate'].mean()
            st.metric("Average Cap Rate", f"{avg_cap_rate:.1f}%")
        else:
            st.metric("Average Cap Rate", "N/A")
    
    st.markdown("---")
    
    # Property distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Property Types Distribution")
        if 'property_type' in properties_df.columns:
            type_counts = properties_df['property_type'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index, 
                        title="Properties by Type")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No property type data available")
    
    with col2:
        st.subheader("Price Distribution")
        fig = px.histogram(properties_df, x='price', nbins=20, 
                          title="Property Price Distribution")
        fig.update_layout(xaxis_title="Price ($)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent properties table
    st.subheader("Recent Properties")
    if len(properties_df) > 0:
        recent_properties = properties_df.tail(10)
        st.dataframe(recent_properties, use_container_width=True)
    else:
        st.info("No properties added yet")
    
    # Top performing properties
    if 'roi' in properties_df.columns:
        st.subheader("Top Performing Properties (by ROI)")
        top_properties = properties_df.nlargest(5, 'roi')[['address', 'price', 'roi', 'cap_rate']]
        st.dataframe(top_properties, use_container_width=True)

else:
    st.info("🏠 No properties in your portfolio yet!")
    st.markdown("""
    ### Get Started:
    1. Navigate to **Property Input** to add your first property
    2. Use the **Financial Calculator** to analyze deals
    3. Compare properties in **Deal Comparison**
    4. Track performance over time
    """)
    
    # Sample workflow
    st.markdown("---")
    st.subheader("Quick Start Guide")
    
    with st.expander("🔍 How to Analyze a Property Deal"):
        st.markdown("""
        1. **Add Property Details**: Go to Property Input and enter basic information
        2. **Financial Analysis**: Use the Financial Calculator to compute ROI, cap rate, and cash flow
        3. **Compare Options**: Use Deal Comparison to evaluate multiple properties
        4. **Market Context**: Check Market Analysis for trends and benchmarks
        5. **Track Performance**: Monitor your investments over time
        """)
    
    with st.expander("📊 Key Metrics Explained"):
        st.markdown("""
        - **ROI (Return on Investment)**: Annual return as percentage of initial investment
        - **Cap Rate (Capitalization Rate)**: Net operating income divided by property price
        - **Cash Flow**: Monthly income after all expenses
        - **Cash-on-Cash Return**: Annual cash flow divided by initial cash investment
        - **DSCR (Debt Service Coverage Ratio)**: NOI divided by annual debt payments
        """)

# Footer
st.markdown("---")
st.markdown("*Property Analytics Dashboard - Built with Streamlit*")
