import numpy as np
import pandas as pd
from datetime import datetime

class PropertyCalculator:
    """Handles all property financial calculations"""
    
    def __init__(self):
        pass
    
    def calculate_mortgage_payment(self, principal, annual_rate, years):
        """Calculate monthly mortgage payment using standard formula"""
        if annual_rate == 0:
            return principal / (years * 12)
        
        monthly_rate = annual_rate / 100 / 12
        num_payments = years * 12
        
        payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return payment
    
    def calculate_cap_rate(self, net_operating_income, property_value):
        """Calculate capitalization rate"""
        if property_value == 0:
            return 0
        return (net_operating_income / property_value) * 100
    
    def calculate_cash_on_cash_return(self, annual_cash_flow, initial_cash_investment):
        """Calculate cash-on-cash return"""
        if initial_cash_investment == 0:
            return 0
        return (annual_cash_flow / initial_cash_investment) * 100
    
    def calculate_roi(self, annual_profit, total_investment):
        """Calculate return on investment"""
        if total_investment == 0:
            return 0
        return (annual_profit / total_investment) * 100
    
    def calculate_dscr(self, net_operating_income, annual_debt_service):
        """Calculate debt service coverage ratio"""
        if annual_debt_service == 0:
            return float('inf')
        return net_operating_income / annual_debt_service
    
    def calculate_grm(self, property_value, annual_rent):
        """Calculate gross rent multiplier"""
        if annual_rent == 0:
            return 0
        return property_value / annual_rent
    
    def calculate_ltv(self, loan_amount, property_value):
        """Calculate Loan-to-Value ratio"""
        if property_value == 0:
            return 0
        return (loan_amount / property_value) * 100
    
    def calculate_one_percent_rule(self, property_value, monthly_rent):
        """Check if property passes 1% rule"""
        return monthly_rent >= (property_value * 0.01)
    
    def calculate_metrics(self, property_data):
        """Calculate comprehensive property metrics"""
        # Extract data
        purchase_price = property_data.get('purchase_price', 0)
        down_payment = property_data.get('down_payment', 0)
        loan_amount = property_data.get('loan_amount', 0)
        interest_rate = property_data.get('interest_rate', 0)
        loan_term = property_data.get('loan_term', 30)
        annual_rent = property_data.get('annual_rent', 0)
        annual_expenses = property_data.get('annual_expenses', 0)
        vacancy_rate = property_data.get('vacancy_rate', 0)
        
        # Calculate basic metrics
        vacancy_loss = annual_rent * (vacancy_rate / 100)
        effective_gross_income = annual_rent - vacancy_loss
        net_operating_income = effective_gross_income - annual_expenses
        
        # Calculate mortgage payment
        monthly_payment = 0
        annual_debt_service = 0
        if loan_amount > 0 and interest_rate > 0:
            monthly_payment = self.calculate_mortgage_payment(loan_amount, interest_rate, loan_term)
            annual_debt_service = monthly_payment * 12
        
        # Calculate cash flow
        annual_cash_flow = net_operating_income - annual_debt_service
        monthly_cash_flow = annual_cash_flow / 12
        
        # Calculate key metrics
        cap_rate = self.calculate_cap_rate(net_operating_income, purchase_price)
        cash_on_cash = self.calculate_cash_on_cash_return(annual_cash_flow, down_payment)
        roi = self.calculate_roi(annual_cash_flow, down_payment)
        dscr = self.calculate_dscr(net_operating_income, annual_debt_service)
        grm = self.calculate_grm(purchase_price, annual_rent)
        ltv = self.calculate_ltv(loan_amount, purchase_price)
        one_percent_rule = self.calculate_one_percent_rule(purchase_price, annual_rent / 12)
        
        return {
            'purchase_price': purchase_price,
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'annual_rent': annual_rent,
            'annual_expenses': annual_expenses,
            'vacancy_loss': vacancy_loss,
            'effective_gross_income': effective_gross_income,
            'net_operating_income': net_operating_income,
            'monthly_payment': monthly_payment,
            'annual_debt_service': annual_debt_service,
            'annual_cash_flow': annual_cash_flow,
            'monthly_cash_flow': monthly_cash_flow,
            'cap_rate': cap_rate,
            'cash_on_cash': cash_on_cash,
            'roi': roi,
            'dscr': dscr,
            'grm': grm,
            'ltv': ltv,
            'one_percent_rule': one_percent_rule
        }
    
    def calculate_comprehensive_metrics(self, property_data):
        """Calculate metrics from property dataframe row"""
        # Convert property data to calculation format
        calc_data = {
            'purchase_price': property_data.get('price', 0),
            'down_payment': property_data.get('down_payment', 0),
            'loan_amount': property_data.get('loan_amount', 0),
            'interest_rate': property_data.get('interest_rate', 0),
            'loan_term': property_data.get('loan_term', 30),
            'annual_rent': property_data.get('monthly_rent', 0) * 12,
            'annual_expenses': property_data.get('monthly_expenses', 0) * 12,
            'vacancy_rate': 5  # Default 5% vacancy rate
        }
        
        return self.calculate_metrics(calc_data)
    
    def calculate_breakeven_rent(self, property_data):
        """Calculate breakeven rent needed"""
        annual_expenses = property_data.get('monthly_expenses', 0) * 12
        
        # Calculate mortgage payment
        loan_amount = property_data.get('loan_amount', 0)
        interest_rate = property_data.get('interest_rate', 0)
        loan_term = property_data.get('loan_term', 30)
        
        annual_debt_service = 0
        if loan_amount > 0 and interest_rate > 0:
            monthly_payment = self.calculate_mortgage_payment(loan_amount, interest_rate, loan_term)
            annual_debt_service = monthly_payment * 12
        
        # Breakeven rent (including vacancy buffer)
        vacancy_rate = 0.05  # 5% vacancy
        breakeven_annual_rent = (annual_expenses + annual_debt_service) / (1 - vacancy_rate)
        
        return breakeven_annual_rent / 12  # Return monthly rent
    
    def calculate_ltv_ratio(self, loan_amount, property_value):
        """Calculate loan-to-value ratio"""
        if property_value == 0:
            return 0
        return (loan_amount / property_value) * 100
    
    def calculate_operating_expense_ratio(self, annual_expenses, annual_rent):
        """Calculate operating expense ratio"""
        if annual_rent == 0:
            return 0
        return (annual_expenses / annual_rent) * 100
    
    def calculate_projected_cash_flow(self, property_data, years, rent_growth_rate=0.03, expense_growth_rate=0.02):
        """Calculate projected cash flow over multiple years"""
        current_metrics = self.calculate_comprehensive_metrics(property_data)
        
        projections = []
        for year in range(1, years + 1):
            # Project rent and expenses
            projected_rent = property_data.get('monthly_rent', 0) * (1 + rent_growth_rate) ** year
            projected_expenses = property_data.get('monthly_expenses', 0) * (1 + expense_growth_rate) ** year
            
            # Calculate projected cash flow
            annual_rent = projected_rent * 12
            annual_expenses = projected_expenses * 12
            
            # Mortgage payment stays the same
            monthly_payment = current_metrics['monthly_payment']
            annual_debt_service = monthly_payment * 12
            
            # Net cash flow
            vacancy_loss = annual_rent * 0.05  # 5% vacancy
            effective_gross_income = annual_rent - vacancy_loss
            net_operating_income = effective_gross_income - annual_expenses
            annual_cash_flow = net_operating_income - annual_debt_service
            
            projections.append({
                'year': year,
                'monthly_rent': projected_rent,
                'monthly_expenses': projected_expenses,
                'annual_cash_flow': annual_cash_flow,
                'monthly_cash_flow': annual_cash_flow / 12,
                'net_operating_income': net_operating_income
            })
        
        return projections
    
    def calculate_appreciation_scenarios(self, property_data, years, appreciation_rates):
        """Calculate property value under different appreciation scenarios"""
        current_value = property_data.get('price', 0)
        
        scenarios = {}
        for rate in appreciation_rates:
            rate_name = f"{rate*100:.1f}%"
            projected_values = []
            
            for year in range(1, years + 1):
                future_value = current_value * (1 + rate) ** year
                projected_values.append({
                    'year': year,
                    'value': future_value,
                    'appreciation_rate': rate
                })
            
            scenarios[rate_name] = projected_values
        
        return scenarios
    
    def calculate_sensitivity_analysis(self, property_data, variables):
        """Perform sensitivity analysis on key variables"""
        base_metrics = self.calculate_comprehensive_metrics(property_data)
        base_roi = base_metrics['roi']
        
        sensitivity_results = {}
        
        for variable, changes in variables.items():
            results = []
            
            for change in changes:
                modified_data = property_data.copy()
                
                if variable == 'rent':
                    modified_data['monthly_rent'] = property_data['monthly_rent'] * (1 + change)
                elif variable == 'expenses':
                    modified_data['monthly_expenses'] = property_data['monthly_expenses'] * (1 + change)
                elif variable == 'price':
                    modified_data['price'] = property_data['price'] * (1 + change)
                elif variable == 'interest_rate':
                    modified_data['interest_rate'] = property_data.get('interest_rate', 0) + change
                
                new_metrics = self.calculate_comprehensive_metrics(modified_data)
                roi_change = new_metrics['roi'] - base_roi
                
                results.append({
                    'change': change,
                    'new_roi': new_metrics['roi'],
                    'roi_change': roi_change
                })
            
            sensitivity_results[variable] = results
        
        return sensitivity_results
