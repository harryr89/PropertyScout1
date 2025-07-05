import pandas as pd
import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class DataManager:
    """Manages property data storage and retrieval"""
    
    def __init__(self, data_file='property_data.json'):
        self.data_file = data_file
        self.properties = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """Load property data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Convert date strings back to datetime objects where needed
                    for prop in data:
                        if 'date_acquired' in prop and isinstance(prop['date_acquired'], str):
                            try:
                                prop['date_acquired'] = datetime.strptime(prop['date_acquired'], '%Y-%m-%d').date()
                            except:
                                prop['date_acquired'] = datetime.now().date()
                        if 'date_added' in prop and isinstance(prop['date_added'], str):
                            try:
                                prop['date_added'] = datetime.strptime(prop['date_added'], '%Y-%m-%d %H:%M:%S.%f')
                            except:
                                prop['date_added'] = datetime.now()
                    return data
            return []
        except Exception as e:
            st.error(f"Error loading property data: {str(e)}")
            return []
    
    def _save_data(self):
        """Save property data to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data_to_save = []
            for prop in self.properties:
                prop_copy = prop.copy()
                if 'date_acquired' in prop_copy and hasattr(prop_copy['date_acquired'], 'strftime'):
                    prop_copy['date_acquired'] = prop_copy['date_acquired'].strftime('%Y-%m-%d')
                if 'date_added' in prop_copy and hasattr(prop_copy['date_added'], 'strftime'):
                    prop_copy['date_added'] = prop_copy['date_added'].strftime('%Y-%m-%d %H:%M:%S.%f')
                data_to_save.append(prop_copy)
            
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving property data: {str(e)}")
    
    def get_properties(self) -> pd.DataFrame:
        """Get all properties as a DataFrame"""
        if not self.properties:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(self.properties)
            # Ensure numeric columns are properly typed
            numeric_columns = ['price', 'down_payment', 'loan_amount', 'interest_rate', 
                             'loan_term', 'monthly_rent', 'monthly_expenses', 'bedrooms', 
                             'bathrooms', 'square_feet', 'year_built']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            return df
        except Exception as e:
            st.error(f"Error converting properties to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def add_property(self, property_data: Dict) -> bool:
        """Add a new property"""
        try:
            # Validate required fields
            required_fields = ['address', 'property_type', 'price']
            for field in required_fields:
                if field not in property_data or not property_data[field]:
                    st.error(f"Missing required field: {field}")
                    return False
            
            # Ensure all numeric fields are properly typed
            numeric_fields = {
                'price': 0,
                'down_payment': 0,
                'loan_amount': 0,
                'interest_rate': 0,
                'loan_term': 30,
                'monthly_rent': 0,
                'monthly_expenses': 0,
                'bedrooms': 0,
                'bathrooms': 0,
                'square_feet': 0,
                'year_built': 2000
            }
            
            for field, default_value in numeric_fields.items():
                if field in property_data:
                    try:
                        property_data[field] = float(property_data[field]) if field in ['bathrooms', 'interest_rate'] else int(property_data[field])
                    except (ValueError, TypeError):
                        property_data[field] = default_value
                else:
                    property_data[field] = default_value
            
            # Add timestamp
            property_data['date_added'] = datetime.now()
            
            # Add to properties list
            self.properties.append(property_data)
            
            # Save to file
            self._save_data()
            
            return True
            
        except Exception as e:
            st.error(f"Error adding property: {str(e)}")
            return False
    
    def update_property(self, property_id: str, updated_data: Dict) -> bool:
        """Update an existing property"""
        try:
            for i, prop in enumerate(self.properties):
                if prop.get('id') == property_id:
                    # Update the property
                    self.properties[i].update(updated_data)
                    self.properties[i]['date_modified'] = datetime.now()
                    
                    # Save to file
                    self._save_data()
                    return True
            
            st.error("Property not found")
            return False
            
        except Exception as e:
            st.error(f"Error updating property: {str(e)}")
            return False
    
    def delete_property(self, property_id: str) -> bool:
        """Delete a property"""
        try:
            original_count = len(self.properties)
            self.properties = [prop for prop in self.properties if prop.get('id') != property_id]
            
            if len(self.properties) < original_count:
                self._save_data()
                return True
            else:
                st.error("Property not found")
                return False
                
        except Exception as e:
            st.error(f"Error deleting property: {str(e)}")
            return False
    
    def get_property_by_id(self, property_id: str) -> Optional[Dict]:
        """Get a specific property by ID"""
        try:
            for prop in self.properties:
                if prop.get('id') == property_id:
                    return prop
            return None
        except Exception as e:
            st.error(f"Error retrieving property: {str(e)}")
            return None
    
    def get_property_by_address(self, address: str) -> Optional[Dict]:
        """Get a specific property by address"""
        try:
            for prop in self.properties:
                if prop.get('address') == address:
                    return prop
            return None
        except Exception as e:
            st.error(f"Error retrieving property: {str(e)}")
            return None
    
    def search_properties(self, criteria: Dict) -> pd.DataFrame:
        """Search properties based on criteria"""
        try:
            df = self.get_properties()
            if df.empty:
                return df
            
            # Apply search filters
            for key, value in criteria.items():
                if key in df.columns and value is not None:
                    if isinstance(value, str):
                        # String search (case-insensitive)
                        df = df[df[key].str.contains(value, case=False, na=False)]
                    elif isinstance(value, (int, float)):
                        # Numeric search
                        df = df[df[key] == value]
                    elif isinstance(value, dict):
                        # Range search
                        if 'min' in value and value['min'] is not None:
                            df = df[df[key] >= value['min']]
                        if 'max' in value and value['max'] is not None:
                            df = df[df[key] <= value['max']]
            
            return df
            
        except Exception as e:
            st.error(f"Error searching properties: {str(e)}")
            return pd.DataFrame()
    
    def get_property_summary(self) -> Dict:
        """Get summary statistics for all properties"""
        try:
            df = self.get_properties()
            if df.empty:
                return {}
            
            summary = {
                'total_properties': len(df),
                'total_value': df['price'].sum(),
                'total_monthly_rent': df['monthly_rent'].sum(),
                'total_monthly_expenses': df['monthly_expenses'].sum(),
                'average_price': df['price'].mean(),
                'average_monthly_rent': df['monthly_rent'].mean(),
                'property_types': df['property_type'].value_counts().to_dict() if 'property_type' in df.columns else {},
                'total_bedrooms': df['bedrooms'].sum(),
                'total_bathrooms': df['bathrooms'].sum(),
                'total_square_feet': df['square_feet'].sum(),
                'average_year_built': df['year_built'].mean() if 'year_built' in df.columns else 0
            }
            
            return summary
            
        except Exception as e:
            st.error(f"Error generating property summary: {str(e)}")
            return {}
    
    def export_properties(self, format='csv') -> str:
        """Export properties to specified format"""
        try:
            df = self.get_properties()
            if df.empty:
                return ""
            
            if format.lower() == 'csv':
                return df.to_csv(index=False)
            elif format.lower() == 'json':
                return df.to_json(orient='records', indent=2)
            else:
                st.error(f"Unsupported export format: {format}")
                return ""
                
        except Exception as e:
            st.error(f"Error exporting properties: {str(e)}")
            return ""
    
    def import_properties(self, data, format='csv') -> bool:
        """Import properties from specified format"""
        try:
            if format.lower() == 'csv':
                if isinstance(data, str):
                    df = pd.read_csv(data)
                else:
                    df = data
            elif format.lower() == 'json':
                if isinstance(data, str):
                    df = pd.read_json(data)
                else:
                    df = pd.DataFrame(data)
            else:
                st.error(f"Unsupported import format: {format}")
                return False
            
            # Convert DataFrame to list of dictionaries
            properties_to_add = df.to_dict('records')
            
            # Add each property
            success_count = 0
            for prop in properties_to_add:
                # Generate ID if not present
                if 'id' not in prop:
                    import uuid
                    prop['id'] = str(uuid.uuid4())
                
                if self.add_property(prop):
                    success_count += 1
            
            st.success(f"Successfully imported {success_count} properties")
            return True
            
        except Exception as e:
            st.error(f"Error importing properties: {str(e)}")
            return False
    
    def backup_data(self, backup_file: str = None) -> bool:
        """Create a backup of the property data"""
        try:
            if backup_file is None:
                backup_file = f"property_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(self.properties, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            st.error(f"Error creating backup: {str(e)}")
            return False
    
    def restore_data(self, backup_file: str) -> bool:
        """Restore property data from backup"""
        try:
            if not os.path.exists(backup_file):
                st.error("Backup file not found")
                return False
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Validate backup data
            if not isinstance(backup_data, list):
                st.error("Invalid backup file format")
                return False
            
            # Create current backup before restore
            self.backup_data()
            
            # Restore data
            self.properties = backup_data
            self._save_data()
            
            st.success("Data restored successfully")
            return True
            
        except Exception as e:
            st.error(f"Error restoring data: {str(e)}")
            return False
    
    def get_property_count(self) -> int:
        """Get total number of properties"""
        return len(self.properties)
    
    def clear_all_data(self) -> bool:
        """Clear all property data (use with caution)"""
        try:
            # Create backup before clearing
            self.backup_data()
            
            self.properties = []
            self._save_data()
            
            return True
            
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")
            return False
