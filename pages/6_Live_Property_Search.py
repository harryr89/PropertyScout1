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

# Enhanced tabs with deal discovery
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Deal Discovery", "Address Search", "Area Search", "Search Results", "Auto Compare"])

with tab1:
    st.subheader("🎯 Investment Deal Discovery Engine")
    st.markdown("""Find the perfect investment deals using advanced criteria filtering and AI-powered property scoring.
    Set your investment criteria and let the system discover deals that match your requirements.""")
    
    # Deal discovery interface
    st.markdown("### 🎯 Investment Deal Discovery Criteria")
    st.markdown("Configure your investment criteria to find the perfect deals:")
    
    with st.form("deal_discovery_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📍 Location & Property**")
            location = st.text_input(
                "Location",
                value="Manchester",
                help="UK city or area to search"
            )
            
            property_types = st.multiselect(
                "Property Types",
                options=["Terraced", "Semi-Detached", "Detached", "Flat/Apartment", "Bungalow"],
                default=["Terraced", "Semi-Detached", "Flat/Apartment"],
                help="Select property types you're interested in"
            )
            
            min_bedrooms = st.selectbox("Min Bedrooms", [1, 2, 3, 4, 5], index=1)
            max_bedrooms = st.selectbox("Max Bedrooms", [2, 3, 4, 5, 6, 7, 8], index=3)
        
        with col2:
            st.markdown("**💰 Financial Criteria**")
            min_price = st.number_input("Min Price (£)", min_value=50000, value=150000, step=10000)
            max_price = st.number_input("Max Price (£)", min_value=100000, value=400000, step=10000)
            
            min_yield = st.slider(
                "Minimum Rental Yield (%)",
                min_value=2.0, max_value=15.0, value=6.0, step=0.5,
                help="UK average is 4-6%. Above 6% is good, 8%+ is excellent"
            )
            
            min_cash_flow = st.number_input(
                "Minimum Monthly Cash Flow (£)",
                min_value=-500, value=200, step=50,
                help="Positive cash flow after expenses and mortgage"
            )
        
        st.markdown("**⚙️ Advanced Options**")
        col3, col4 = st.columns(2)
        
        with col3:
            max_results = st.slider("Max Results", 10, 100, 50, 5)
            include_analysis = st.checkbox("Include Detailed Analysis", value=True)
        
        with col4:
            sort_by = st.selectbox(
                "Sort Results By",
                ["Deal Score", "Rental Yield", "Price (Low to High)", "Cash Flow"]
            )
            auto_compare = st.checkbox("Auto-select for Comparison", value=True)
        
        submitted = st.form_submit_button(
            "🚀 Discover Investment Deals",
            use_container_width=True
        )
        
        if submitted:
            criteria = {
                'location': location,
                'property_types': property_types,
                'min_bedrooms': min_bedrooms,
                'max_bedrooms': max_bedrooms,
                'min_price': min_price,
                'max_price': max_price,
                'min_yield': min_yield,
                'min_cash_flow': min_cash_flow,
                'max_results': max_results,
                'sort_by': sort_by,
                'include_analysis': include_analysis,
                'auto_compare': auto_compare
            }
            
            with st.spinner("🔍 Discovering investment deals..."):
                deals = st.session_state.property_sources.discover_investment_deals(criteria)
                
                if deals:
                    st.session_state.discovered_deals = deals
                    st.session_state.deal_criteria = criteria
                    
                    # Display results
                    st.success(f"🎉 Found {len(deals)} investment deals matching your criteria!")
                    
                    # Summary metrics
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        avg_deal_score = sum(d.get('deal_score', 0) for d in deals) / len(deals)
                        st.metric("Avg Deal Score", f"{avg_deal_score:.1f}/100")
                    
                    with col2:
                        avg_yield = sum(d.get('rental_yield', 0) for d in deals) / len(deals)
                        st.metric("Avg Yield", f"{avg_yield:.1f}%")
                    
                    with col3:
                        avg_price = sum(d.get('price', 0) for d in deals) / len(deals)
                        st.metric("Avg Price", f"£{avg_price:,.0f}")
                    
                    with col4:
                        avg_cash_flow = sum(d.get('estimated_cash_flow', 0) for d in deals) / len(deals)
                        st.metric("Avg Cash Flow", f"£{avg_cash_flow:,.0f}")
                    
                    with col5:
                        excellent_deals = len([d for d in deals if d.get('deal_score', 0) >= 80])
                        st.metric("Excellent Deals", excellent_deals)
                    
                    # Top 5 deals preview
                    st.markdown("### 🏆 Top Investment Deals")
                    
                    for i, deal in enumerate(deals[:5]):
                        with st.expander(
                            f"{deal.get('deal_quality', 'Unknown')} - "
                            f"{deal.get('address', 'N/A')} - "
                            f"£{deal.get('price', 0):,.0f} "
                            f"({deal.get('rental_yield', 0):.1f}% yield)",
                            expanded=i < 2
                        ):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.markdown(f"**📍 Address:** {deal.get('address', 'N/A')}")
                                st.markdown(f"**🏠 Type:** {deal.get('property_type', 'N/A')}")
                                st.markdown(f"**💰 Price:** £{deal.get('price', 0):,.0f}")
                                st.markdown(f"**📊 Deal Score:** {deal.get('deal_score', 0):.1f}/100")
                            
                            with col2:
                                st.markdown(f"**🛏️ Bedrooms:** {deal.get('bedrooms', 'N/A')}")
                                st.markdown(f"**📈 Yield:** {deal.get('rental_yield', 0):.1f}%")
                                st.markdown(f"**£ Monthly Rent:** £{deal.get('monthly_rent', 0):,}")
                                cash_flow = deal.get('estimated_cash_flow', 0)
                                st.markdown(f"**💵 Cash Flow:** £{cash_flow:,}/month")
                            
                            with col3:
                                st.metric("Quality", deal.get('deal_quality', 'Unknown'))
                                
                                # Action button
                                if st.button(f"➕ Add to Portfolio", key=f"add_deal_{deal.get('id', '')}_{i}"):
                                    if 'data_manager' in st.session_state:
                                        property_data = {
                                            'id': deal.get('id', f"deal_{uuid.uuid4().hex[:8]}"),
                                            'address': deal.get('address', ''),
                                            'property_type': deal.get('property_type', 'Unknown'),
                                            'price': deal.get('price', 0),
                                            'monthly_rent': deal.get('monthly_rent', 0),
                                            'monthly_expenses': deal.get('estimated_monthly_expenses', deal.get('price', 0) * 0.01),
                                            'loan_amount': deal.get('price', 0) * 0.75,
                                            'down_payment': deal.get('price', 0) * 0.25,
                                            'interest_rate': 5.5,
                                            'loan_term': 25,
                                            'bedrooms': deal.get('bedrooms', 0),
                                            'bathrooms': deal.get('bathrooms', 0),
                                            'square_feet': deal.get('square_feet', 0),
                                            'year_built': deal.get('year_built', 1990),
                                            'date_acquired': datetime.now().strftime('%Y-%m-%d'),
                                            'source': f"Deal Discovery - {deal.get('source', 'Unknown')}",
                                            'notes': f"Deal Score: {deal.get('deal_score', 0):.1f}/100. Quality: {deal.get('deal_quality', 'Unknown')}."
                                        }
                                        
                                        st.session_state.data_manager.save_property(property_data)
                                        st.success("✅ Added to portfolio!")
                    
                    # Auto-populate comparison if enabled
                    if criteria.get('auto_compare', False) and len(deals) >= 2:
                        st.session_state.auto_compare_properties = deals[:10]
                        st.success("🔥 Top deals auto-selected for comparison! Check the 'Auto Compare' tab.")
                    
                    # Show all deals button
                    if st.button("📄 View All Deals", use_container_width=True):
                        st.session_state['show_all_deals'] = True
                        st.rerun()
                else:
                    st.warning("No deals found matching your criteria. Try adjusting your filters.")
                    
    # Display all deals if requested
    if st.session_state.get('show_all_deals', False) and 'discovered_deals' in st.session_state:
        st.markdown("### 📈 Complete Deal Analysis")
        deals = st.session_state.discovered_deals
        
        # Deal quality pie chart
        quality_counts = {}
        for deal in deals:
            quality = deal.get('deal_quality', 'Unknown')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        if quality_counts:
            quality_df = pd.DataFrame([
                {'Quality': k, 'Count': v} for k, v in quality_counts.items()
            ])
            
            fig = px.pie(
                quality_df,
                values='Count',
                names='Quality',
                title="Deal Quality Distribution"
            )
            st.plotly_chart(fig, use_container_width=True, key="deal_quality_pie")
        
        # All deals table
        deal_df = pd.DataFrame([{
            'Address': d.get('address', 'N/A'),
            'Price': f"£{d.get('price', 0):,.0f}",
            'Yield': f"{d.get('rental_yield', 0):.1f}%",
            'Cash Flow': f"£{d.get('estimated_cash_flow', 0):,}",
            'Deal Score': f"{d.get('deal_score', 0):.1f}/100",
            'Quality': d.get('deal_quality', 'Unknown')
        } for d in deals])
        
        st.dataframe(deal_df, use_container_width=True)
        
        if st.button("❌ Hide All Deals"):
            st.session_state['show_all_deals'] = False
            st.rerun()

