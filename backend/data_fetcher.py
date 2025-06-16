"""
Data fetching module for GDP and fertility rate data from World Bank API.

This module provides functions to fetch, process, and format GDP and fertility
rate data using the wbgapi library for the visualization frontend.
"""

import wbgapi as wb
import logging
from typing import Dict, List, Optional, Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# World Bank indicator codes
GDP_INDICATOR = "NY.GDP.PCAP.CD"  # GDP per capita (current US$)
FERTILITY_INDICATOR = "SP.DYN.TFRT.IN"  # Fertility rate (births per woman)


def fetch_gdp_data(countries: List[str], start_year: int = 1990, end_year: int = 2022) -> Dict[str, Any]:
    """
    Fetch GDP per capita data for specified countries and years.
    
    Args:
        countries: List of country codes (ISO 3-letter codes)
        start_year: Starting year for data collection
        end_year: Ending year for data collection
        
    Returns:
        Dictionary containing GDP data organized by country and year
    """
    try:
        logger.info(f"Fetching GDP data for countries: {countries}")
        
        data = wb.data.fetch(
            GDP_INDICATOR,
            countries,
            time=range(start_year, end_year + 1),
            skipBlanks=True
        )
        
        formatted_data = {}
        for record in data:
            country_code = record['economy']
            year = record['time']
            value = record['value']
            
            if country_code not in formatted_data:
                formatted_data[country_code] = {}
            
            if value is not None:
                # Extract year from format like 'YR2020'
                if year.startswith('YR'):
                    year_num = year[2:]
                else:
                    year_num = str(year)
                formatted_data[country_code][year_num] = float(value)
        
        logger.info(f"Successfully fetched GDP data for {len(formatted_data)} countries")
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error fetching GDP data: {str(e)}")
        raise


def fetch_fertility_data(countries: List[str], start_year: int = 1990, end_year: int = 2022) -> Dict[str, Any]:
    """
    Fetch fertility rate data for specified countries and years.
    
    Args:
        countries: List of country codes (ISO 3-letter codes)
        start_year: Starting year for data collection
        end_year: Ending year for data collection
        
    Returns:
        Dictionary containing fertility data organized by country and year
    """
    try:
        logger.info(f"Fetching fertility data for countries: {countries}")
        
        data = wb.data.fetch(
            FERTILITY_INDICATOR,
            countries,
            time=range(start_year, end_year + 1),
            skipBlanks=True
        )
        
        formatted_data = {}
        for record in data:
            country_code = record['economy']
            year = record['time']
            value = record['value']
            
            if country_code not in formatted_data:
                formatted_data[country_code] = {}
            
            if value is not None:
                # Extract year from format like 'YR2020'
                if year.startswith('YR'):
                    year_num = year[2:]
                else:
                    year_num = str(year)
                formatted_data[country_code][year_num] = float(value)
        
        logger.info(f"Successfully fetched fertility data for {len(formatted_data)} countries")
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error fetching fertility data: {str(e)}")
        raise


def fetch_combined_data(countries: List[str], start_year: int = 1990, end_year: int = 2022) -> Dict[str, Any]:
    """
    Fetch both GDP and fertility data for specified countries and years.
    
    Args:
        countries: List of country codes (ISO 3-letter codes)
        start_year: Starting year for data collection
        end_year: Ending year for data collection
        
    Returns:
        Dictionary containing combined data with GDP and fertility information
    """
    try:
        logger.info(f"Fetching combined data for countries: {countries}")
        
        gdp_data = fetch_gdp_data(countries, start_year, end_year)
        fertility_data = fetch_fertility_data(countries, start_year, end_year)
        
        # Combine the data into a structure suitable for visualization
        combined_data = {
            "countries": {},
            "years": list(range(start_year, end_year + 1)),
            "metadata": {
                "gdp_indicator": GDP_INDICATOR,
                "fertility_indicator": FERTILITY_INDICATOR,
                "start_year": start_year,
                "end_year": end_year
            }
        }
        
        for country in countries:
            if country in gdp_data or country in fertility_data:
                combined_data["countries"][country] = {
                    "gdp": gdp_data.get(country, {}),
                    "fertility": fertility_data.get(country, {})
                }
        
        logger.info(f"Successfully combined data for {len(combined_data['countries'])} countries")
        return combined_data
        
    except Exception as e:
        logger.error(f"Error fetching combined data: {str(e)}")
        raise


def get_available_countries() -> List[Dict[str, str]]:
    """
    Get list of available countries from World Bank API.
    
    Returns:
        List of dictionaries containing country code, name, and region
    """
    try:
        logger.info("Fetching available countries")
        
        # First, get region mappings
        region_map = {}
        try:
            for region in wb.region.list():
                if isinstance(region, dict):
                    region_map[region.get('code', region.get('id', ''))] = region.get('name', 'Unknown')
        except Exception as e:
            logger.warning(f"Could not fetch region mappings: {e}")
        
        # Fetch economies with their metadata
        countries = []
        
        # Get all economies (countries) - filter out aggregates
        for economy in wb.economy.list():
            # Skip aggregate regions (like Africa Eastern and Southern)
            if isinstance(economy, dict) and not economy.get('aggregate', True):
                region_code = economy.get('region', '')
                countries.append({
                    'code': economy['id'],
                    'name': economy['value'],
                    'region': region_map.get(region_code, region_code or 'Unknown')
                })
        
        logger.info(f"Found {len(countries)} available countries")
        return countries
        
    except Exception as e:
        logger.error(f"Error fetching available countries: {str(e)}")
        raise


def validate_country_codes(countries: List[str]) -> List[str]:
    """
    Validate country codes against available countries.
    
    Args:
        countries: List of country codes to validate
        
    Returns:
        List of valid country codes
    """
    try:
        available_countries = get_available_countries()
        available_codes = {country['code'] for country in available_countries}
        
        valid_codes = [code for code in countries if code in available_codes]
        invalid_codes = [code for code in countries if code not in available_codes]
        
        if invalid_codes:
            logger.warning(f"Invalid country codes: {invalid_codes}")
        
        return valid_codes
        
    except Exception as e:
        logger.error(f"Error validating country codes: {str(e)}")
        raise