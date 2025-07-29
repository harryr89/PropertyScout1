import requests
import pandas as pd
import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
import trafilatura
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

class PropertyDataSources:
    """Handles fetching real property data from various UK sources"""
    
    def __init__(self):
        # UK Property API Keys (to be set via environment variables)
        self.rightmove_api_key = os.getenv('RIGHTMOVE_API_KEY')
        self.zoopla_api_key = os.getenv('ZOOPLA_API_KEY')
        self.onthemarket_api_key = os.getenv('ONTHEMARKET_API_KEY')
        self.propertydata_api_key = os.getenv('PROPERTYDATA_API_KEY')
        self.land_registry_api_key = os.getenv('LAND_REGISTRY_API_KEY')
        
        # UK API Base URLs
        self.base_urls = {
            'rightmove': 'https://api.rightmove.co.uk/api/rent',
            'zoopla': 'https://api.zoopla.co.uk/api/v1',
            'onthemarket': 'https://api.onthemarket.com/v1',
            'propertydata': 'https://api.propertydata.co.uk/v1',
            'land_registry': 'https://landregistry.data.gov.uk'
        }
    
    def check_api_availability(self) -> Dict[str, bool]:
        """Check which UK property APIs are available based on API keys"""
        availability = {}
        
        apis = {
            'Rightmove': self.rightmove_api_key,
            'Zoopla': self.zoopla_api_key,
            'OnTheMarket': self.onthemarket_api_key,
            'PropertyData': self.propertydata_api_key,
            'Land Registry': self.land_registry_api_key
        }
        
        for api_name, api_key in apis.items():
            availability[api_name] = bool(api_key)
        
        return availability
    
    def search_properties_rightmove(self, location: str, property_type: str = 'all', max_results: int = 50) -> List[Dict]:
        """Search properties using Rightmove API"""
        if not self.rightmove_api_key:
            st.error("Rightmove API key not found. Please add RIGHTMOVE_API_KEY to your environment variables.")
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.rightmove_api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'location': location,
                'propertyType': property_type,
                'maxResults': max_results,
                'sortBy': 'price'
            }
            
            response = requests.get(
                f"{self.base_urls['rightmove']}/properties",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_rightmove_data(data.get('properties', []))
            else:
                st.error(f"Rightmove API Error: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error fetching Rightmove data: {str(e)}")
            return []
    
    def search_properties_zoopla(self, area: str, max_results: int = 50) -> List[Dict]:
        """Search properties using Zoopla API"""
        if not self.zoopla_api_key:
            st.error("Zoopla API key not found. Please add ZOOPLA_API_KEY to your environment variables.")
            return []
        
        try:
            params = {
                'api_key': self.zoopla_api_key,
                'area': area,
                'page_size': max_results,
                'order_by': 'price',
                'listing_status': 'sale'
            }
            
            response = requests.get(
                f"{self.base_urls['zoopla']}/property_listings",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_zoopla_data(data.get('listing', []))
            else:
                st.error(f"Zoopla API Error: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error fetching Zoopla data: {str(e)}")
            return []
    
    def search_properties_onthemarket(self, location: str, max_results: int = 50) -> List[Dict]:
        """Search properties using OnTheMarket API"""
        if not self.onthemarket_api_key:
            st.error("OnTheMarket API key not found. Please add ONTHEMARKET_API_KEY to your environment variables.")
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.onthemarket_api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'location': location,
                'max_results': max_results,
                'sort': 'price_low_to_high'
            }
            
            response = requests.get(
                f"{self.base_urls['onthemarket']}/properties",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_onthemarket_data(data.get('properties', []))
            else:
                st.error(f"OnTheMarket API Error: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error fetching OnTheMarket data: {str(e)}")
            return []
    
    def _normalize_rightmove_data(self, properties: List[Dict]) -> List[Dict]:
        """Normalize Rightmove data to standard format"""
        normalized = []
        
        for prop in properties:
            try:
                normalized_prop = {
                    'id': f"rm_{prop.get('id', '')}",
                    'address': prop.get('displayAddress', ''),
                    'property_type': prop.get('propertyType', 'Unknown'),
                    'price': float(prop.get('price', {}).get('amount', 0)),
                    'monthly_rent': float(prop.get('rentAmount', 0)),
                    'bedrooms': int(prop.get('bedrooms', 0)),
                    'bathrooms': int(prop.get('bathrooms', 0)),
                    'square_feet': 0,  # Not typically available, will estimate
                    'year_built': 0,   # Not typically available
                    'neighborhood': prop.get('location', {}).get('displayName', ''),
                    'description': prop.get('summary', ''),
                    'source': 'Rightmove',
                    'date_added': datetime.now(),
                    'listing_url': prop.get('propertyUrl', ''),
                    'images': prop.get('propertyImages', []),
                    'postcode': prop.get('location', {}).get('postcode', ''),
                    'tenure': prop.get('tenure', ''),
                    'agent': prop.get('contactDetails', {}).get('name', '')
                }
                normalized.append(normalized_prop)
            except Exception as e:
                st.warning(f"Error normalizing Rightmove property: {str(e)}")
                continue
        
        return normalized
    
    def _normalize_zoopla_data(self, properties: List[Dict]) -> List[Dict]:
        """Normalize Zoopla data to standard format"""
        normalized = []
        
        for prop in properties:
            try:
                normalized_prop = {
                    'id': f"zp_{prop.get('listing_id', '')}",
                    'address': prop.get('displayable_address', ''),
                    'property_type': prop.get('property_type', 'Unknown'),
                    'price': float(prop.get('price', 0)),
                    'monthly_rent': 0,  # Will estimate based on price
                    'bedrooms': int(prop.get('num_bedrooms', 0)),
                    'bathrooms': int(prop.get('num_bathrooms', 0)),
                    'square_feet': int(prop.get('floor_area', {}).get('max_floor_area', 0) * 10.764) if prop.get('floor_area') else 0,  # Convert sq meters to sq feet
                    'year_built': 0,   # Not typically available
                    'neighborhood': prop.get('county', ''),
                    'description': prop.get('description', ''),
                    'source': 'Zoopla',
                    'date_added': datetime.now(),
                    'listing_url': prop.get('details_url', ''),
                    'images': [prop.get('image_url', '')] if prop.get('image_url') else [],
                    'postcode': prop.get('postcode', ''),
                    'agent_name': prop.get('agent_name', ''),
                    'property_category': prop.get('category', '')
                }
                normalized.append(normalized_prop)
            except Exception as e:
                st.warning(f"Error normalizing Zoopla property: {str(e)}")
                continue
        
        return normalized
    
    def _normalize_onthemarket_data(self, properties: List[Dict]) -> List[Dict]:
        """Normalize OnTheMarket data to standard format"""
        normalized = []
        
        for prop in properties:
            try:
                normalized_prop = {
                    'id': f"otm_{prop.get('id', '')}",
                    'address': prop.get('address', ''),
                    'property_type': prop.get('type', 'Unknown'),
                    'price': float(prop.get('price', 0)),
                    'monthly_rent': 0,  # Will estimate
                    'bedrooms': int(prop.get('bedrooms', 0)),
                    'bathrooms': int(prop.get('bathrooms', 0)),
                    'square_feet': 0,  # Not typically available
                    'year_built': 0,   # Not typically available
                    'neighborhood': prop.get('area', ''),
                    'description': prop.get('description', ''),
                    'source': 'OnTheMarket',
                    'date_added': datetime.now(),
                    'listing_url': prop.get('url', ''),
                    'images': prop.get('images', []),
                    'postcode': prop.get('postcode', ''),
                    'tenure': prop.get('tenure', ''),
                    'agent': prop.get('agent', {}).get('name', '')
                }
                normalized.append(normalized_prop)
            except Exception as e:
                st.warning(f"Error normalizing OnTheMarket property: {str(e)}")
                continue
        
        return normalized
    
    def estimate_rental_income(self, property_data: Dict) -> float:
        """Estimate rental income using various methods"""
        try:
            # Method 1: Use existing rent if available
            if property_data.get('monthly_rent', 0) > 0:
                return property_data['monthly_rent']
            
            # Method 2: Use 1% rule as baseline
            price = property_data.get('price', 0)
            if price > 0:
                one_percent_estimate = price * 0.01
                
                # Method 3: Adjust based on location and property type
                location_multiplier = self._get_location_rent_multiplier(property_data.get('neighborhood', ''))
                property_type_multiplier = self._get_property_type_multiplier(property_data.get('property_type', ''))
                
                estimated_rent = one_percent_estimate * location_multiplier * property_type_multiplier
                
                return max(estimated_rent, price * 0.005)  # Minimum 0.5% rule
            
            return 0
            
        except Exception as e:
            st.warning(f"Error estimating rental income: {str(e)}")
            return 0
    
    def _get_location_rent_multiplier(self, location: str) -> float:
        """Get rental multiplier based on UK location characteristics"""
        location_lower = location.lower()
        
        # High-rent UK areas
        if any(indicator in location_lower for indicator in ['london', 'kensington', 'chelsea', 'mayfair', 'canary wharf', 'shoreditch', 'oxford', 'cambridge', 'bath', 'brighton']):
            return 1.4
        
        # Medium-high rent areas
        if any(indicator in location_lower for indicator in ['manchester', 'birmingham', 'bristol', 'edinburgh', 'glasgow', 'leeds', 'liverpool', 'nottingham']):
            return 1.1
        
        # Medium-rent indicators  
        if any(indicator in location_lower for indicator in ['suburb', 'residential', 'new town']):
            return 1.0
        
        # Lower-rent indicators
        if any(indicator in location_lower for indicator in ['rural', 'remote', 'industrial', 'ex-mining']):
            return 0.7
        
        return 1.0  # Default multiplier
    
    def _get_property_type_multiplier(self, property_type: str) -> float:
        """Get rental multiplier based on property type"""
        property_type_lower = property_type.lower()
        
        multipliers = {
            'single family': 1.0,
            'condo': 0.9,
            'townhouse': 0.95,
            'multi-family': 1.1,
            'apartment': 0.85,
            'commercial': 1.2
        }
        
        for prop_type, multiplier in multipliers.items():
            if prop_type in property_type_lower:
                return multiplier
        
        return 1.0  # Default multiplier
    
    def search_all_sources(self, location: str, max_results_per_source: int = 25) -> List[Dict]:
        """Search all available data sources"""
        all_properties = []
        
        # Parse location for UK format
        location_parts = location.split(',')
        if len(location_parts) >= 2:
            city = location_parts[0].strip()
            county = location_parts[1].strip()
        else:
            city = location
            county = 'Greater London'  # Default county
        
        # Check API availability
        availability = self.check_api_availability()
        
        st.info(f"Searching for properties in {city}, {county}...")
        
        # Search each available UK source
        if availability.get('Rightmove', False):
            st.info("Searching Rightmove...")
            rightmove_properties = self.search_properties_rightmove(location, max_results=max_results_per_source)
            all_properties.extend(rightmove_properties)
        
        if availability.get('Zoopla', False):
            st.info("Searching Zoopla...")
            zoopla_properties = self.search_properties_zoopla(city, max_results=max_results_per_source)
            all_properties.extend(zoopla_properties)
        
        if availability.get('OnTheMarket', False):
            st.info("Searching OnTheMarket...")
            onthemarket_properties = self.search_properties_onthemarket(location, max_results=max_results_per_source)
            all_properties.extend(onthemarket_properties)
        
        # Estimate rental income for properties without it
        for prop in all_properties:
            if prop.get('monthly_rent', 0) == 0:
                prop['monthly_rent'] = self.estimate_rental_income(prop)
        
        # If no API data available, try web scraping (demo only)
        if not all_properties:
            st.info("No API data available. Attempting to demonstrate with sample data...")
            all_properties = self._generate_uk_demo_data(location, max_results_per_source * 2)
        
        return all_properties
    
    def _generate_uk_demo_data(self, location: str, count: int) -> List[Dict]:
        """Generate realistic UK property demo data for demonstration"""
        import random
        
        demo_properties = []
        
        # UK-specific property types and areas
        uk_property_types = ["Terraced House", "Semi-Detached", "Detached", "Flat/Apartment", "Bungalow"]
        uk_areas = ["City Centre", "Suburb", "New Development", "Victorian Area", "Modern Estate"]
        
        # UK price ranges by area type
        price_ranges = {
            "london": (300000, 800000),
            "manchester": (150000, 350000),
            "birmingham": (120000, 300000),
            "bristol": (200000, 450000),
            "leeds": (130000, 280000),
            "liverpool": (100000, 250000),
            "default": (120000, 300000)
        }
        
        # Determine price range based on location
        location_lower = location.lower()
        price_range = price_ranges.get("default")
        for city, ranges in price_ranges.items():
            if city in location_lower:
                price_range = ranges
                break
        
        for i in range(count):
            property_type = random.choice(uk_property_types)
            area = random.choice(uk_areas)
            price = random.randint(price_range[0], price_range[1])
            
            # Calculate realistic UK rental yield
            base_yield = random.uniform(0.04, 0.08)  # 4-8% typical UK yields
            monthly_rent = int((price * base_yield) / 12)
            
            # Adjust for property type
            if property_type == "Flat/Apartment":
                monthly_rent = int(monthly_rent * 0.9)
            elif property_type == "Detached":
                monthly_rent = int(monthly_rent * 1.1)
            
            bedrooms = random.choice([1, 2, 3, 4, 5])
            if property_type == "Flat/Apartment":
                bedrooms = min(bedrooms, 3)
            
            demo_property = {
                'id': f"demo_uk_{i}",
                'address': f"{i+1} {area} {random.choice(['Road', 'Street', 'Avenue', 'Close', 'Gardens'])}, {location}",
                'property_type': property_type,
                'price': price,
                'monthly_rent': monthly_rent,
                'bedrooms': bedrooms,
                'bathrooms': random.choice([1, 2, 3]) if bedrooms <= 3 else random.choice([2, 3, 4]),
                'square_feet': random.randint(600, 2000),
                'year_built': random.randint(1960, 2020),
                'neighborhood': area,
                'description': f"A lovely {property_type.lower()} in {area.lower()} area of {location}.",
                'source': 'Demo Data (UK)',
                'date_added': datetime.now(),
                'listing_url': f"https://example-uk-property-site.co.uk/property/{i}",
                'postcode': f"{random.choice(['M', 'B', 'L', 'LS', 'BS'])}{random.randint(1,30)} {random.randint(1,9)}{random.choice('ABCDEFG')}{random.choice('HJKLMNPQRSTUVWXYZ')}",
                'tenure': random.choice(['Freehold', 'Leasehold']),
                'council_tax_band': random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
            }
            
            demo_properties.append(demo_property)
        
        return demo_properties
    
    def scrape_rightmove_search(self, location: str, max_results: int = 25) -> List[Dict]:
        """Scrape Rightmove search results (fallback when no API)"""
        try:
            # This is a demonstration of how web scraping could work
            # In practice, you'd need to respect robots.txt and terms of service
            search_url = f"https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E{location}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Note: This is demo code - actual implementation would need proper handling
            st.warning("Web scraping is for demonstration only. Use official APIs for production.")
            
            return []
            
        except Exception as e:
            st.warning(f"Web scraping not available: {str(e)}")
            return []
    
    def save_properties_to_portfolio(self, properties: List[Dict], data_manager) -> int:
        """Save selected properties to the portfolio"""
        added_count = 0
        
        for prop in properties:
            try:
                # Convert to portfolio format
                portfolio_property = {
                    'id': prop.get('id', ''),
                    'address': prop.get('address', ''),
                    'property_type': prop.get('property_type', 'Single Family'),
                    'price': prop.get('price', 0),
                    'monthly_rent': prop.get('monthly_rent', 0),
                    'bedrooms': prop.get('bedrooms', 0),
                    'bathrooms': prop.get('bathrooms', 0),
                    'square_feet': prop.get('square_feet', 0),
                    'year_built': prop.get('year_built', 2000),
                    'neighborhood': prop.get('neighborhood', ''),
                    'notes': f"Imported from {prop.get('source', 'External Source')}",
                    'date_acquired': datetime.now().date(),
                    'date_added': datetime.now(),
                    'down_payment': prop.get('price', 0) * 0.2,  # Default 20%
                    'loan_amount': prop.get('price', 0) * 0.8,    # Default 80%
                    'interest_rate': 6.5,  # Default rate
                    'loan_term': 30,       # Default term
                    'monthly_expenses': prop.get('monthly_rent', 0) * 0.35,  # Default 35% expense ratio
                    'school_district': '',
                    'source_data': {
                        'source': prop.get('source', ''),
                        'listing_url': prop.get('listing_url', ''),
                        'original_data': prop
                    }
                }
                
                if data_manager.add_property(portfolio_property):
                    added_count += 1
                    
            except Exception as e:
                st.warning(f"Error adding property to portfolio: {str(e)}")
                continue
        
        return added_count