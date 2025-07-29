import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="Live Property Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Live Property Search & Import")
st.markdown("Search real estate listings from multiple sources and import them for analysis.")

# Initialize session state
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

if 'property_calculator' not in st.session_state:
    from utils.calculations import PropertyCalculator
    st.session_state.property_calculator = PropertyCalculator()

from utils.property_data_sources import PropertyDataSources

# Initialize property data sources
if 'property_sources' not in st.session_state:
    st.session_state.property_sources = PropertyDataSources()

# Check API availability
api_status = st.session_state.property_sources.check_api_availability()

# Display API status
st.sidebar.markdown("### API Status")
for api_name, is_available in api_status.items():
    status_icon = "✅" if is_available else "❌"
    st.sidebar.markdown(f"{status_icon} {api_name}")

if not any(api_status.values()):
    st.warning("⚠️ No API keys configured. You'll need API keys to access live property data.")
    
    with st.expander("🔧 How to Set Up API Keys"):
        st.markdown("""
        To access live UK property data, you need API keys from UK property data providers:
        
        **Available UK Data Sources:**
        1. **Rightmove API** - UK's largest property portal
        2. **Zoopla API** - Comprehensive UK property listings and valuations
        3. **OnTheMarket API** - Independent UK property platform
        4. **PropertyData API** - UK property investment data and analytics
        5. **Land Registry API** - Official UK property transaction data
        
        **Setup Instructions:**
        1. Sign up for API access with one or more UK providers
        2. Get your API key from their developer portal
        3. Add it as a secret in your environment
        
        **Environment Variables Needed:**
        - `RIGHTMOVE_API_KEY`
        - `ZOOPLA_API_KEY` 
        - `ONTHEMARKET_API_KEY`
        - `PROPERTYDATA_API_KEY`
        - `LAND_REGISTRY_API_KEY`
        """)

# Tabs for different search options
tab1, tab2, tab3 = st.tabs(["Property Search", "Search Results", "Saved Searches"])

with tab1:
    st.subheader("🔍 Search Properties")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Search Parameters**")
        search_location = st.text_input(
            "Location (City, County)", 
            placeholder="Manchester, Greater Manchester",
            help="Enter UK city and county separated by comma"
        )
        
        property_type = st.selectbox(
            "Property Type",
            ["All Types", "Terraced House", "Semi-Detached", "Detached", "Flat/Apartment", "Bungalow", "Commercial"]
        )
        
        max_results = st.slider("Maximum Results per Source", 10, 100, 25, 5)
        
    with col2:
        st.markdown("**Price Range**")
        price_min = st.number_input("Minimum Price ($)", min_value=0, value=0, step=10000)
        price_max = st.number_input("Maximum Price ($)", min_value=0, value=1000000, step=10000)
        
        st.markdown("**Property Size**")
        min_bedrooms = st.selectbox("Minimum Bedrooms", [0, 1, 2, 3, 4, 5], index=0)
        min_sqft = st.number_input("Minimum Square Feet", min_value=0, value=0, step=100)
    
    # Search button
    if st.button("🔍 Search Properties", type="primary"):
        if search_location:
            with st.spinner("Searching property databases..."):
                # Search all available sources
                search_results = st.session_state.property_sources.search_all_sources(
                    location=search_location,
                    max_results_per_source=max_results
                )
                
                if search_results:
                    # Filter results based on criteria
                    filtered_results = []
                    for prop in search_results:
                        # Price filter
                        if price_min > 0 and prop.get('price', 0) < price_min:
                            continue
                        if price_max > 0 and prop.get('price', 0) > price_max:
                            continue
                        
                        # Bedroom filter
                        if prop.get('bedrooms', 0) < min_bedrooms:
                            continue
                        
                        # Square footage filter
                        if min_sqft > 0 and prop.get('square_feet', 0) < min_sqft:
                            continue
                        
                        # Property type filter
                        if property_type != "All Types" and prop.get('property_type', '') != property_type:
                            continue
                        
                        filtered_results.append(prop)
                    
                    # Store results in session state
                    st.session_state.search_results = filtered_results
                    st.session_state.search_timestamp = datetime.now()
                    
                    st.success(f"Found {len(filtered_results)} properties matching your criteria!")
                    
                    if len(filtered_results) != len(search_results):
                        st.info(f"Filtered from {len(search_results)} total results")
                else:
                    st.error("No properties found. Please check your search criteria or API configuration.")
        else:
            st.error("Please enter a search location.")

