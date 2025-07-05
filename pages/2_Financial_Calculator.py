import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Financial Calculator",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Financial Calculator")
st.markdown("Analyze property investments with detailed financial calculations.")

# Initialize session state
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

if 'property_calculator' not in st.session_state:
    from utils.calculations import PropertyCalculator
    st.session_state.property_calculator = PropertyCalculator()

# Tabs for different calculation types
tab1, tab2, tab3 = st.tabs(["Quick Analysis", "Detailed Analysis", "Scenario Comparison"])

with tab1:
    st.subheader("Quick Property Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Property Details**")
        purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, value=300000.0, step=1000.0)
        down_payment_pct = st.slider("Down Payment (%)", min_value=0, max_value=100, value=20)
        down_payment = purchase_price * (down_payment_pct / 100)
        st.write(f"Down Payment: ${down_payment:,.0f}")
        
        loan_amount = purchase_price - down_payment
        st.write(f"Loan Amount: ${loan_amount:,.0f}")
        
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0, value=6.5, step=0.25)
        loan_term = st.number_input("Loan Term (years)", min_value=1, max_value=50, value=30)
        
    with col2:
        st.markdown("**Income & Expenses**")
        monthly_rent = st.number_input("Monthly Rent ($)", min_value=0.0, value=2500.0, step=50.0)
        annual_rent = monthly_rent * 12
        st.write(f"Annual Rent: ${annual_rent:,.0f}")
        
        # Operating expenses
        property_taxes = st.number_input("Annual Property Taxes ($)", min_value=0.0, value=3600.0, step=100.0)
        insurance = st.number_input("Annual Insurance ($)", min_value=0.0, value=1200.0, step=100.0)
        maintenance = st.number_input("Annual Maintenance ($)", min_value=0.0, value=3000.0, step=100.0)
        property_mgmt = st.number_input("Property Management ($)", min_value=0.0, value=2400.0, step=100.0)
        vacancy_rate = st.slider("Vacancy Rate (%)", min_value=0, max_value=30, value=5)
        
        total_expenses = property_taxes + insurance + maintenance + property_mgmt
        vacancy_loss = annual_rent * (vacancy_rate / 100)
        net_operating_income = annual_rent - vacancy_loss - total_expenses
        
        st.write(f"Total Operating Expenses: ${total_expenses:,.0f}")
        st.write(f"Vacancy Loss: ${vacancy_loss:,.0f}")
        st.write(f"Net Operating Income: ${net_operating_income:,.0f}")
    
    # Calculate key metrics
    if st.button("Calculate Metrics", type="primary"):
        results = st.session_state.property_calculator.calculate_metrics({
            'purchase_price': purchase_price,
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'loan_term': loan_term,
            'annual_rent': annual_rent,
            'annual_expenses': total_expenses,
            'vacancy_rate': vacancy_rate
        })
        
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Key metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cap Rate", f"{results['cap_rate']:.2f}%")
            st.metric("Cash Flow", f"${results['monthly_cash_flow']:,.0f}/month")
            
        with col2:
            st.metric("ROI", f"{results['roi']:.2f}%")
            st.metric("Cash-on-Cash", f"{results['cash_on_cash']:.2f}%")
            
        with col3:
            st.metric("DSCR", f"{results['dscr']:.2f}")
            st.metric("Monthly Payment", f"${results['monthly_payment']:,.0f}")
            
        with col4:
            st.metric("Gross Rent Multiplier", f"{results['grm']:.1f}")
            st.metric("1% Rule", "✅ Pass" if results['one_percent_rule'] else "❌ Fail")
        
        # Investment summary
        st.markdown("---")
        st.subheader("💡 Investment Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if results['roi'] > 12:
                st.success("🎯 **Excellent ROI** - This property shows strong returns!")
            elif results['roi'] > 8:
                st.info("👍 **Good ROI** - This property meets minimum return criteria.")
            else:
                st.warning("⚠️ **Low ROI** - Consider negotiating price or increasing rents.")
                
            if results['cash_on_cash'] > 8:
                st.success("💰 **Strong Cash Returns** - Good cash-on-cash return!")
            elif results['cash_on_cash'] > 4:
                st.info("📊 **Moderate Cash Returns** - Acceptable cash flow.")
            else:
                st.warning("🔍 **Low Cash Returns** - Review financing options.")
        
        with col2:
            if results['dscr'] > 1.25:
                st.success("🛡️ **Safe Debt Coverage** - Low risk of payment issues.")
            elif results['dscr'] > 1.0:
                st.info("⚖️ **Adequate Coverage** - Monitor cash flow closely.")
            else:
                st.error("🚨 **Insufficient Coverage** - High risk investment!")
                
            if results['one_percent_rule']:
                st.success("📏 **Meets 1% Rule** - Good income-to-price ratio.")
            else:
                st.info("📏 **Below 1% Rule** - Common in appreciating markets.")

with tab2:
    st.subheader("Detailed Financial Analysis")
    
    # Select property from existing portfolio
    properties_df = st.session_state.data_manager.get_properties()
    
    if not properties_df.empty:
        selected_property = st.selectbox(
            "Select a property for detailed analysis:",
            options=["New Property"] + properties_df['address'].tolist()
        )
        
        if selected_property != "New Property":
            property_data = properties_df[properties_df['address'] == selected_property].iloc[0]
            
            # Display property details
            st.markdown(f"**Analyzing: {property_data['address']}**")
            
            # Calculate and display comprehensive metrics
            metrics = st.session_state.property_calculator.calculate_comprehensive_metrics(property_data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Return Metrics**")
                st.metric("ROI", f"{metrics.get('roi', 0):.2f}%")
                st.metric("Cap Rate", f"{metrics.get('cap_rate', 0):.2f}%")
                st.metric("Cash-on-Cash", f"{metrics.get('cash_on_cash', 0):.2f}%")
                
            with col2:
                st.markdown("**Cash Flow Analysis**")
                st.metric("Monthly Cash Flow", f"${metrics.get('monthly_cash_flow', 0):,.0f}")
                st.metric("Annual Cash Flow", f"${metrics.get('annual_cash_flow', 0):,.0f}")
                st.metric("Break-even Rent", f"${metrics.get('breakeven_rent', 0):,.0f}")
                
            with col3:
                st.markdown("**Risk Metrics**")
                st.metric("DSCR", f"{metrics.get('dscr', 0):.2f}")
                st.metric("Loan-to-Value", f"{metrics.get('ltv', 0):.1f}%")
                st.metric("Operating Expense Ratio", f"{metrics.get('oer', 0):.1f}%")
            
            # Cash flow projection chart
            st.markdown("---")
            st.subheader("📈 10-Year Cash Flow Projection")
            
            years = list(range(1, 11))
            cash_flows = []
            
            for year in years:
                # Assume 3% annual rent increase and 2% expense increase
                projected_rent = property_data['monthly_rent'] * 12 * (1.03 ** year)
                projected_expenses = property_data['monthly_expenses'] * 12 * (1.02 ** year)
                annual_cash_flow = projected_rent - projected_expenses - (metrics.get('monthly_payment', 0) * 12)
                cash_flows.append(annual_cash_flow)
            
            fig = px.line(x=years, y=cash_flows, title="Projected Annual Cash Flow")
            fig.update_xaxis(title="Year")
            fig.update_yaxis(title="Cash Flow ($)")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Select a property from your portfolio or add new properties in the Property Input page.")
    else:
        st.info("No properties available for analysis. Add properties in the Property Input page.")

with tab3:
    st.subheader("Scenario Comparison")
    
    st.markdown("Compare different scenarios for the same property or different properties.")
    
    # Scenario inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Scenario A**")
        price_a = st.number_input("Purchase Price A ($)", min_value=0.0, value=300000.0, step=1000.0, key="price_a")
        rent_a = st.number_input("Monthly Rent A ($)", min_value=0.0, value=2500.0, step=50.0, key="rent_a")
        down_a = st.number_input("Down Payment A ($)", min_value=0.0, value=60000.0, step=1000.0, key="down_a")
        rate_a = st.number_input("Interest Rate A (%)", min_value=0.0, value=6.5, step=0.25, key="rate_a")
        
    with col2:
        st.markdown("**Scenario B**")
        price_b = st.number_input("Purchase Price B ($)", min_value=0.0, value=320000.0, step=1000.0, key="price_b")
        rent_b = st.number_input("Monthly Rent B ($)", min_value=0.0, value=2600.0, step=50.0, key="rent_b")
        down_b = st.number_input("Down Payment B ($)", min_value=0.0, value=64000.0, step=1000.0, key="down_b")
        rate_b = st.number_input("Interest Rate B (%)", min_value=0.0, value=7.0, step=0.25, key="rate_b")
    
    if st.button("Compare Scenarios", type="primary"):
        # Calculate metrics for both scenarios
        scenario_a = {
            'purchase_price': price_a,
            'down_payment': down_a,
            'loan_amount': price_a - down_a,
            'interest_rate': rate_a,
            'loan_term': 30,
            'annual_rent': rent_a * 12,
            'annual_expenses': rent_a * 12 * 0.35,  # Assume 35% expense ratio
            'vacancy_rate': 5
        }
        
        scenario_b = {
            'purchase_price': price_b,
            'down_payment': down_b,
            'loan_amount': price_b - down_b,
            'interest_rate': rate_b,
            'loan_term': 30,
            'annual_rent': rent_b * 12,
            'annual_expenses': rent_b * 12 * 0.35,
            'vacancy_rate': 5
        }
        
        results_a = st.session_state.property_calculator.calculate_metrics(scenario_a)
        results_b = st.session_state.property_calculator.calculate_metrics(scenario_b)
        
        # Comparison table
        st.markdown("---")
        st.subheader("📊 Scenario Comparison")
        
        comparison_data = {
            'Metric': ['Purchase Price', 'Down Payment', 'ROI (%)', 'Cap Rate (%)', 
                      'Cash Flow (Monthly)', 'Cash-on-Cash (%)', 'DSCR'],
            'Scenario A': [
                f"${price_a:,.0f}",
                f"${down_a:,.0f}",
                f"{results_a['roi']:.2f}%",
                f"{results_a['cap_rate']:.2f}%",
                f"${results_a['monthly_cash_flow']:,.0f}",
                f"{results_a['cash_on_cash']:.2f}%",
                f"{results_a['dscr']:.2f}"
            ],
            'Scenario B': [
                f"${price_b:,.0f}",
                f"${down_b:,.0f}",
                f"{results_b['roi']:.2f}%",
                f"{results_b['cap_rate']:.2f}%",
                f"${results_b['monthly_cash_flow']:,.0f}",
                f"{results_b['cash_on_cash']:.2f}%",
                f"{results_b['dscr']:.2f}"
            ],
            'Winner': []
        }
        
        # Determine winners
        winners = []
        if results_a['roi'] > results_b['roi']:
            winners.extend(['', '', 'A', '', '', '', ''])
        else:
            winners.extend(['', '', 'B', '', '', '', ''])
            
        if results_a['cap_rate'] > results_b['cap_rate']:
            winners[3] = 'A'
        else:
            winners[3] = 'B'
            
        if results_a['monthly_cash_flow'] > results_b['monthly_cash_flow']:
            winners[4] = 'A'
        else:
            winners[4] = 'B'
            
        if results_a['cash_on_cash'] > results_b['cash_on_cash']:
            winners[5] = 'A'
        else:
            winners[5] = 'B'
            
        if results_a['dscr'] > results_b['dscr']:
            winners[6] = 'A'
        else:
            winners[6] = 'B'
        
        comparison_data['Winner'] = winners
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Visual comparison
        metrics_names = ['ROI', 'Cap Rate', 'Cash-on-Cash', 'DSCR']
        scenario_a_values = [results_a['roi'], results_a['cap_rate'], results_a['cash_on_cash'], results_a['dscr']]
        scenario_b_values = [results_b['roi'], results_b['cap_rate'], results_b['cash_on_cash'], results_b['dscr']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Scenario A', x=metrics_names, y=scenario_a_values))
        fig.add_trace(go.Bar(name='Scenario B', x=metrics_names, y=scenario_b_values))
        
        fig.update_layout(title="Scenario Comparison", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendation
        st.markdown("---")
        st.subheader("💡 Recommendation")
        
        # Simple scoring system
        score_a = (results_a['roi'] + results_a['cap_rate'] + results_a['cash_on_cash'] + results_a['dscr']) / 4
        score_b = (results_b['roi'] + results_b['cap_rate'] + results_b['cash_on_cash'] + results_b['dscr']) / 4
        
        if score_a > score_b:
            st.success("🎯 **Scenario A** appears to be the better investment based on overall metrics.")
        elif score_b > score_a:
            st.success("🎯 **Scenario B** appears to be the better investment based on overall metrics.")
        else:
            st.info("🤔 Both scenarios are very similar. Consider other factors like location, condition, and growth potential.")
