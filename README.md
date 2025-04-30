# Python Audible Scraper

This repository contains scripts for scraping data from the user's Audible library while handling authentication. It contains very basic functionality and was the project with which I first dipped my toe into the pool of web-scraping. The goal of this project is to gather information about audiobooks, including their metadata, cover images, and other related details.

## Features

- **Authentication Handling**: Scripts include functionality to log in and maintain authenticated sessions with Audible.
- **Data Scraping**: Extract audiobook metadata, such as titles, authors, narrators, and cover images.
- **Create Markdown File** Reads the json file created via data scraping and generates a Markdown file that can then be converted to docx, pdf or whatever other format is required via Pandoc.

## Scripts Overview

### `scraper.py`

This script is responsible for:

- Logging into Audible using user credentials.
- Navigating through user's Audible library pages to collect audiobook data.
- Saving the scraped data into structured formats, specifically a .json file.  It then downloads all the cover images for the library into a specified folder.

### `create-excel.py`

- This script reads a .json file originally created by the scraper and then creates an Excel workbook containing all the books in the Audible library:
- Uses openpyxl package to create an Excel workbook.

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

Clone the repository and install the dependencies:

```PowerShell
git clone https://github.com/NelCapeTown/PythonAudibleScraperNCT
cd PythonAudibleScraperNCT
pip install -r requirements.txt
```