with tab2:
    st.subheader("📋 Search Results")
    
    if 'search_results' in st.session_state and st.session_state.search_results:
        results = st.session_state.search_results
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Properties", len(results))
        
        with col2:
            avg_price = sum(p.get('price', 0) for p in results) / len(results) if results else 0
            st.metric("Average Price", f"£{avg_price:,.0f}")
        
        with col3:
            sources = set(p.get('source', 'Unknown') for p in results)
            st.metric("Data Sources", len(sources))
        
        with col4:
            avg_rent = sum(p.get('monthly_rent', 0) for p in results) / len(results) if results else 0
            st.metric("Average Rent", f"£{avg_rent:,.0f}")
        
        # Display properties
        st.markdown("---")
        
        # Selection controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Select Properties to Import**")
        
        with col2:
            if st.button("📥 Import All Selected", type="primary"):
                selected_properties = []
                for i, prop in enumerate(results):
                    if st.session_state.get(f"select_prop_{i}", False):
                        selected_properties.append(prop)
                
                if selected_properties:
                    added_count = st.session_state.property_sources.save_properties_to_portfolio(
                        selected_properties, 
                        st.session_state.data_manager
                    )
                    st.success(f"Successfully imported {added_count} properties to your portfolio!")
                    st.rerun()
                else:
                    st.warning("Please select at least one property to import.")
        
        # Property cards
        for i, prop in enumerate(results):
            with st.expander(f"🏠 {prop.get('address', 'Unknown Address')} - £{prop.get('price', 0):,.0f}"):
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    # Selection checkbox
                    st.checkbox(
                        "Select for import",
                        key=f"select_prop_{i}",
                        value=False
                    )
                    
                    # Property image placeholder
                    st.markdown("📷 *Image placeholder*")
                
                with col2:
                    # Property details
                    st.markdown(f"**Address:** {prop.get('address', 'N/A')}")
                    st.markdown(f"**Type:** {prop.get('property_type', 'N/A')}")
                    st.markdown(f"**Price:** £{prop.get('price', 0):,.0f}")
                    st.markdown(f"**Monthly Rent:** £{prop.get('monthly_rent', 0):,.0f}/month")
                    st.markdown(f"**Bedrooms:** {prop.get('bedrooms', 'N/A')}")
                    st.markdown(f"**Bathrooms:** {prop.get('bathrooms', 'N/A')}")
                    st.markdown(f"**Square Feet:** {prop.get('square_feet', 'N/A'):,}")
                    st.markdown(f"**Postcode:** {prop.get('postcode', 'N/A')}")
                    st.markdown(f"**Tenure:** {prop.get('tenure', 'N/A')}")
                    st.markdown(f"**Source:** {prop.get('source', 'N/A')}")
                
                with col3:
                    # Quick analysis
                    if prop.get('price', 0) > 0:
                        # Calculate quick metrics
                        price = prop.get('price', 0)
                        monthly_rent = prop.get('monthly_rent', 0)
                        
                        if monthly_rent > 0:
                            # UK rental yield calculation
                            annual_rent = monthly_rent * 12
                            gross_yield = (annual_rent / price) * 100 if price > 0 else 0
                            
                            # UK specific metrics
                            st.markdown("**Quick Analysis:**")
                            st.metric("Gross Yield", f"{gross_yield:.1f}%")
                            
                            # Good yield indicator for UK market
                            yield_status = "✅ Good" if gross_yield >= 6 else "⚠️ Average" if gross_yield >= 4 else "❌ Low"
                            st.metric("Yield Rating", yield_status)
                            
                            # Monthly yield
                            monthly_yield = (monthly_rent / price) * 100 if price > 0 else 0
                            st.metric("Monthly Yield", f"{monthly_yield:.2f}%")
                        else:
                            st.info("Rent data not available")
                    
                    # Link to listing
                    if prop.get('listing_url'):
                        st.markdown(f"[View Listing]({prop.get('listing_url')})")
        
        # Bulk actions
        st.markdown("---")
        st.subheader("🔧 Bulk Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Select All"):
                for i in range(len(results)):
                    st.session_state[f"select_prop_{i}"] = True
                st.rerun()
        
        with col2:
            if st.button("❌ Clear Selection"):
                for i in range(len(results)):
                    st.session_state[f"select_prop_{i}"] = False
                st.rerun()
        
        with col3:
            if st.button("📊 Analyze Selected"):
                selected_props = []
                for i, prop in enumerate(results):
                    if st.session_state.get(f"select_prop_{i}", False):
                        selected_props.append(prop)
                
                if selected_props:
                    st.markdown("### 📈 Quick Analysis of Selected Properties")
                    
                    # Create analysis dataframe
                    analysis_data = []
                    for prop in selected_props:
                        if prop.get('price', 0) > 0 and prop.get('monthly_rent', 0) > 0:
                            price = prop.get('price', 0)
                            monthly_rent = prop.get('monthly_rent', 0)
                            annual_rent = monthly_rent * 12
                            gross_yield = (annual_rent / price) * 100
                            
                            analysis_data.append({
                                'Address': prop.get('address', 'N/A'),
                                'Price': price,
                                'Monthly Rent': monthly_rent,
                                'Gross Yield': gross_yield,
                                'Source': prop.get('source', 'N/A')
                            })
                    
                    if analysis_data:
                        analysis_df = pd.DataFrame(analysis_data)
                        
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Selected Properties", len(analysis_data))
                        with col2:
                            avg_yield = analysis_df['Gross Yield'].mean()
                            st.metric("Average Gross Yield", f"{avg_yield:.1f}%")
                        with col3:
                            avg_price = analysis_df['Price'].mean()
                            st.metric("Average Price", f"£{avg_price:,.0f}")
                        
                        # Visualization
                        fig = px.scatter(
                            analysis_df,
                            x='Price',
                            y='Gross Yield',
                            hover_data=['Address', 'Monthly Rent'],
                            title="Price vs Gross Yield for Selected Properties"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Data table
                        st.dataframe(analysis_df, use_container_width=True)
                else:
                    st.warning("Please select properties to analyze.")
    
    else:
        st.info("No search results available. Use the Property Search tab to find properties.")

with tab3:
    st.subheader("💾 Saved Searches")
    
    st.markdown("**Save Current Search**")
    
    if 'search_results' in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            search_name = st.text_input("Search Name", placeholder="Downtown San Francisco Properties")
        
        with col2:
            if st.button("💾 Save Search"):
                if search_name and 'search_results' in st.session_state:
                    # Initialize saved searches if not exists
                    if 'saved_searches' not in st.session_state:
                        st.session_state.saved_searches = {}
                    
                    # Save search
                    st.session_state.saved_searches[search_name] = {
                        'results': st.session_state.search_results,
                        'timestamp': st.session_state.search_timestamp,
                        'location': search_location if 'search_location' in locals() else 'Unknown'
                    }
                    
                    st.success(f"Search '{search_name}' saved successfully!")
                else:
                    st.error("Please enter a search name and ensure you have search results.")
    else:
        st.info("No current search to save. Perform a search first.")
    
    # Display saved searches
    if 'saved_searches' in st.session_state and st.session_state.saved_searches:
        st.markdown("---")
        st.markdown("**Your Saved Searches**")
        
        for search_name, search_data in st.session_state.saved_searches.items():
            with st.expander(f"📂 {search_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Location:** {search_data.get('location', 'Unknown')}")
                    st.write(f"**Properties:** {len(search_data.get('results', []))}")
                    st.write(f"**Saved:** {search_data.get('timestamp', 'Unknown').strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if st.button(f"🔄 Load Search", key=f"load_{search_name}"):
                        st.session_state.search_results = search_data['results']
                        st.session_state.search_timestamp = search_data['timestamp']
                        st.success(f"Loaded search '{search_name}'")
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{search_name}"):
                        del st.session_state.saved_searches[search_name]
                        st.success(f"Deleted search '{search_name}'")
                        st.rerun()
    else:
        st.info("No saved searches yet.")

# Footer with tips
st.markdown("---")
st.markdown("### 💡 Tips for Better Results")

with st.expander("How to get the best property data"):
    st.markdown("""
    **UK API Setup:**
    - Rightmove: UK's largest property portal with extensive listings
    - Zoopla: Comprehensive UK data including valuations and market trends
    - OnTheMarket: Independent platform with competitive listings
    - PropertyData: Specialized UK investment and yield data
    - Land Registry: Official UK government transaction data
    
    **UK Search Tips:**
    - Use specific UK city and county combinations for better results
    - Consider postcode areas for more precise searches
    - Start with broader criteria, then filter results
    - Save searches for areas you monitor regularly
    - Compare properties from different UK sources for completeness
    
    **UK Analysis Notes:**
    - Rental yields of 6%+ are generally considered good for UK buy-to-let
    - Yields of 4-6% are average, below 4% may be poor for investment
    - Estimated rents are calculated using UK market algorithms
    - Always verify property details with original listings
    - Consider UK-specific factors: council tax, ground rent, service charges
    - Use multiple metrics for comprehensive analysis
    """)