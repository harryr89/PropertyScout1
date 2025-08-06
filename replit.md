# Property Analytics Dashboard

## Overview

This is a comprehensive UK property investment analytics platform built with Streamlit. The application provides UK real estate investors with tools to analyze, compare, and track British property investments through multiple analytical perspectives including financial calculations, market analysis, and live property data sourcing from UK markets.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with multi-page navigation
- **UI Components**: Interactive dashboards with Plotly visualizations
- **State Management**: Streamlit session state for persistent data across pages
- **Layout**: Wide layout with sidebar navigation and tabbed interfaces

### Backend Architecture
- **Core Logic**: Utility classes for calculations, data management, and scoring
- **Data Processing**: Pandas for data manipulation and analysis
- **Calculations**: Custom PropertyCalculator class for real estate financial metrics
- **Scoring**: PropertyScorer class for ranking and comparison algorithms

### Data Storage
- **Local Storage**: JSON file-based storage for property data
- **Session State**: In-memory storage for user session data
- **Data Models**: Dictionary-based property records with datetime handling

## Key Components

### Core Application (app.py)
- Main dashboard with overview metrics
- Session state initialization for core utility classes
- Primary navigation hub with sidebar menu

### Page Components
1. **Property Input** (`pages/1_Property_Input.py`)
   - Property data entry forms
   - Property management interface
   - Bulk import functionality

2. **Financial Calculator** (`pages/2_Financial_Calculator.py`)
   - Quick property analysis tools
   - Detailed financial calculations
   - Scenario comparison features

3. **Deal Comparison** (`pages/3_Deal_Comparison.py`)
   - Side-by-side property comparison
   - Ranking and scoring system
   - Market position analysis

4. **Market Analysis** (`pages/4_Market_Analysis.py`)
   - Market trend visualization
   - Sample data generation for demonstration
   - Benchmarking capabilities

5. **Performance Tracking** (`pages/5_Performance_Tracking.py`)
   - Investment performance monitoring
   - Historical data analysis
   - Time-series performance metrics

6. **Live Property Search** (`pages/6_Live_Property_Search.py`)
   - UK property data sourcing from multiple platforms
   - Real-time property search and filtering
   - Market-based property import and analysis
   - UK-specific yield calculations and metrics

### Utility Classes

#### DataManager (`utils/data_manager.py`)
- Handles property data persistence
- JSON file operations with datetime serialization
- Data validation and error handling
- CRUD operations for property records

#### PropertyCalculator (`utils/calculations.py`)
- Financial metric calculations (ROI, Cap Rate, Cash Flow, DSCR)
- Mortgage payment calculations
- Investment return analysis
- Comprehensive metrics computation

#### PropertyScorer (`utils/scoring.py`)
- Property ranking algorithms
- Weighted scoring system
- Market benchmark comparisons
- Normalization and scoring functions

#### PropertyDataSources (`utils/property_data_sources.py`)
- UK property data integration from multiple sources
- API connections to Rightmove, Zoopla, OnTheMarket, PropertyData, Land Registry
- Real-time property search and data normalization
- UK market-specific yield calculations and rental estimations
- Fallback demo data generation based on current UK market research

## Data Flow

1. **Input Flow**: User enters property data through forms → DataManager validates and stores → JSON persistence
2. **Calculation Flow**: Property data → PropertyCalculator processes metrics → Results displayed in UI
3. **Analysis Flow**: Stored properties → PropertyScorer ranks/compares → Visualization components render results
4. **Session Flow**: Session state maintains utility class instances across page navigation

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations (express and graph_objects)
- **NumPy**: Mathematical operations and calculations

### Data Sourcing Dependencies
- **Requests**: HTTP client for API interactions
- **BeautifulSoup4**: HTML parsing for web scraping fallbacks
- **Selenium**: Browser automation for complex property sites
- **Trafilatura**: Web content extraction and text processing
- **Python-dotenv**: Environment variable management

### Standard Library
- **datetime**: Date and time handling
- **json**: Data serialization
- **os**: File system operations
- **uuid**: Unique identifier generation
- **random**: Market-realistic sample data generation

## Deployment Strategy

### Local Development
- Single-command Streamlit server (`streamlit run app.py`)
- File-based data storage for simplicity
- No external database dependencies

### Production Considerations
- Designed for cloud deployment (Streamlit Cloud, Heroku, etc.)
- Stateless architecture with session-based persistence
- JSON file storage suitable for single-user or small-scale deployments
- Easily extensible to database storage for multi-user scenarios

## User Preferences

- **Market Focus**: UK-based property deal sourcing and analysis
- **Communication Style**: Simple, everyday language
- **Currency**: British Pounds (£) for all financial displays
- **Property Types**: UK-specific property categories (Terraced, Semi-Detached, Detached, Flat/Apartment, Bungalow)
- **Yield Focus**: UK rental yield standards (6%+ considered good, 4-6% average, <4% poor)

## Changelog

- **August 06, 2025**: Major system improvements based on code analysis
  - **Fixed critical calculation bug**: Replaced linear growth with proper cumulative compounding in performance tracking
  - **Updated UK market rates**: Property appreciation reduced to 2.5% annually (from 4%) based on 2025 market data
  - **Currency standardization**: All financial displays now use £ consistently across all pages
  - **UK property types**: Standardized to Terraced, Semi-Detached, Detached, Flat/Apartment, Bungalow
  - **Enhanced calculations**: Added LTV (Loan-to-Value) ratio to financial metrics
  - **Realistic UK defaults**: Updated base house price to £280,000, rent to £1,800/month
  - **Fixed Streamlit errors**: Added unique keys to all plotly charts to prevent duplicate element errors
  - **Market data accuracy**: Implemented proper compound growth in market analysis

- **July 29, 2025**: Adapted system for UK property market focus
  - Updated PropertyDataSources for UK property APIs (Rightmove, Zoopla, OnTheMarket, PropertyData, Land Registry)
  - Implemented UK-specific property types and market data
  - Added realistic UK market data generation based on 2025 research
  - Updated UI for British currency (£) and UK property terminology
  - Added UK-specific yield calculations and market benchmarks
  - Integrated live property search with UK market focus

- **July 05, 2025**: Initial setup