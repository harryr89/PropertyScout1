import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Market Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Market Analysis & Trends")
st.markdown("Analyze market trends and benchmark your properties against market data.")

# Initialize session state
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

# Generate sample market data (in a real application, this would come from external APIs)
def generate_market_data():
    """Generate sample market data for demonstration"""
    # Historical price trends
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='ME')
    base_price = 280000  # Updated to reflect current UK average house price
    
    price_data = []
    for date in dates:
        # Add some trend and seasonality
        months_from_start = (date - dates[0]).days / 30.44
        trend = (1 + 0.0021) ** months_from_start  # 2.5% annual growth compounded monthly
        seasonal = 1 + 0.05 * np.sin(2 * np.pi * date.month / 12)  # 5% seasonal variation
        noise = 1 + np.random.normal(0, 0.02)  # 2% random noise
        
        price = base_price * trend * seasonal * noise
        price_data.append({
            'date': date,
            'median_price': price,
            'avg_days_on_market': random.randint(25, 90),
            'inventory_months': random.uniform(2.5, 8.0),
            'price_per_sqft': price / 1500  # Assume 1500 sq ft average
        })
    
    return pd.DataFrame(price_data)

# Tabs for different analysis types
tab1, tab2, tab3, tab4 = st.tabs(["Price Trends", "Market Metrics", "Comparative Analysis", "Market Forecast"])

