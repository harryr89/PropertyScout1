import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Performance Tracking",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Investment Performance Tracking")
st.markdown("Track and analyze the performance of your property investments over time.")

# Initialize session state
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

if 'property_calculator' not in st.session_state:
    from utils.calculations import PropertyCalculator
    st.session_state.property_calculator = PropertyCalculator()

# Get properties data
properties_df = st.session_state.data_manager.get_properties()

if properties_df.empty:
    st.info("No properties available for tracking. Add properties in the Property Input page.")
else:
    # Generate performance data for demonstration
    def generate_performance_data(property_data):
        """Generate historical performance data for a property"""
        start_date = property_data.get('date_acquired', datetime.now() - timedelta(days=365))
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        months = pd.date_range(start=start_date, end=datetime.now(), freq='M')
        
        performance_data = []
        base_value = property_data['price']
        base_rent = property_data['monthly_rent']
        
        for i, month in enumerate(months):
            # Property appreciation (3-5% annually with some volatility)
            appreciation_rate = 0.04 + np.random.normal(0, 0.02)
            current_value = base_value * (1 + appreciation_rate * (i / 12))
            
            # Rent growth (2-4% annually)
            rent_growth = 0.03 + np.random.normal(0, 0.01)
            current_rent = base_rent * (1 + rent_growth * (i / 12))
            
            # Monthly expenses (varies with some seasonality)
            monthly_expenses = property_data['monthly_expenses'] * (1 + 0.02 * (i / 12))
            
            # Calculate metrics
            monthly_cash_flow = current_rent - monthly_expenses
            annual_cash_flow = monthly_cash_flow * 12
            
            # Simple mortgage calculation
            if property_data['loan_amount'] > 0:
                r = property_data['interest_rate'] / 100 / 12
                n = property_data['loan_term'] * 12
                monthly_payment = property_data['loan_amount'] * (r * (1 + r)**n) / ((1 + r)**n - 1)
                monthly_cash_flow -= monthly_payment
                annual_cash_flow = monthly_cash_flow * 12
            
            total_return = ((current_value - base_value) + (annual_cash_flow * (i / 12))) / base_value * 100
            
            performance_data.append({
                'date': month,
                'property_value': current_value,
                'monthly_rent': current_rent,
                'monthly_cash_flow': monthly_cash_flow,
                'annual_cash_flow': annual_cash_flow,
                'total_return': total_return,
                'appreciation': ((current_value - base_value) / base_value) * 100
            })
        
        return pd.DataFrame(performance_data)
    
    # Tabs for different performance views
    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", "Individual Property", "Performance Metrics", "Reports"])
    
    with tab1:
        st.subheader("🏠 Portfolio Performance Overview")
        
        # Portfolio summary metrics
        total_value = properties_df['price'].sum()
        total_monthly_rent = properties_df['monthly_rent'].sum()
        total_monthly_expenses = properties_df['monthly_expenses'].sum()
        net_monthly_cash_flow = total_monthly_rent - total_monthly_expenses
        
        # Calculate portfolio metrics
        portfolio_metrics = []
        total_equity = 0
        total_debt = 0
        
        for _, prop in properties_df.iterrows():
            metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
            portfolio_metrics.append(metrics)
            total_equity += prop['price'] - prop.get('loan_amount', 0)
            total_debt += prop.get('loan_amount', 0)
        
        avg_roi = np.mean([m.get('roi', 0) for m in portfolio_metrics])
        avg_cap_rate = np.mean([m.get('cap_rate', 0) for m in portfolio_metrics])
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.0f}")
            st.metric("Total Monthly Rent", f"${total_monthly_rent:,.0f}")
        
        with col2:
            st.metric("Monthly Cash Flow", f"${net_monthly_cash_flow:,.0f}")
            st.metric("Annual Cash Flow", f"${net_monthly_cash_flow * 12:,.0f}")
        
        with col3:
            st.metric("Average ROI", f"{avg_roi:.1f}%")
            st.metric("Average Cap Rate", f"{avg_cap_rate:.1f}%")
        
        with col4:
            st.metric("Total Equity", f"${total_equity:,.0f}")
            st.metric("Total Debt", f"${total_debt:,.0f}")
        
        # Portfolio composition
        st.markdown("---")
        st.subheader("📊 Portfolio Composition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # By property type
            if 'property_type' in properties_df.columns:
                type_values = properties_df.groupby('property_type')['price'].sum()
                fig = px.pie(
                    values=type_values.values,
                    names=type_values.index,
                    title="Portfolio Value by Property Type"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # By individual property
            fig = px.bar(
                properties_df,
                x='address',
                y='price',
                title="Individual Property Values"
            )
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance over time (aggregate)
        st.markdown("---")
        st.subheader("📈 Portfolio Performance Over Time")
        
        # Generate aggregate performance data
        all_performance_data = []
        for _, prop in properties_df.iterrows():
            prop_performance = generate_performance_data(prop)
            prop_performance['property_id'] = prop['address']
            all_performance_data.append(prop_performance)
        
        if all_performance_data:
            # Combine all property data
            combined_performance = pd.concat(all_performance_data, ignore_index=True)
            
            # Aggregate by date
            portfolio_performance = combined_performance.groupby('date').agg({
                'property_value': 'sum',
                'monthly_rent': 'sum',
                'monthly_cash_flow': 'sum',
                'annual_cash_flow': 'sum'
            }).reset_index()
            
            # Calculate total return
            initial_value = portfolio_performance['property_value'].iloc[0]
            portfolio_performance['total_return'] = (
                (portfolio_performance['property_value'] - initial_value) / initial_value * 100
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Portfolio value over time
                fig = px.line(
                    portfolio_performance,
                    x='date',
                    y='property_value',
                    title="Portfolio Value Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Cash flow over time
                fig = px.line(
                    portfolio_performance,
                    x='date',
                    y='monthly_cash_flow',
                    title="Monthly Cash Flow Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Total return chart
            fig = px.line(
                portfolio_performance,
                x='date',
                y='total_return',
                title="Total Return Over Time (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🏡 Individual Property Performance")
        
        # Property selection
        selected_property = st.selectbox(
            "Select a property to analyze:",
            properties_df['address'].tolist()
        )
        
        if selected_property:
            property_data = properties_df[properties_df['address'] == selected_property].iloc[0]
            
            st.markdown(f"**Analyzing: {property_data['address']}**")
            
            # Generate performance data for selected property
            performance_data = generate_performance_data(property_data)
            
            # Current vs initial metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Current Performance**")
                if not performance_data.empty:
                    current_value = performance_data['property_value'].iloc[-1]
                    current_rent = performance_data['monthly_rent'].iloc[-1]
                    current_cash_flow = performance_data['monthly_cash_flow'].iloc[-1]
                    
                    st.metric("Current Value", f"${current_value:,.0f}")
                    st.metric("Current Rent", f"${current_rent:,.0f}")
                    st.metric("Current Cash Flow", f"${current_cash_flow:,.0f}")
                else:
                    st.write("No performance data available")
            
            with col2:
                st.markdown("**Performance vs Initial**")
                if not performance_data.empty:
                    initial_value = performance_data['property_value'].iloc[0]
                    initial_rent = performance_data['monthly_rent'].iloc[0]
                    
                    value_change = current_value - initial_value
                    rent_change = current_rent - initial_rent
                    
                    st.metric("Value Change", f"${value_change:,.0f}", 
                             delta=f"{(value_change/initial_value)*100:.1f}%")
                    st.metric("Rent Change", f"${rent_change:,.0f}", 
                             delta=f"{(rent_change/initial_rent)*100:.1f}%")
                    
                    total_return = performance_data['total_return'].iloc[-1]
                    st.metric("Total Return", f"{total_return:.1f}%")
            
            with col3:
                st.markdown("**Key Metrics**")
                current_metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(property_data)
                
                st.metric("Current ROI", f"{current_metrics.get('roi', 0):.1f}%")
                st.metric("Current Cap Rate", f"{current_metrics.get('cap_rate', 0):.1f}%")
                st.metric("Cash-on-Cash", f"{current_metrics.get('cash_on_cash', 0):.1f}%")
            
            # Performance charts
            if not performance_data.empty:
                st.markdown("---")
                st.subheader("📊 Performance Charts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Property value over time
                    fig = px.line(
                        performance_data,
                        x='date',
                        y='property_value',
                        title="Property Value Over Time"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Monthly cash flow
                    fig = px.line(
                        performance_data,
                        x='date',
                        y='monthly_cash_flow',
                        title="Monthly Cash Flow Over Time"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Combined performance chart
                fig = go.Figure()
                
                # Add appreciation line
                fig.add_trace(go.Scatter(
                    x=performance_data['date'],
                    y=performance_data['appreciation'],
                    mode='lines',
                    name='Appreciation (%)',
                    line=dict(color='blue')
                ))
                
                # Add total return line
                fig.add_trace(go.Scatter(
                    x=performance_data['date'],
                    y=performance_data['total_return'],
                    mode='lines',
                    name='Total Return (%)',
                    line=dict(color='green')
                ))
                
                fig.update_layout(
                    title="Appreciation vs Total Return",
                    xaxis_title="Date",
                    yaxis_title="Return (%)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📈 Performance Metrics Analysis")
        
        # Calculate performance metrics for all properties
        performance_summary = []
        
        for _, prop in properties_df.iterrows():
            performance_data = generate_performance_data(prop)
            current_metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
            
            if not performance_data.empty:
                current_value = performance_data['property_value'].iloc[-1]
                initial_value = performance_data['property_value'].iloc[0]
                total_return = performance_data['total_return'].iloc[-1]
                appreciation = performance_data['appreciation'].iloc[-1]
                
                # Calculate annualized returns
                years_held = len(performance_data) / 12
                if years_held > 0:
                    annualized_return = (((current_value / initial_value) ** (1/years_held)) - 1) * 100
                else:
                    annualized_return = 0
                
                performance_summary.append({
                    'Property': prop['address'],
                    'Initial Value': initial_value,
                    'Current Value': current_value,
                    'Total Return': total_return,
                    'Appreciation': appreciation,
                    'Annualized Return': annualized_return,
                    'ROI': current_metrics.get('roi', 0),
                    'Cap Rate': current_metrics.get('cap_rate', 0),
                    'Cash-on-Cash': current_metrics.get('cash_on_cash', 0),
                    'Years Held': years_held
                })
        
        if performance_summary:
            perf_df = pd.DataFrame(performance_summary)
            
            # Performance metrics table
            st.markdown("**Performance Summary**")
            
            display_df = perf_df.copy()
            display_df['Initial Value'] = display_df['Initial Value'].apply(lambda x: f"${x:,.0f}")
            display_df['Current Value'] = display_df['Current Value'].apply(lambda x: f"${x:,.0f}")
            display_df['Total Return'] = display_df['Total Return'].apply(lambda x: f"{x:.1f}%")
            display_df['Appreciation'] = display_df['Appreciation'].apply(lambda x: f"{x:.1f}%")
            display_df['Annualized Return'] = display_df['Annualized Return'].apply(lambda x: f"{x:.1f}%")
            display_df['ROI'] = display_df['ROI'].apply(lambda x: f"{x:.1f}%")
            display_df['Cap Rate'] = display_df['Cap Rate'].apply(lambda x: f"{x:.1f}%")
            display_df['Cash-on-Cash'] = display_df['Cash-on-Cash'].apply(lambda x: f"{x:.1f}%")
            display_df['Years Held'] = display_df['Years Held'].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Performance analysis
            st.markdown("---")
            st.subheader("📊 Performance Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Total return comparison
                fig = px.bar(
                    perf_df,
                    x='Property',
                    y='Total Return',
                    title="Total Return by Property"
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Annualized return vs ROI
                fig = px.scatter(
                    perf_df,
                    x='ROI',
                    y='Annualized Return',
                    text='Property',
                    title="ROI vs Annualized Return"
                )
                fig.update_traces(textposition="top center")
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance benchmarks
            st.markdown("---")
            st.subheader("🎯 Performance Benchmarks")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_total_return = perf_df['Total Return'].mean()
                st.metric("Average Total Return", f"{avg_total_return:.1f}%")
                
                if avg_total_return > 15:
                    st.success("🎉 Excellent Performance")
                elif avg_total_return > 10:
                    st.info("👍 Good Performance")
                else:
                    st.warning("📈 Below Average")
            
            with col2:
                avg_annualized = perf_df['Annualized Return'].mean()
                st.metric("Average Annualized Return", f"{avg_annualized:.1f}%")
                
                if avg_annualized > 12:
                    st.success("🚀 Outstanding")
                elif avg_annualized > 8:
                    st.info("✅ Good")
                else:
                    st.warning("⚠️ Below Target")
            
            with col3:
                top_performer = perf_df.loc[perf_df['Total Return'].idxmax()]
                st.metric("Top Performer", f"{top_performer['Total Return']:.1f}%")
                st.write(f"Property: {top_performer['Property']}")
    
    with tab4:
        st.subheader("📋 Performance Reports")
        
        # Report generation options
        report_type = st.selectbox(
            "Select Report Type:",
            ["Monthly Performance", "Quarterly Summary", "Annual Review", "Property Comparison"]
        )
        
        report_period = st.selectbox(
            "Select Period:",
            ["Last 3 Months", "Last 6 Months", "Last 12 Months", "Year to Date", "All Time"]
        )
        
        if st.button("Generate Report", type="primary"):
            st.markdown("---")
            st.subheader(f"📊 {report_type} Report - {report_period}")
            
            # Generate report based on selections
            if report_type == "Monthly Performance":
                st.markdown("**Monthly Performance Summary**")
                
                # Create monthly performance data
                monthly_data = []
                for _, prop in properties_df.iterrows():
                    performance_data = generate_performance_data(prop)
                    if not performance_data.empty:
                        # Get last 12 months
                        recent_data = performance_data.tail(12)
                        for _, row in recent_data.iterrows():
                            monthly_data.append({
                                'Property': prop['address'],
                                'Month': row['date'].strftime('%Y-%m'),
                                'Value': row['property_value'],
                                'Rent': row['monthly_rent'],
                                'Cash Flow': row['monthly_cash_flow'],
                                'Return': row['total_return']
                            })
                
                if monthly_data:
                    monthly_df = pd.DataFrame(monthly_data)
                    
                    # Monthly cash flow chart
                    fig = px.line(
                        monthly_df,
                        x='Month',
                        y='Cash Flow',
                        color='Property',
                        title="Monthly Cash Flow by Property"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Monthly performance table
                    pivot_table = monthly_df.pivot(index='Month', columns='Property', values='Cash Flow')
                    st.dataframe(pivot_table, use_container_width=True)
            
            elif report_type == "Quarterly Summary":
                st.markdown("**Quarterly Performance Summary**")
                
                # Portfolio summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Properties", len(properties_df))
                    st.metric("Total Portfolio Value", f"${properties_df['price'].sum():,.0f}")
                
                with col2:
                    st.metric("Total Monthly Rent", f"${properties_df['monthly_rent'].sum():,.0f}")
                    st.metric("Total Monthly Expenses", f"${properties_df['monthly_expenses'].sum():,.0f}")
                
                with col3:
                    net_cash_flow = properties_df['monthly_rent'].sum() - properties_df['monthly_expenses'].sum()
                    st.metric("Net Monthly Cash Flow", f"${net_cash_flow:,.0f}")
                    st.metric("Quarterly Cash Flow", f"${net_cash_flow * 3:,.0f}")
            
            elif report_type == "Annual Review":
                st.markdown("**Annual Performance Review**")
                
                # Calculate annual performance for each property
                annual_performance = []
                for _, prop in properties_df.iterrows():
                    performance_data = generate_performance_data(prop)
                    if not performance_data.empty:
                        current_value = performance_data['property_value'].iloc[-1]
                        initial_value = performance_data['property_value'].iloc[0]
                        total_return = performance_data['total_return'].iloc[-1]
                        
                        annual_performance.append({
                            'Property': prop['address'],
                            'Initial Value': initial_value,
                            'Current Value': current_value,
                            'Value Change': current_value - initial_value,
                            'Total Return': total_return,
                            'Annual Cash Flow': prop['monthly_rent'] * 12 - prop['monthly_expenses'] * 12
                        })
                
                if annual_performance:
                    annual_df = pd.DataFrame(annual_performance)
                    
                    # Format for display
                    display_annual = annual_df.copy()
                    display_annual['Initial Value'] = display_annual['Initial Value'].apply(lambda x: f"${x:,.0f}")
                    display_annual['Current Value'] = display_annual['Current Value'].apply(lambda x: f"${x:,.0f}")
                    display_annual['Value Change'] = display_annual['Value Change'].apply(lambda x: f"${x:,.0f}")
                    display_annual['Total Return'] = display_annual['Total Return'].apply(lambda x: f"{x:.1f}%")
                    display_annual['Annual Cash Flow'] = display_annual['Annual Cash Flow'].apply(lambda x: f"${x:,.0f}")
                    
                    st.dataframe(display_annual, use_container_width=True)
                    
                    # Annual performance chart
                    fig = px.bar(
                        annual_df,
                        x='Property',
                        y='Total Return',
                        title="Annual Total Return by Property"
                    )
                    fig.update_xaxis(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif report_type == "Property Comparison":
                st.markdown("**Property Comparison Report**")
                
                # Create comparison metrics
                comparison_data = []
                for _, prop in properties_df.iterrows():
                    metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                    performance_data = generate_performance_data(prop)
                    
                    if not performance_data.empty:
                        total_return = performance_data['total_return'].iloc[-1]
                    else:
                        total_return = 0
                    
                    comparison_data.append({
                        'Property': prop['address'],
                        'Type': prop['property_type'],
                        'Price': prop['price'],
                        'Monthly Rent': prop['monthly_rent'],
                        'ROI': metrics.get('roi', 0),
                        'Cap Rate': metrics.get('cap_rate', 0),
                        'Cash Flow': metrics.get('monthly_cash_flow', 0),
                        'Total Return': total_return
                    })
                
                if comparison_data:
                    comp_df = pd.DataFrame(comparison_data)
                    
                    # Ranking by different metrics
                    st.markdown("**Property Rankings**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Top Properties by ROI**")
                        roi_ranking = comp_df.nlargest(5, 'ROI')[['Property', 'ROI']]
                        st.dataframe(roi_ranking, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Top Properties by Cash Flow**")
                        cash_flow_ranking = comp_df.nlargest(5, 'Cash Flow')[['Property', 'Cash Flow']]
                        st.dataframe(cash_flow_ranking, use_container_width=True)
                    
                    # Comparison visualization
                    fig = px.scatter(
                        comp_df,
                        x='ROI',
                        y='Cap Rate',
                        size='Price',
                        color='Type',
                        text='Property',
                        title="Property Performance Comparison"
                    )
                    fig.update_traces(textposition="top center")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        st.markdown("---")
        st.subheader("📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to CSV"):
                # Create comprehensive export data
                export_data = []
                for _, prop in properties_df.iterrows():
                    metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(prop)
                    performance_data = generate_performance_data(prop)
                    
                    if not performance_data.empty:
                        current_value = performance_data['property_value'].iloc[-1]
                        total_return = performance_data['total_return'].iloc[-1]
                    else:
                        current_value = prop['price']
                        total_return = 0
                    
                    export_data.append({
                        'Address': prop['address'],
                        'Property Type': prop['property_type'],
                        'Purchase Price': prop['price'],
                        'Current Value': current_value,
                        'Monthly Rent': prop['monthly_rent'],
                        'Monthly Expenses': prop['monthly_expenses'],
                        'ROI': metrics.get('roi', 0),
                        'Cap Rate': metrics.get('cap_rate', 0),
                        'Monthly Cash Flow': metrics.get('monthly_cash_flow', 0),
                        'Total Return': total_return,
                        'Date Acquired': prop.get('date_acquired', '')
                    })
                
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"property_performance_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Generate PDF Report"):
                st.info("PDF generation feature coming soon! For now, use the print function in your browser.")
