import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Deal Comparison",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Deal Comparison & Ranking")
st.markdown("Compare multiple properties and rank them based on investment criteria.")

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

# Get properties data
properties_df = st.session_state.data_manager.get_properties()

if properties_df.empty:
    st.info("No properties available for comparison. Add properties in the Property Input page.")
else:
    # Tabs for different comparison views
    tab1, tab2, tab3 = st.tabs(["Side-by-Side Comparison", "Ranking & Scoring", "Market Position"])
    
    with tab1:
        st.subheader("Side-by-Side Property Comparison")
        
        # Property selection
        available_properties = properties_df['address'].tolist()
        
        if len(available_properties) >= 2:
            selected_properties = st.multiselect(
                "Select properties to compare (2-6 properties):",
                available_properties,
                default=available_properties[:min(3, len(available_properties))]
            )
            
            if len(selected_properties) >= 2:
                # Filter data for selected properties
                comparison_df = properties_df[properties_df['address'].isin(selected_properties)]
                
                # Calculate metrics for each property
                enhanced_data = []
                for _, prop in comparison_df.iterrows():
                    metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                    
                    enhanced_prop = {
                        'Address': prop['address'],
                        'Type': prop['property_type'],
                        'Price': f"${prop['price']:,.0f}",
                        'Monthly Rent': f"${prop['monthly_rent']:,.0f}",
                        'ROI': f"{metrics.get('roi', 0):.2f}%",
                        'Cap Rate': f"{metrics.get('cap_rate', 0):.2f}%",
                        'Cash Flow': f"${metrics.get('monthly_cash_flow', 0):,.0f}",
                        'Cash-on-Cash': f"{metrics.get('cash_on_cash', 0):.2f}%",
                        'DSCR': f"{metrics.get('dscr', 0):.2f}",
                        'Bedrooms': prop['bedrooms'],
                        'Bathrooms': prop['bathrooms'],
                        'Sq Ft': f"{prop['square_feet']:,}",
                        'Year Built': prop['year_built']
                    }
                    enhanced_data.append(enhanced_prop)
                
                # Display comparison table
                comparison_display_df = pd.DataFrame(enhanced_data)
                st.dataframe(comparison_display_df.T, use_container_width=True)
                
                # Visual comparisons
                st.markdown("---")
                st.subheader("📊 Visual Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Price vs Monthly Rent
                    fig = px.scatter(
                        comparison_df, 
                        x='price', 
                        y='monthly_rent',
                        text='address',
                        title="Price vs Monthly Rent",
                        labels={'price': 'Purchase Price ($)', 'monthly_rent': 'Monthly Rent ($)'}
                    )
                    fig.update_traces(textposition="top center")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # ROI comparison
                    roi_data = []
                    for _, prop in comparison_df.iterrows():
                        metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                        roi_data.append({
                            'Address': prop['address'],
                            'ROI': metrics.get('roi', 0)
                        })
                    
                    roi_df = pd.DataFrame(roi_data)
                    fig = px.bar(roi_df, x='Address', y='ROI', title="ROI Comparison")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Financial metrics comparison
                st.markdown("---")
                st.subheader("💰 Financial Metrics Comparison")
                
                metrics_data = []
                for _, prop in comparison_df.iterrows():
                    metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                    metrics_data.append({
                        'Property': prop['address'],
                        'ROI': metrics.get('roi', 0),
                        'Cap Rate': metrics.get('cap_rate', 0),
                        'Cash-on-Cash': metrics.get('cash_on_cash', 0),
                        'DSCR': metrics.get('dscr', 0)
                    })
                
                metrics_df = pd.DataFrame(metrics_data)
                
                # Radar chart for metrics comparison
                fig = go.Figure()
                
                for i, row in metrics_df.iterrows():
                    fig.add_trace(go.Scatterpolar(
                        r=[row['ROI'], row['Cap Rate'], row['Cash-on-Cash'], row['DSCR']],
                        theta=['ROI', 'Cap Rate', 'Cash-on-Cash', 'DSCR'],
                        fill='toself',
                        name=row['Property']
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(metrics_df[['ROI', 'Cap Rate', 'Cash-on-Cash', 'DSCR']].max())]
                        )),
                    showlegend=True,
                    title="Financial Metrics Comparison"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning("Please select at least 2 properties for comparison.")
        else:
            st.info("You need at least 2 properties to perform comparisons.")
    
    with tab2:
        st.subheader("Property Ranking & Scoring")
        
        # Scoring criteria weights
        st.markdown("**Customize Scoring Weights**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            roi_weight = st.slider("ROI Weight", 0.0, 1.0, 0.3, 0.1)
        with col2:
            cap_rate_weight = st.slider("Cap Rate Weight", 0.0, 1.0, 0.25, 0.1)
        with col3:
            cash_flow_weight = st.slider("Cash Flow Weight", 0.0, 1.0, 0.25, 0.1)
        with col4:
            dscr_weight = st.slider("DSCR Weight", 0.0, 1.0, 0.2, 0.1)
        
        # Normalize weights
        total_weight = roi_weight + cap_rate_weight + cash_flow_weight + dscr_weight
        if total_weight > 0:
            roi_weight /= total_weight
            cap_rate_weight /= total_weight
            cash_flow_weight /= total_weight
            dscr_weight /= total_weight
        
        # Calculate scores for all properties
        scored_properties = []
        for _, prop in properties_df.iterrows():
            metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
            
            # Calculate weighted score
            score = (
                metrics.get('roi', 0) * roi_weight +
                metrics.get('cap_rate', 0) * cap_rate_weight +
                (metrics.get('monthly_cash_flow', 0) / 1000) * cash_flow_weight +  # Normalize cash flow
                metrics.get('dscr', 0) * 10 * dscr_weight  # Normalize DSCR
            )
            
            scored_properties.append({
                'Address': prop['address'],
                'Property Type': prop['property_type'],
                'Price': prop['price'],
                'ROI': metrics.get('roi', 0),
                'Cap Rate': metrics.get('cap_rate', 0),
                'Monthly Cash Flow': metrics.get('monthly_cash_flow', 0),
                'DSCR': metrics.get('dscr', 0),
                'Score': score
            })
        
        # Sort by score (highest first)
        scored_properties.sort(key=lambda x: x['Score'], reverse=True)
        
        # Display ranking
        st.markdown("---")
        st.subheader("🏆 Property Rankings")
        
        ranking_data = []
        for i, prop in enumerate(scored_properties, 1):
            ranking_data.append({
                'Rank': i,
                'Address': prop['Address'],
                'Type': prop['Property Type'],
                'Price': f"${prop['Price']:,.0f}",
                'Score': f"{prop['Score']:.2f}",
                'ROI': f"{prop['ROI']:.2f}%",
                'Cap Rate': f"{prop['Cap Rate']:.2f}%",
                'Cash Flow': f"${prop['Monthly Cash Flow']:,.0f}",
                'DSCR': f"{prop['DSCR']:.2f}"
            })
        
        ranking_df = pd.DataFrame(ranking_data)
        
        # Style the dataframe
        def highlight_top_performers(row):
            if row['Rank'] <= 3:
                return ['background-color: #d4edda'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            ranking_df.style.apply(highlight_top_performers, axis=1),
            use_container_width=True
        )
        
        # Top performers visualization
        st.markdown("---")
        st.subheader("🎯 Top Performers")
        
        top_5 = scored_properties[:5]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score comparison
            addresses = [prop['Address'] for prop in top_5]
            scores = [prop['Score'] for prop in top_5]
            
            fig = px.bar(
                x=addresses, 
                y=scores,
                title="Top 5 Properties by Score",
                labels={'x': 'Property', 'y': 'Score'}
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ROI vs Cap Rate scatter
            roi_values = [prop['ROI'] for prop in top_5]
            cap_rate_values = [prop['Cap Rate'] for prop in top_5]
            
            fig = px.scatter(
                x=roi_values,
                y=cap_rate_values,
                text=addresses,
                title="ROI vs Cap Rate (Top 5)",
                labels={'x': 'ROI (%)', 'y': 'Cap Rate (%)'}
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
        
        # Investment recommendations
        st.markdown("---")
        st.subheader("💡 Investment Recommendations")
        
        if scored_properties:
            best_property = scored_properties[0]
            
            st.success(f"🏆 **Top Recommendation**: {best_property['Address']}")
            st.write(f"**Score**: {best_property['Score']:.2f}")
            st.write(f"**ROI**: {best_property['ROI']:.2f}%")
            st.write(f"**Cap Rate**: {best_property['Cap Rate']:.2f}%")
            st.write(f"**Monthly Cash Flow**: ${best_property['Monthly Cash Flow']:,.0f}")
            
            # Risk assessment
            if best_property['DSCR'] > 1.25:
                st.info("✅ **Low Risk**: Strong debt service coverage ratio")
            elif best_property['DSCR'] > 1.0:
                st.warning("⚠️ **Medium Risk**: Adequate but monitor closely")
            else:
                st.error("🚨 **High Risk**: Insufficient debt coverage")
    
    with tab3:
        st.subheader("Market Position Analysis")
        
        # Market benchmarks (these would typically come from external data)
        st.markdown("**Market Benchmarks**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            market_roi = st.number_input("Market Average ROI (%)", value=8.0, step=0.5)
        with col2:
            market_cap_rate = st.number_input("Market Average Cap Rate (%)", value=6.5, step=0.5)
        with col3:
            market_rent_psf = st.number_input("Market Rent per Sq Ft ($)", value=1.50, step=0.05)
        
        # Analyze portfolio vs market
        portfolio_analysis = []
        for _, prop in properties_df.iterrows():
            metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
            
            rent_psf = (prop['monthly_rent'] * 12) / prop['square_feet'] if prop['square_feet'] > 0 else 0
            
            portfolio_analysis.append({
                'Address': prop['address'],
                'ROI': metrics.get('roi', 0),
                'Cap Rate': metrics.get('cap_rate', 0),
                'Rent per Sq Ft': rent_psf,
                'ROI vs Market': metrics.get('roi', 0) - market_roi,
                'Cap Rate vs Market': metrics.get('cap_rate', 0) - market_cap_rate,
                'Rent vs Market': rent_psf - market_rent_psf
            })
        
        analysis_df = pd.DataFrame(portfolio_analysis)
        
        # Performance vs market visualization
        st.markdown("---")
        st.subheader("📊 Portfolio vs Market Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI comparison
            fig = px.bar(
                analysis_df,
                x='Address',
                y='ROI vs Market',
                title="ROI vs Market Average",
                color='ROI vs Market',
                color_continuous_scale='RdYlGn'
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Market Average")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cap Rate comparison
            fig = px.bar(
                analysis_df,
                x='Address',
                y='Cap Rate vs Market',
                title="Cap Rate vs Market Average",
                color='Cap Rate vs Market',
                color_continuous_scale='RdYlGn'
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Market Average")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Portfolio positioning
        st.markdown("---")
        st.subheader("🎯 Portfolio Positioning")
        
        # Quadrant analysis
        fig = px.scatter(
            analysis_df,
            x='ROI vs Market',
            y='Cap Rate vs Market',
            text='Address',
            title="Portfolio Positioning (vs Market)",
            labels={'x': 'ROI vs Market (%)', 'y': 'Cap Rate vs Market (%)'}
        )
        
        # Add quadrant lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        
        # Add quadrant labels
        fig.add_annotation(x=2, y=2, text="High ROI<br>High Cap Rate", showarrow=False, bgcolor="lightgreen")
        fig.add_annotation(x=-2, y=2, text="Low ROI<br>High Cap Rate", showarrow=False, bgcolor="lightyellow")
        fig.add_annotation(x=2, y=-2, text="High ROI<br>Low Cap Rate", showarrow=False, bgcolor="lightyellow")
        fig.add_annotation(x=-2, y=-2, text="Low ROI<br>Low Cap Rate", showarrow=False, bgcolor="lightcoral")
        
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.markdown("---")
        st.subheader("📈 Portfolio Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_roi_diff = analysis_df['ROI vs Market'].mean()
            if avg_roi_diff > 0:
                st.metric("Portfolio ROI vs Market", f"+{avg_roi_diff:.1f}%", delta=f"{avg_roi_diff:.1f}%")
            else:
                st.metric("Portfolio ROI vs Market", f"{avg_roi_diff:.1f}%", delta=f"{avg_roi_diff:.1f}%")
        
        with col2:
            avg_cap_diff = analysis_df['Cap Rate vs Market'].mean()
            if avg_cap_diff > 0:
                st.metric("Portfolio Cap Rate vs Market", f"+{avg_cap_diff:.1f}%", delta=f"{avg_cap_diff:.1f}%")
            else:
                st.metric("Portfolio Cap Rate vs Market", f"{avg_cap_diff:.1f}%", delta=f"{avg_cap_diff:.1f}%")
        
        with col3:
            outperforming = len(analysis_df[analysis_df['ROI vs Market'] > 0])
            total = len(analysis_df)
            st.metric("Properties Outperforming Market", f"{outperforming}/{total}", 
                     delta=f"{(outperforming/total)*100:.0f}% of portfolio")
