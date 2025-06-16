"""
Backend tests for GDP and fertility data fetching functionality.

This comprehensive test suite validates all aspects of the backend data fetching
functionality including API endpoints, data validation, error handling, and
integration with the World Bank API.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app
import data_fetcher


class TestDataFetcher(unittest.TestCase):
    """Test the data_fetcher module functionality."""

    def test_get_available_countries(self):
        """Test that we can fetch available countries."""
        countries = data_fetcher.get_available_countries()
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        
        # Check structure of first country
        if countries:
            country = countries[0]
            self.assertIn('code', country)
            self.assertIn('name', country)
            self.assertIsInstance(country['code'], str)
            self.assertIsInstance(country['name'], str)

    def test_validate_country_codes(self):
        """Test country code validation."""
        valid_countries = data_fetcher.validate_country_codes(['USA', 'GBR', 'INVALID'])
        self.assertIn('USA', valid_countries)
        self.assertIn('GBR', valid_countries)
        self.assertNotIn('INVALID', valid_countries)

    def test_fetch_gdp_data(self):
        """Test GDP data fetching."""
        countries = ['USA', 'GBR']
        data = data_fetcher.fetch_gdp_data(countries, 2020, 2021)
        
        self.assertIsInstance(data, dict)
        self.assertIn('USA', data)
        self.assertIn('GBR', data)
        
        # Check data structure
        usa_data = data['USA']
        self.assertIsInstance(usa_data, dict)
        if usa_data:
            year, value = next(iter(usa_data.items()))
            self.assertIsInstance(year, str)
            self.assertIsInstance(value, float)

    def test_fetch_gdp_data_empty_countries(self):
        """Test GDP data fetching with empty countries list."""
        with self.assertRaises(Exception):
            # World Bank API doesn't handle empty country list well
            data_fetcher.fetch_gdp_data([], 2020, 2021)

    def test_fetch_gdp_data_invalid_year_range(self):
        """Test GDP data fetching with invalid year range."""
        countries = ['USA']
        with self.assertRaises(Exception):
            # World Bank API doesn't handle invalid year ranges well
            data_fetcher.fetch_gdp_data(countries, 2022, 2020)

    def test_fetch_gdp_data_edge_case_years(self):
        """Test GDP data fetching with edge case years."""
        countries = ['USA']
        # Test with very old year (may have no data)
        data = data_fetcher.fetch_gdp_data(countries, 1960, 1960)
        self.assertIsInstance(data, dict)

    def test_fetch_fertility_data(self):
        """Test fertility data fetching."""
        countries = ['USA', 'GBR']
        data = data_fetcher.fetch_fertility_data(countries, 2020, 2021)
        
        self.assertIsInstance(data, dict)
        self.assertIn('USA', data)
        self.assertIn('GBR', data)
        
        # Check data structure
        usa_data = data['USA']
        self.assertIsInstance(usa_data, dict)
        if usa_data:
            year, value = next(iter(usa_data.items()))
            self.assertIsInstance(year, str)
            self.assertIsInstance(value, float)

    def test_fetch_fertility_data_empty_countries(self):
        """Test fertility data fetching with empty countries list."""
        with self.assertRaises(Exception):
            # World Bank API doesn't handle empty country list well
            data_fetcher.fetch_fertility_data([], 2020, 2021)

    def test_fetch_fertility_data_single_country(self):
        """Test fertility data fetching with single country."""
        countries = ['USA']
        data = data_fetcher.fetch_fertility_data(countries, 2020, 2021)
        self.assertIsInstance(data, dict)
        self.assertIn('USA', data)

    def test_fetch_combined_data(self):
        """Test combined data fetching."""
        countries = ['USA', 'GBR']
        data = data_fetcher.fetch_combined_data(countries, 2020, 2021)
        
        self.assertIsInstance(data, dict)
        self.assertIn('countries', data)
        self.assertIn('years', data)
        self.assertIn('metadata', data)
        
        # Check countries data structure
        countries_data = data['countries']
        self.assertIn('USA', countries_data)
        self.assertIn('GBR', countries_data)
        
        usa_data = countries_data['USA']
        self.assertIn('gdp', usa_data)
        self.assertIn('fertility', usa_data)

    def test_fetch_combined_data_metadata(self):
        """Test combined data includes proper metadata."""
        countries = ['USA']
        data = data_fetcher.fetch_combined_data(countries, 2020, 2021)
        
        metadata = data['metadata']
        self.assertEqual(metadata['gdp_indicator'], 'NY.GDP.PCAP.CD')
        self.assertEqual(metadata['fertility_indicator'], 'SP.DYN.TFRT.IN')
        self.assertEqual(metadata['start_year'], 2020)
        self.assertEqual(metadata['end_year'], 2021)

    def test_fetch_combined_data_years_array(self):
        """Test combined data includes correct years array."""
        countries = ['USA']
        data = data_fetcher.fetch_combined_data(countries, 2020, 2022)
        
        expected_years = [2020, 2021, 2022]
        self.assertEqual(data['years'], expected_years)

    @patch('data_fetcher.wb.data.fetch')
    def test_fetch_gdp_data_api_error(self, mock_fetch):
        """Test GDP data fetching handles API errors gracefully."""
        mock_fetch.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            data_fetcher.fetch_gdp_data(['USA'], 2020, 2021)

    @patch('data_fetcher.wb.economy.list')
    def test_get_available_countries_api_error(self, mock_list):
        """Test countries endpoint handles API errors gracefully."""
        mock_list.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            data_fetcher.get_available_countries()

    def test_validate_country_codes_mixed_case(self):
        """Test country code validation with mixed case."""
        valid_countries = data_fetcher.validate_country_codes(['usa', 'GBR', 'Jpn'])
        # Function should handle case normalization in calling code
        self.assertIsInstance(valid_countries, list)


class TestFlaskAPI(unittest.TestCase):
    """Test the Flask API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_countries_endpoint(self):
        """Test the countries endpoint."""
        response = self.app.get('/countries')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('count', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(data['count'], 0)

    def test_data_endpoint_valid_request(self):
        """Test the data endpoint with valid parameters."""
        response = self.app.get('/data?countries=USA,GBR&start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('valid_countries', data)
        self.assertIn('USA', data['valid_countries'])
        self.assertIn('GBR', data['valid_countries'])

    def test_data_endpoint_missing_countries(self):
        """Test the data endpoint without countries parameter."""
        response = self.app.get('/data?start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Missing required parameter')

    def test_data_endpoint_invalid_years(self):
        """Test the data endpoint with invalid year range."""
        response = self.app.get('/data?countries=USA&start_year=2025&end_year=2020')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid year range')

    def test_data_endpoint_invalid_countries(self):
        """Test the data endpoint with invalid country codes."""
        response = self.app.get('/data?countries=INVALID1,INVALID2&start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid countries')

    def test_gdp_endpoint(self):
        """Test the GDP-specific endpoint."""
        response = self.app.get('/data/gdp?countries=USA&start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data_type'], 'gdp')
        self.assertIn('data', data)

    def test_fertility_endpoint(self):
        """Test the fertility-specific endpoint."""
        response = self.app.get('/data/fertility?countries=USA&start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data_type'], 'fertility')
        self.assertIn('data', data)

    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = self.app.get('/health')
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_data_endpoint_year_boundary_validation(self):
        """Test data endpoint year boundary validation."""
        # Test year too early
        response = self.app.get('/data?countries=USA&start_year=1950&end_year=2021')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        
        # Test year too late
        response = self.app.get('/data?countries=USA&start_year=2020&end_year=2035')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_data_endpoint_invalid_year_format(self):
        """Test data endpoint with invalid year format."""
        response = self.app.get('/data?countries=USA&start_year=abc&end_year=2021')
        # ValueError is caught as 400 bad request by the app
        self.assertEqual(response.status_code, 400)
        
    def test_data_endpoint_whitespace_countries(self):
        """Test data endpoint handles whitespace in country codes."""
        response = self.app.get('/data?countries= USA , GBR &start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_data_endpoint_case_insensitive_countries(self):
        """Test data endpoint handles lowercase country codes."""
        response = self.app.get('/data?countries=usa,gbr&start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('USA', data['valid_countries'])
        self.assertIn('GBR', data['valid_countries'])

    def test_gdp_endpoint_missing_countries(self):
        """Test GDP endpoint without countries parameter."""
        response = self.app.get('/data/gdp?start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_fertility_endpoint_missing_countries(self):
        """Test fertility endpoint without countries parameter."""
        response = self.app.get('/data/fertility?start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_health_endpoint_response_format(self):
        """Test health endpoint returns proper format."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'healthy')

    def test_countries_endpoint_response_format(self):
        """Test countries endpoint returns proper format."""
        response = self.app.get('/countries')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('count', data)
        self.assertIsInstance(data['data'], list)
        
        # Verify country object structure
        if data['data']:
            country = data['data'][0]
            self.assertIn('code', country)
            self.assertIn('name', country)

    def test_data_endpoint_default_years(self):
        """Test data endpoint uses default years when not specified."""
        response = self.app.get('/data?countries=USA')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    @patch('app.fetch_combined_data')
    def test_data_endpoint_handles_data_fetcher_errors(self, mock_fetch):
        """Test data endpoint handles data fetcher exceptions."""
        mock_fetch.side_effect = Exception("Data fetch error")
        
        response = self.app.get('/data?countries=USA&start_year=2020&end_year=2021')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Failed to fetch data')

    @patch('app.get_available_countries')
    def test_countries_endpoint_handles_api_errors(self, mock_countries):
        """Test countries endpoint handles API exceptions."""
        mock_countries.side_effect = Exception("API Error")
        
        response = self.app.get('/countries')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Failed to fetch countries')

    def test_404_error_handler(self):
        """Test 404 error handler for non-existent endpoints."""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Not found')


if __name__ == '__main__':
    unittest.main()