with tab2:
    st.subheader("🏠 Address-Based Property Search")
    st.markdown("Enter a specific address to find local market comparisons and automatically populate deal analysis.")
    
    # Address search form (existing functionality)
    with st.form("address_search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            target_address = st.text_input(
                "Property Address",
                placeholder="e.g., 123 Victoria Street, Manchester M1 2AB",
                help="Enter a specific UK address to search for comparable properties in the local area"
            )
        
        with col2:
            search_radius = st.selectbox(
                "Search Radius",
                ["0.5 miles", "1 mile", "2 miles", "5 miles"],
                index=1
            )
        
        # Search criteria
        col1, col2, col3 = st.columns(3)
        
        with col1:
            property_type = st.selectbox(
                "Property Type",
                ["All Types", "Terraced", "Semi-Detached", "Detached", "Flat/Apartment", "Bungalow"]
            )
        
        with col2:
            min_price = st.number_input("Min Price (£)", min_value=0, value=150000, step=10000)
        
        with col3:
            max_price = st.number_input("Max Price (£)", min_value=0, value=500000, step=10000)
        
        # Additional filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_bedrooms = st.selectbox("Min Bedrooms", [1, 2, 3, 4, 5, 6], index=1)
        
        with col2:
            max_bedrooms = st.selectbox("Max Bedrooms", [1, 2, 3, 4, 5, 6, 7, 8], index=3)
        
        with col3:
            include_investment = st.checkbox("Include Investment Analysis", value=True)
        
        submit_search = st.form_submit_button("🔍 Search Local Market", use_container_width=True)
    
    if submit_search and target_address:
        with st.spinner("Searching for properties near your address..."):
            # Parse the address to extract city/area
            address_parts = target_address.split(',')
            if len(address_parts) >= 2:
                city = address_parts[-2].strip()
            else:
                city = target_address.split()[-1]
            
            # Search for properties in the area
            search_params = {
                'location': city,
                'property_type': property_type.lower().replace('/', '_') if property_type != "All Types" else 'all',
                'min_price': min_price,
                'max_price': max_price,
                'min_bedrooms': min_bedrooms,
                'max_bedrooms': max_bedrooms,
                'radius': search_radius
            }
            
            properties = st.session_state.property_sources.search_local_market(target_address, search_params)
            
            if properties:
                st.success(f"Found {len(properties)} properties near {target_address}")
                
                # Store search results in session state
                st.session_state.address_search_results = properties
                st.session_state.target_address = target_address
                
                # Display summary
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_price = sum(p['price'] for p in properties) / len(properties)
                    st.metric("Average Price", f"£{avg_price:,.0f}")
                
                with col2:
                    avg_yield = sum(p.get('rental_yield', 0) for p in properties) / len(properties)
                    st.metric("Average Yield", f"{avg_yield:.1f}%")
                
                with col3:
                    price_range = max(p['price'] for p in properties) - min(p['price'] for p in properties)
                    st.metric("Price Range", f"£{price_range:,.0f}")
                
                with col4:
                    st.metric("Properties Found", len(properties))
                
                # Quick preview of top properties
                st.markdown("### Top 5 Properties")
                preview_df = pd.DataFrame(properties[:5])
                display_cols = ['address', 'price', 'bedrooms', 'property_type', 'rental_yield']
                available_cols = [col for col in display_cols if col in preview_df.columns]
                
                if available_cols:
                    preview_display = preview_df[available_cols].copy()
                    if 'price' in preview_display.columns:
                        preview_display['price'] = preview_display['price'].apply(lambda x: f"£{x:,.0f}")
                    if 'rental_yield' in preview_display.columns:
                        preview_display['rental_yield'] = preview_display['rental_yield'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(preview_display, use_container_width=True)
                
                # Auto-compare button
                if include_investment and len(properties) >= 2:
                    if st.button("📊 Auto-Compare Top Properties", use_container_width=True):
                        # Store top properties for comparison
                        st.session_state.auto_compare_properties = properties[:10]
                        st.success("Properties queued for automatic comparison! Check the 'Auto Compare' tab.")
                        st.rerun()
                
            else:
                st.warning(f"No properties found near {target_address}. Try expanding your search criteria.")

with tab3:
    st.subheader("🌍 Area-Based Property Search")
    
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

with tab4:
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

with tab5:
    st.subheader("⚡ Auto Compare Properties")
    st.markdown("Automatically import and compare properties from your address search for investment analysis.")
    
    if 'auto_compare_properties' in st.session_state and st.session_state.auto_compare_properties:
        properties = st.session_state.auto_compare_properties
        
        st.success(f"Ready to compare {len(properties)} properties from your search!")
        
        # Selection interface
        st.markdown("### Select Properties for Comparison")
        
        # Create selection interface
        selected_properties = []
        
        for i, prop in enumerate(properties):
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                selected = st.checkbox(
                    f"Property {i+1}",
                    key=f"auto_compare_{i}",
                    value=i < 5  # Auto-select first 5
                )
            
            with col2:
                st.markdown(f"**{prop.get('address', 'N/A')}**")
                st.markdown(f"£{prop.get('price', 0):,.0f} • {prop.get('bedrooms', 'N/A')} bed • {prop.get('rental_yield', 0):.1f}% yield")
            
            with col3:
                if prop.get('rental_yield', 0) >= 7:
                    st.success("High Yield")
                elif prop.get('rental_yield', 0) >= 5:
                    st.info("Good Yield")
                else:
                    st.warning("Low Yield")
            
            if selected:
                selected_properties.append(prop)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Deal Comparison", use_container_width=True):
                if selected_properties:
                    # Convert selected properties to the format expected by Deal Comparison
                    for prop in selected_properties:
                        # Add required fields for property import
                        import_data = {
                            'id': prop.get('id', f"auto_import_{uuid.uuid4()}"),
                            'address': prop.get('address', ''),
                            'property_type': prop.get('property_type', 'Unknown'),
                            'price': prop.get('price', 0),
                            'monthly_rent': prop.get('monthly_rent', 0),
                            'monthly_expenses': prop.get('price', 0) * 0.01,  # Estimate 1% monthly expenses
                            'loan_amount': prop.get('price', 0) * 0.75,  # Assume 75% LTV
                            'down_payment': prop.get('price', 0) * 0.25,  # 25% down
                            'interest_rate': 5.5,  # Current UK average
                            'loan_term': 25,  # UK standard
                            'bedrooms': prop.get('bedrooms', 0),
                            'bathrooms': prop.get('bathrooms', 0),
                            'square_feet': prop.get('square_feet', 0),
                            'year_built': 1980,  # Default estimate
                            'date_acquired': datetime.now().strftime('%Y-%m-%d'),
                            'source': prop.get('source', 'Auto Import')
                        }
                        
                        # Save to data manager
                        st.session_state.data_manager.add_property(import_data)
                    
                    st.success(f"Imported {len(selected_properties)} properties for comparison!")
                    st.info("Navigate to the 'Deal Comparison' page to analyze these properties.")
                    
                    # Optional: Auto-navigate hint
                    st.markdown("**Next Steps:**")
                    st.markdown("1. Go to the **Deal Comparison** page")
                    st.markdown("2. Your imported properties will be available for analysis")
                    st.markdown("3. Use the scoring system to rank investment potential")
                else:
                    st.warning("Please select properties to import.")
        
        with col2:
            if st.button("📈 Quick Analysis", use_container_width=True):
                if selected_properties:
                    # Generate quick comparison metrics
                    st.markdown("### Quick Investment Analysis")
                    
                    comparison_data = []
                    for prop in selected_properties:
                        price = prop.get('price', 0)
                        monthly_rent = prop.get('monthly_rent', 0)
                        rental_yield = prop.get('rental_yield', 0)
                        
                        comparison_data.append({
                            'Address': prop.get('address', 'N/A')[:30] + '...',
                            'Price': f"£{price:,.0f}",
                            'Monthly Rent': f"£{monthly_rent:,.0f}",
                            'Gross Yield': f"{rental_yield:.1f}%",
                            'Property Type': prop.get('property_type', 'N/A')
                        })
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True)
                    
                    # Quick metrics
                    prices = [prop.get('price', 0) for prop in selected_properties]
                    yields = [prop.get('rental_yield', 0) for prop in selected_properties]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_price = sum(prices) / len(prices) if prices else 0
                        st.metric("Average Price", f"£{avg_price:,.0f}")
                    with col2:
                        avg_yield = sum(yields) / len(yields) if yields else 0
                        st.metric("Average Yield", f"{avg_yield:.1f}%")
                    with col3:
                        best_yield = max(yields) if yields else 0
                        st.metric("Best Yield", f"{best_yield:.1f}%")
                else:
                    st.warning("Please select properties to analyze.")
        
        with col3:
            if st.button("🗑️ Clear Selection", use_container_width=True):
                # Clear the auto compare properties
                if 'auto_compare_properties' in st.session_state:
                    del st.session_state.auto_compare_properties
                st.success("Selection cleared!")
                st.rerun()
    
    else:
        st.info("No properties available for auto comparison.")
        st.markdown("**To use Auto Compare:**")
        st.markdown("1. Use the **Address Search** tab")
        st.markdown("2. Search for properties near a specific address")
        st.markdown("3. Click **Auto-Compare Top Properties**")
        st.markdown("4. Return to this tab to import and analyze")

with tab3:
    st.subheader("📋 Search Results")
    
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