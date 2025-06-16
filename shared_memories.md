# Shared Memories

This file tracks important decisions, context, and learnings across all development tasks. Update this file when you make significant decisions or discoveries that other agents should know about.

## Recent Decisions

<!-- Add new decisions at the top -->

### Backend Data Fetching Implementation (2025-06-16)
- Implemented comprehensive backend data fetching using World Bank API via wbgapi library
- Flask app with CORS configured for frontend integration
- Data fetcher module with modular functions for GDP and fertility data
- Comprehensive test suite with 14 tests covering all endpoints and edge cases
- World Bank API returns data in generator format with records containing 'economy', 'time', 'value' fields
- Country names are in 'value' field, not 'name' field in wb.economy.list()
- Time format is 'YR2020' style, requires parsing to extract year number

## Architecture Decisions

### Backend API Design
- REST API with separate endpoints for combined data (/data), GDP only (/data/gdp), and fertility only (/data/fertility)
- Countries endpoint (/countries) for frontend country selection
- Health check endpoint (/health) for monitoring
- CORS enabled with flask-cors for frontend integration
- Error handling with appropriate HTTP status codes and JSON error responses
- Input validation for country codes, year ranges, and required parameters

## Known Issues & Workarounds

### World Bank API Data Structure
- wbgapi returns generators, not dictionaries - iterate through records
- Country data uses 'value' for name, not 'name' field
- Time data format is 'YRyyyy' and needs parsing
- Some countries may not have data for all indicators/years - handle with skipBlanks=True

## Integration Notes

### Backend-Frontend Communication
- Backend serves JSON data on port 5000
- CORS configured to allow requests from any origin for development
- Data format: countries object with GDP and fertility sub-objects, years array, metadata
- Country codes should be ISO 3-letter format (USA, GBR, JPN, etc.)

## Testing Insights

### Backend Testing Strategy
- Unit tests for data fetcher functions with real World Bank API calls
- Flask endpoint integration tests with test client
- Error condition testing for invalid inputs
- CORS header verification
- All 14 tests pass successfully with real API data

### Frontend Interactive Visualization Implementation (2025-06-16)
- Implemented interactive D3.js scatter plot visualization in frontend/app.js
- Created responsive HTML structure with controls for year slider and country selection
- Added CSS styling with responsive design for mobile and desktop
- Visualization features:
  - Scatter plot with GDP per capita (log scale) vs fertility rate (linear scale)
  - Time slider with play/pause functionality for animation through years 1960-2023
  - Country dropdown for highlighting specific countries
  - Interactive tooltips showing country details on hover
  - Color coding by regions using D3 color schemes
  - Responsive design with mobile-friendly controls
- Integration with backend API endpoints for data fetching
- Error handling for network failures and missing data
- Basic test structure created for frontend functionality

---
*Last updated: 2025-06-16*