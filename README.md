# Audible Scraper with Auth

This repository contains scripts for scraping data from Audible while handling authentication. The goal of this project is to gather information about audiobooks, including their metadata, cover images, and other related details. We are planning to convert this project into a Python package for easier reuse and distribution.

## Features
- **Authentication Handling**: Scripts include functionality to log in and maintain authenticated sessions with Audible.
- **Data Scraping**: Extract audiobook metadata, such as titles, authors, narrators, and cover images.
- **Planned Python Package**: Future updates will focus on modularizing the code and turning this repository into a Python package.

## Scripts Overview

### `scraper.py`
This script is responsible for:
- Logging into Audible using user credentials.
- Navigating through Audible's pages to collect audiobook data.
- Saving the scraped data into structured formats, such as JSON or CSV.

### `auth_manager.py`
This script manages authentication by:
- Handling login sessions with Audible.
- Refreshing tokens or cookies to maintain active sessions.
- Providing reusable authentication functions for other scripts.

### `data_processor.py`
This script processes the scraped data:
- Cleans and formats the raw data for better usability.
- Removes duplicates and handles missing fields.
- Prepares data for export or further analysis.

## Requirements
- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/NelCapeTown/Audible-Scraper-with-Auth.git
cd Audible-Scraper-with-Auth
pip install -r requirements.txt
