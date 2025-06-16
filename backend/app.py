"""
Flask application for serving GDP and fertility rate data from World Bank API.

This application provides RESTful endpoints for fetching and serving data
to the frontend visualization component.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from typing import Dict, Any

from data_fetcher import (
    fetch_combined_data,
    fetch_gdp_data,
    fetch_fertility_data,
    get_available_countries,
    validate_country_codes
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow frontend requests
CORS(app, origins=['*'])


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'GDP Fertility Viz API is running'})


@app.route('/countries', methods=['GET'])
def get_countries():
    """
    Get list of available countries.

    Returns:
        JSON response with list of countries including code and name
    """
    try:
        logger.info("Fetching available countries")
        countries = get_available_countries()

        # Return countries directly for frontend compatibility
        return jsonify({
            'countries': countries
        })

    except Exception as e:
        logger.error(f"Error in get_countries: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch countries',
            'message': str(e)
        }), 500


@app.route('/data', methods=['GET'])
def get_data():
    """
    Get combined GDP and fertility data for specified countries and years.

    Query parameters:
        countries: Comma-separated list of country codes
        start_year: Starting year (default: 1960)
        end_year: Ending year (default: 2023)

    Returns:
        JSON response with combined GDP and fertility data
    """
    try:
        # Parse query parameters
        countries_param = request.args.get('countries')
        start_year = int(request.args.get('start_year', 1960))
        end_year = int(request.args.get('end_year', 2023))

        if not countries_param:
            # Default to a set of major countries if none specified
            countries = ['USA', 'CHN', 'IND', 'JPN', 'DEU', 'GBR', 'FRA', 'BRA', 'CAN', 'AUS', 
                        'KOR', 'MEX', 'IDN', 'TUR', 'RUS', 'ITA', 'ESP', 'NLD', 'CHE', 'SWE',
                        'NOR', 'DNK', 'FIN', 'BEL', 'AUT', 'NZL', 'SGP', 'ARE', 'ISR', 'HKG']
        else:
            # Parse and validate countries
            countries = [country.strip().upper() for country in countries_param.split(',')]

        valid_countries = validate_country_codes(countries)

        if not valid_countries:
            return jsonify({
                'success': False,
                'error': 'Invalid countries',
                'message': 'No valid country codes provided'
            }), 400

        # Validate year range
        if start_year > end_year:
            return jsonify({
                'success': False,
                'error': 'Invalid year range',
                'message': 'start_year must be less than or equal to end_year'
            }), 400

        if start_year < 1960 or end_year > 2030:
            return jsonify({
                'success': False,
                'error': 'Invalid year range',
                'message': 'Years must be between 1960 and 2030'
            }), 400

        logger.info(f"Fetching data for countries: {valid_countries}, years: {start_year}-{end_year}")

        # Fetch the data
        data = fetch_combined_data(valid_countries, start_year, end_year)

        # Return data directly for frontend compatibility
        return jsonify(data)

    except ValueError as e:
        logger.error(f"Value error in get_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error in get_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch data',
            'message': str(e)
        }), 500


@app.route('/data/gdp', methods=['GET'])
def get_gdp_data():
    """
    Get GDP data for specified countries and years.

    Query parameters:
        countries: Comma-separated list of country codes
        start_year: Starting year (default: 1990)
        end_year: Ending year (default: 2022)

    Returns:
        JSON response with GDP data
    """
    try:
        # Parse query parameters
        countries_param = request.args.get('countries')
        start_year = int(request.args.get('start_year', 1990))
        end_year = int(request.args.get('end_year', 2022))

        if not countries_param:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter',
                'message': 'countries parameter is required'
            }), 400

        # Parse and validate countries
        countries = [country.strip().upper() for country in countries_param.split(',')]
        valid_countries = validate_country_codes(countries)

        if not valid_countries:
            return jsonify({
                'success': False,
                'error': 'Invalid countries',
                'message': 'No valid country codes provided'
            }), 400

        logger.info(f"Fetching GDP data for countries: {valid_countries}, years: {start_year}-{end_year}")

        # Fetch the data
        data = fetch_gdp_data(valid_countries, start_year, end_year)

        return jsonify({
            'success': True,
            'data': data,
            'data_type': 'gdp',
            'requested_countries': countries,
            'valid_countries': valid_countries
        })

    except Exception as e:
        logger.error(f"Error in get_gdp_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch GDP data',
            'message': str(e)
        }), 500


@app.route('/data/fertility', methods=['GET'])
def get_fertility_data():
    """
    Get fertility rate data for specified countries and years.

    Query parameters:
        countries: Comma-separated list of country codes
        start_year: Starting year (default: 1990)
        end_year: Ending year (default: 2022)

    Returns:
        JSON response with fertility data
    """
    try:
        # Parse query parameters
        countries_param = request.args.get('countries')
        start_year = int(request.args.get('start_year', 1990))
        end_year = int(request.args.get('end_year', 2022))

        if not countries_param:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter',
                'message': 'countries parameter is required'
            }), 400

        # Parse and validate countries
        countries = [country.strip().upper() for country in countries_param.split(',')]
        valid_countries = validate_country_codes(countries)

        if not valid_countries:
            return jsonify({
                'success': False,
                'error': 'Invalid countries',
                'message': 'No valid country codes provided'
            }), 400

        logger.info(f"Fetching fertility data for countries: {valid_countries}, years: {start_year}-{end_year}")

        # Fetch the data
        data = fetch_fertility_data(valid_countries, start_year, end_year)

        return jsonify({
            'success': True,
            'data': data,
            'data_type': 'fertility',
            'requested_countries': countries,
            'valid_countries': valid_countries
        })

    except Exception as e:
        logger.error(f"Error in get_fertility_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch fertility data',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Starting GDP Fertility Viz API server")
    app.run(debug=True, host='0.0.0.0', port=5001)
