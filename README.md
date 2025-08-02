# Property Analytics Dashboard

A comprehensive UK property investment analytics platform built with Streamlit. This application provides UK real estate investors with tools to analyze, compare, and track British property investments through multiple analytical perspectives.

## 🏠 Features

### Core Functionality
- **Property Input & Management** - Add and manage property portfolios
- **Financial Calculator** - Calculate ROI, cap rates, cash flow, and other key metrics
- **Deal Comparison** - Compare multiple investment opportunities side-by-side
- **Market Analysis** - Analyze market trends and benchmarks
- **Performance Tracking** - Monitor investment performance over time
- **Live Property Search** - Search and import UK property data

### UK Market Focus
- British pound (£) calculations throughout
- UK-specific property types (Terraced, Semi-Detached, Detached, Flat/Apartment, Bungalow)
- UK rental yield standards and benchmarks
- Integration with UK property data sources

### Advanced Analytics
- Comprehensive financial metrics (ROI, Cap Rate, Cash Flow, DSCR)
- Interactive Plotly visualizations
- Property scoring and ranking algorithms
- CSV data export functionality
- Real-time market data integration

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Streamlit
- Required dependencies (see `pyproject.toml`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/property-analytics-dashboard.git
cd property-analytics-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py --server.port 5000
```

4. Open your browser to `http://localhost:5000`

## 📊 Application Structure

```
├── app.py                      # Main dashboard
├── pages/
│   ├── 1_Property_Input.py     # Property data entry
│   ├── 2_Financial_Calculator.py # Financial calculations
│   ├── 3_Deal_Comparison.py    # Property comparison
│   ├── 4_Market_Analysis.py    # Market trends
│   ├── 5_Performance_Tracking.py # Performance monitoring
│   └── 6_Live_Property_Search.py # Live property data
├── utils/
│   ├── calculations.py         # Financial calculation engine
│   ├── data_manager.py        # Data persistence
│   ├── property_data_sources.py # UK property data integration
│   └── scoring.py             # Property scoring algorithms
└── .streamlit/
    └── config.toml            # Streamlit configuration
```

## 🎯 Key Metrics Calculated

- **ROI (Return on Investment)** - Annual return as percentage of initial investment
- **Cap Rate (Capitalization Rate)** - Net operating income divided by property price
- **Cash Flow** - Monthly income after all expenses
- **Cash-on-Cash Return** - Annual cash flow divided by initial cash investment
- **DSCR (Debt Service Coverage Ratio)** - NOI divided by annual debt payments
- **Gross Rental Yield** - Annual rental income as percentage of property price

## 🔧 Configuration

### Streamlit Configuration
The application includes optimized Streamlit settings in `.streamlit/config.toml`:
- Wide layout for better dashboard visualization
- Proper server configuration for deployment
- Performance optimizations

### UK Market Data
- Realistic pricing for major UK cities (Manchester, Birmingham, Leeds, London, Liverpool)
- UK-specific rental yield calculations
- Council tax bands and property classifications

## 📈 Usage Examples

### Adding Properties
1. Navigate to "Property Input" page
2. Enter property details including address, price, rental income
3. Add financing details if applicable
4. Save to portfolio

### Comparing Investments
1. Go to "Deal Comparison" page
2. Select properties from your portfolio
3. Review side-by-side financial metrics
4. Use scoring system to rank opportunities

### Market Analysis
1. Access "Market Analysis" page
2. View market trends and benchmarks
3. Compare your properties to market averages

## 🌟 Live Property Search

The application includes integration capabilities for UK property data sources:
- Address-based local market search
- Property filtering by price, bedrooms, type
- Automatic import to comparison tools
- UK market-specific yield calculations

## 🛠️ Technical Details

### Built With
- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive visualizations
- **NumPy** - Mathematical operations

### Data Storage
- JSON-based local storage for properties
- Session state management for user data
- CSV export functionality

### Performance Features
- Data caching for improved performance
- Error handling for robust operation
- Input validation and data sanitization

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For support or questions about this property analytics platform, please open an issue on GitHub.

---

**Built for UK Property Investors** | **Powered by Streamlit & Replit**