with tab1:
    st.subheader("📊 Price Trends Analysis")
    
    # Market selection
    col1, col2 = st.columns(2)
    
    with col1:
        selected_market = st.selectbox(
            "Select Market:",
            ["National Average", "Local Market", "Metropolitan Area", "County"]
        )
    
    with col2:
        time_period = st.selectbox(
            "Time Period:",
            ["1 Year", "2 Years", "3 Years", "5 Years"]
        )
    
    # Generate market data
    market_data = generate_market_data()
    
    # Filter data based on time period
    end_date = market_data['date'].max()
    if time_period == "1 Year":
        start_date = end_date - timedelta(days=365)
    elif time_period == "2 Years":
        start_date = end_date - timedelta(days=730)
    elif time_period == "3 Years":
        start_date = end_date - timedelta(days=1095)
    else:  # 5 Years
        start_date = end_date - timedelta(days=1825)
    
    filtered_data = market_data[market_data['date'] >= start_date]
    
    # Price trend chart
    st.markdown("---")
    st.subheader(f"📈 Median Home Price Trend - {selected_market}")
    
    fig = px.line(
        filtered_data,
        x='date',
        y='median_price',
        title=f"Median Home Price Trend ({time_period})",
        labels={'date': 'Date', 'median_price': 'Median Price (£)'}
    )
    
    # Add trend line
    z = np.polyfit(range(len(filtered_data)), filtered_data['median_price'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=p(range(len(filtered_data))),
        mode='lines',
        name='Trend Line',
        line=dict(dash='dash', color='red')
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Price statistics
    col1, col2, col3, col4 = st.columns(4)
    
    current_price = filtered_data['median_price'].iloc[-1]
    previous_price = filtered_data['median_price'].iloc[0]
    price_change = ((current_price - previous_price) / previous_price) * 100
    
    with col1:
        st.metric("Current Median Price", f"£{current_price:,.0f}")
    
    with col2:
        st.metric("Price Change", f"{price_change:+.1f}%", delta=f"£{current_price - previous_price:,.0f}")
    
    with col3:
        annual_growth = (price_change / int(time_period.split()[0])) if time_period != "1 Year" else price_change
        st.metric("Annual Growth Rate", f"{annual_growth:.1f}%")
    
    with col4:
        avg_price_psf = filtered_data['price_per_sqft'].mean()
        st.metric("Avg Price per Sq Ft", f"${avg_price_psf:.0f}")
    
    # Price distribution
    st.markdown("---")
    st.subheader("📊 Price Distribution")
    
    fig = px.histogram(
        filtered_data,
        x='median_price',
        nbins=20,
        title="Price Distribution Over Time Period"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📈 Market Metrics Dashboard")
    
    # Key market indicators
    st.markdown("**Key Market Indicators**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Supply Metrics**")
        current_inventory = market_data['inventory_months'].iloc[-1]
        st.metric("Months of Inventory", f"{current_inventory:.1f}")
        
        if current_inventory < 4:
            st.success("🔥 Seller's Market")
        elif current_inventory < 6:
            st.info("⚖️ Balanced Market")
        else:
            st.warning("📉 Buyer's Market")
    
    with col2:
        st.markdown("**Demand Metrics**")
        avg_days_market = market_data['avg_days_on_market'].iloc[-1]
        st.metric("Avg Days on Market", f"{avg_days_market}")
        
        if avg_days_market < 30:
            st.success("🚀 High Demand")
        elif avg_days_market < 60:
            st.info("📊 Moderate Demand")
        else:
            st.warning("🐌 Low Demand")
    
    with col3:
        st.markdown("**Price Metrics**")
        current_price_psf = market_data['price_per_sqft'].iloc[-1]
        st.metric("Price per Sq Ft", f"${current_price_psf:.0f}")
        
        price_psf_change = ((current_price_psf - market_data['price_per_sqft'].iloc[0]) / 
                           market_data['price_per_sqft'].iloc[0]) * 100
        st.metric("Price/Sq Ft Change", f"{price_psf_change:+.1f}%")
    
    # Market health indicators
    st.markdown("---")
    st.subheader("🏥 Market Health Indicators")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory trend
        fig = px.line(
            market_data.tail(12),
            x='date',
            y='inventory_months',
            title="Inventory Trend (Last 12 Months)",
            labels={'date': 'Date', 'inventory_months': 'Months of Inventory'}
        )
        fig.add_hline(y=4, line_dash="dash", line_color="green", annotation_text="Seller's Market")
        fig.add_hline(y=6, line_dash="dash", line_color="orange", annotation_text="Buyer's Market")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Days on market trend
        fig = px.line(
            market_data.tail(12),
            x='date',
            y='avg_days_on_market',
            title="Days on Market Trend (Last 12 Months)",
            labels={'date': 'Date', 'avg_days_on_market': 'Average Days on Market'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Market cycle analysis
    st.markdown("---")
    st.subheader("🔄 Market Cycle Analysis")
    
    # Determine market phase
    recent_price_change = ((market_data['median_price'].iloc[-1] - market_data['median_price'].iloc[-6]) / 
                          market_data['median_price'].iloc[-6]) * 100
    
    if recent_price_change > 5 and current_inventory < 4:
        market_phase = "🚀 Expansion"
        phase_color = "green"
    elif recent_price_change > 0 and current_inventory < 6:
        market_phase = "📈 Growth"
        phase_color = "blue"
    elif recent_price_change < -2 and current_inventory > 6:
        market_phase = "📉 Decline"
        phase_color = "red"
    else:
        market_phase = "⚖️ Stabilization"
        phase_color = "orange"
    
    st.markdown(f"**Current Market Phase:** {market_phase}")
    
    # Market cycle visualization
    phases = ['Decline', 'Stabilization', 'Growth', 'Expansion']
    phase_values = [1, 2, 3, 4]
    current_phase_value = phases.index(market_phase.split()[1]) + 1
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[current_phase_value],
        theta=[market_phase.split()[1]],
        fill='toself',
        name='Current Phase'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 4]),
            angularaxis=dict(tickvals=phase_values, ticktext=phases)
        ),
        showlegend=True,
        title="Market Cycle Position"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🔍 Comparative Market Analysis")
    
    # Get user properties
    properties_df = st.session_state.data_manager.get_properties()
    
    if not properties_df.empty:
        # Property selection for comparison
        selected_property = st.selectbox(
            "Select a property to compare with market:",
            properties_df['address'].tolist()
        )
        
        if selected_property:
            property_data = properties_df[properties_df['address'] == selected_property].iloc[0]
            
            st.markdown(f"**Analyzing: {property_data['address']}**")
            
            # Property vs market comparison
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Property Details**")
                st.write(f"**Price:** ${property_data['price']:,.0f}")
                st.write(f"**Type:** {property_data['property_type']}")
                st.write(f"**Bedrooms:** {property_data['bedrooms']}")
                st.write(f"**Bathrooms:** {property_data['bathrooms']}")
                st.write(f"**Square Feet:** {property_data['square_feet']:,}")
                
                property_psf = property_data['price'] / property_data['square_feet']
                st.write(f"**Price per Sq Ft:** ${property_psf:.0f}")
            
            with col2:
                st.markdown("**Market Comparison**")
                market_median = market_data['median_price'].iloc[-1]
                market_psf = market_data['price_per_sqft'].iloc[-1]
                
                price_vs_market = ((property_data['price'] - market_median) / market_median) * 100
                psf_vs_market = ((property_psf - market_psf) / market_psf) * 100
                
                st.metric("Price vs Market", f"{price_vs_market:+.1f}%")
                st.metric("Price/Sq Ft vs Market", f"{psf_vs_market:+.1f}%")
                
                if price_vs_market > 10:
                    st.warning("⚠️ Above Market Premium")
                elif price_vs_market < -10:
                    st.success("💰 Below Market Value")
                else:
                    st.info("✅ Market Aligned")
            
            with col3:
                st.markdown("**Investment Timing**")
                
                # Calculate timing score based on market conditions
                timing_score = 0
                
                if current_inventory > 6:  # Buyer's market
                    timing_score += 30
                elif current_inventory < 4:  # Seller's market
                    timing_score -= 20
                
                if avg_days_market > 60:  # Slow market
                    timing_score += 20
                elif avg_days_market < 30:  # Fast market
                    timing_score -= 10
                
                if recent_price_change < 0:  # Declining prices
                    timing_score += 25
                elif recent_price_change > 10:  # Rapid appreciation
                    timing_score -= 15
                
                timing_score = max(0, min(100, timing_score + 50))  # Normalize to 0-100
                
                st.metric("Buy Timing Score", f"{timing_score}/100")
                
                if timing_score > 70:
                    st.success("🎯 Excellent Timing")
                elif timing_score > 50:
                    st.info("👍 Good Timing")
                else:
                    st.warning("⏳ Consider Waiting")
            
            # Comparable properties analysis
            st.markdown("---")
            st.subheader("🏠 Comparable Properties Analysis")
            
            # Generate comparable properties (mock data)
            comparable_properties = []
            for i in range(5):
                comp_price = property_data['price'] * (1 + np.random.normal(0, 0.15))
                comp_sqft = property_data['square_feet'] * (1 + np.random.normal(0, 0.10))
                comp_beds = property_data['bedrooms'] + np.random.randint(-1, 2)
                comp_beds = max(1, comp_beds)
                
                comparable_properties.append({
                    'Address': f"Comparable Property {i+1}",
                    'Price': comp_price,
                    'Square Feet': comp_sqft,
                    'Bedrooms': comp_beds,
                    'Bathrooms': property_data['bathrooms'] + np.random.choice([-0.5, 0, 0.5]),
                    'Price per Sq Ft': comp_price / comp_sqft
                })
            
            comp_df = pd.DataFrame(comparable_properties)
            
            # Add subject property to comparison
            subject_property = {
                'Address': f"{property_data['address']} (Subject)",
                'Price': property_data['price'],
                'Square Feet': property_data['square_feet'],
                'Bedrooms': property_data['bedrooms'],
                'Bathrooms': property_data['bathrooms'],
                'Price per Sq Ft': property_psf
            }
            
            comp_df = pd.concat([comp_df, pd.DataFrame([subject_property])], ignore_index=True)
            
            # Display comparison table
            st.dataframe(comp_df.round(0), use_container_width=True)
            
            # Visualization
            fig = px.scatter(
                comp_df,
                x='Square Feet',
                y='Price',
                color='Bedrooms',
                size='Bathrooms',
                hover_data=['Price per Sq Ft'],
                title="Comparable Properties Analysis"
            )
            
            # Highlight subject property
            subject_row = comp_df[comp_df['Address'].str.contains('Subject')]
            fig.add_trace(go.Scatter(
                x=subject_row['Square Feet'],
                y=subject_row['Price'],
                mode='markers',
                marker=dict(size=15, color='red', symbol='star'),
                name='Subject Property'
            ))
            
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No properties available for comparison. Add properties in the Property Input page.")

with tab4:
    st.subheader("🔮 Market Forecast")
    
    st.markdown("**Predictive Market Analysis**")
    
    # Generate forecast data
    forecast_periods = 12  # 12 months
    last_date = market_data['date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=30), periods=forecast_periods, freq='ME')
    
    # Simple trend-based forecast
    recent_trend = np.polyfit(range(12), market_data['median_price'].tail(12), 1)[0]
    last_price = market_data['median_price'].iloc[-1]
    
    forecast_prices = []
    for i in range(forecast_periods):
        # Add trend with some uncertainty
        trend_price = last_price + (recent_trend * (i + 1))
        seasonal_factor = 1 + 0.03 * np.sin(2 * np.pi * (last_date.month + i) / 12)
        forecast_price = trend_price * seasonal_factor
        forecast_prices.append(forecast_price)
    
    forecast_data = pd.DataFrame({
        'date': forecast_dates,
        'forecast_price': forecast_prices,
        'confidence_low': [p * 0.95 for p in forecast_prices],
        'confidence_high': [p * 1.05 for p in forecast_prices]
    })
    
    # Combine historical and forecast data
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['median_price'],
        mode='lines',
        name='Historical Prices',
        line=dict(color='blue')
    ))
    
    # Forecast data
    fig.add_trace(go.Scatter(
        x=forecast_data['date'],
        y=forecast_data['forecast_price'],
        mode='lines',
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_data['date'],
        y=forecast_data['confidence_high'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_data['date'],
        y=forecast_data['confidence_low'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.2)',
        name='Confidence Interval',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title="12-Month Price Forecast",
        xaxis_title="Date",
        yaxis_title="Median Price ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast insights
    st.markdown("---")
    st.subheader("📊 Forecast Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        forecast_change = ((forecast_data['forecast_price'].iloc[-1] - last_price) / last_price) * 100
        st.metric("12-Month Forecast", f"{forecast_change:+.1f}%")
    
    with col2:
        if forecast_change > 5:
            outlook = "🔥 Strong Growth"
        elif forecast_change > 0:
            outlook = "📈 Modest Growth"
        elif forecast_change > -5:
            outlook = "📊 Stable"
        else:
            outlook = "📉 Decline"
        st.metric("Market Outlook", outlook)
    
    with col3:
        confidence = "High" if abs(recent_trend) > 1000 else "Moderate"
        st.metric("Forecast Confidence", confidence)
    
    # Investment recommendations based on forecast
    st.markdown("---")
    st.subheader("💡 Investment Recommendations")
    
    if forecast_change > 5:
        st.success("🚀 **Strong Buy Signal**: Market showing strong upward momentum")
        st.write("- Consider accelerating purchase timelines")
        st.write("- Look for properties with renovation potential")
        st.write("- Consider leveraging opportunities")
    elif forecast_change > 0:
        st.info("📈 **Moderate Buy Signal**: Steady market growth expected")
        st.write("- Good time for quality investments")
        st.write("- Focus on cash flow positive properties")
        st.write("- Consider long-term hold strategies")
    elif forecast_change > -5:
        st.warning("⚖️ **Neutral Signal**: Market stability expected")
        st.write("- Focus on high-yield properties")
        st.write("- Consider value-add opportunities")
        st.write("- Maintain conservative approach")
    else:
        st.error("🛑 **Caution Signal**: Market decline forecasted")
        st.write("- Consider delaying purchases")
        st.write("- Focus on distressed opportunities")
        st.write("- Maintain high cash reserves")
    
    # Market risk assessment
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")
    
    risk_factors = []
    
    if current_inventory < 2:
        risk_factors.append("Very tight inventory - potential for rapid price swings")
    elif current_inventory > 8:
        risk_factors.append("High inventory - potential for price stagnation")
    
    if recent_price_change > 15:
        risk_factors.append("Rapid price appreciation - potential bubble risk")
    elif recent_price_change < -10:
        risk_factors.append("Significant price decline - market instability")
    
    if avg_days_market > 120:
        risk_factors.append("Extended time on market - liquidity concerns")
    
    if risk_factors:
        st.warning("**Risk Factors Identified:**")
        for risk in risk_factors:
            st.write(f"- {risk}")
    else:
        st.success("✅ **No significant risk factors identified**")
