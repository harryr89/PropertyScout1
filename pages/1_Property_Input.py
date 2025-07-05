import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="Property Input",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Property Input & Management")
st.markdown("Add new properties or manage existing ones in your portfolio.")

# Initialize session state
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["Add New Property", "Manage Properties", "Bulk Import"])

with tab1:
    st.subheader("Add New Property")
    
    with st.form("property_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Basic property information
            st.markdown("**Basic Information**")
            address = st.text_input("Property Address*", placeholder="123 Main St, City, State")
            property_type = st.selectbox("Property Type*", 
                                       ["Single Family", "Multi-Family", "Condo", "Townhouse", 
                                        "Commercial", "Land", "Other"])
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=20, value=3)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=20.0, value=2.0, step=0.5)
            square_feet = st.number_input("Square Feet", min_value=0, value=1500)
            year_built = st.number_input("Year Built", min_value=1800, max_value=2025, value=2000)
            
        with col2:
            # Financial information
            st.markdown("**Financial Details**")
            price = st.number_input("Purchase Price ($)*", min_value=0.0, value=300000.0, step=1000.0)
            down_payment = st.number_input("Down Payment ($)", min_value=0.0, value=60000.0, step=1000.0)
            loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, value=240000.0, step=1000.0)
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0, value=6.5, step=0.25)
            loan_term = st.number_input("Loan Term (years)", min_value=1, max_value=50, value=30)
            
            # Income and expenses
            st.markdown("**Income & Expenses**")
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0.0, value=2500.0, step=50.0)
            monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0.0, value=500.0, step=50.0)
            
        # Additional details
        st.markdown("**Additional Information**")
        col3, col4 = st.columns(2)
        
        with col3:
            neighborhood = st.text_input("Neighborhood", placeholder="Downtown, Suburb, etc.")
            school_district = st.text_input("School District")
            
        with col4:
            date_acquired = st.date_input("Date Acquired", datetime.now())
            notes = st.text_area("Notes", placeholder="Any additional notes about this property...")
        
        # Submit button
        submitted = st.form_submit_button("Add Property", type="primary")
        
        if submitted:
            if address and property_type and price > 0:
                # Create property data
                property_data = {
                    'id': str(uuid.uuid4()),
                    'address': address,
                    'property_type': property_type,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'square_feet': square_feet,
                    'year_built': year_built,
                    'price': price,
                    'down_payment': down_payment,
                    'loan_amount': loan_amount,
                    'interest_rate': interest_rate,
                    'loan_term': loan_term,
                    'monthly_rent': monthly_rent,
                    'monthly_expenses': monthly_expenses,
                    'neighborhood': neighborhood,
                    'school_district': school_district,
                    'date_acquired': date_acquired,
                    'notes': notes,
                    'date_added': datetime.now()
                }
                
                # Add property to data manager
                st.session_state.data_manager.add_property(property_data)
                st.success("✅ Property added successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields (marked with *)")

with tab2:
    st.subheader("Manage Existing Properties")
    
    properties_df = st.session_state.data_manager.get_properties()
    
    if not properties_df.empty:
        # Property selection
        selected_property = st.selectbox(
            "Select a property to edit:",
            options=properties_df['address'].tolist(),
            format_func=lambda x: f"{x} - ${properties_df[properties_df['address']==x]['price'].iloc[0]:,.0f}"
        )
        
        if selected_property:
            property_data = properties_df[properties_df['address'] == selected_property].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Property Details**")
                st.write(f"**Address:** {property_data['address']}")
                st.write(f"**Type:** {property_data['property_type']}")
                st.write(f"**Price:** ${property_data['price']:,.0f}")
                st.write(f"**Monthly Rent:** ${property_data['monthly_rent']:,.0f}")
                
            with col2:
                st.markdown("**Actions**")
                if st.button("🗑️ Delete Property", type="secondary"):
                    st.session_state.data_manager.delete_property(property_data['id'])
                    st.success("Property deleted successfully!")
                    st.rerun()
                
                if st.button("📊 View Analysis", type="primary"):
                    st.switch_page("pages/2_Financial_Calculator.py")
    else:
        st.info("No properties available. Add a property in the 'Add New Property' tab.")

with tab3:
    st.subheader("Bulk Import Properties")
    
    # Sample CSV format
    st.markdown("**Import multiple properties from CSV**")
    
    with st.expander("📋 View Required CSV Format"):
        sample_data = {
            'address': ['123 Main St', '456 Oak Ave'],
            'property_type': ['Single Family', 'Multi-Family'],
            'price': [300000, 450000],
            'monthly_rent': [2500, 3500],
            'bedrooms': [3, 4],
            'bathrooms': [2, 3],
            'square_feet': [1500, 2000]
        }
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, use_container_width=True)
        
        # Download sample CSV
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv,
            file_name="property_sample.csv",
            mime="text/csv"
        )
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.markdown("**Preview of uploaded data:**")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("Import Properties", type="primary"):
                success_count = 0
                for _, row in df.iterrows():
                    try:
                        property_data = {
                            'id': str(uuid.uuid4()),
                            'address': row.get('address', ''),
                            'property_type': row.get('property_type', 'Single Family'),
                            'price': float(row.get('price', 0)),
                            'monthly_rent': float(row.get('monthly_rent', 0)),
                            'bedrooms': int(row.get('bedrooms', 0)),
                            'bathrooms': float(row.get('bathrooms', 0)),
                            'square_feet': int(row.get('square_feet', 0)),
                            'year_built': int(row.get('year_built', 2000)),
                            'down_payment': float(row.get('down_payment', 0)),
                            'loan_amount': float(row.get('loan_amount', 0)),
                            'interest_rate': float(row.get('interest_rate', 0)),
                            'loan_term': int(row.get('loan_term', 30)),
                            'monthly_expenses': float(row.get('monthly_expenses', 0)),
                            'neighborhood': row.get('neighborhood', ''),
                            'school_district': row.get('school_district', ''),
                            'notes': row.get('notes', ''),
                            'date_acquired': datetime.now(),
                            'date_added': datetime.now()
                        }
                        
                        st.session_state.data_manager.add_property(property_data)
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error importing row: {e}")
                
                st.success(f"✅ Successfully imported {success_count} properties!")
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
