"""
Backend tests for GDP and fertility data fetching functionality.
"""

import unittest
import json
import sys
import os

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


if __name__ == '__main__':
    unittest.main()