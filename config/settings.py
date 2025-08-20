"""
Configuration settings for Local Food Wastage Management System
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Database settings
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_NAME = "food_management.db"
DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

# CSV file paths
CSV_FILES = {
    'providers': RAW_DATA_DIR / "providers_data.csv",
    'receivers': RAW_DATA_DIR / "receivers_data.csv",
    'food_listings': RAW_DATA_DIR / "food_listings_data.csv",
    'claims': RAW_DATA_DIR / "claims_data.csv"
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': 'Local Food Wastage Management System',
    'page_icon': '🍽️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Create directories if they don't exist
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DATABASE_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    create_directories()
    print("Project directories created successfully!")