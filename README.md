# MojPosao Job Scraper

This project is a job scraper for [MojPosao.hr](https://mojposao.hr) using Selenium and BeautifulSoup. It extracts job listings, updates an existing Excel file with new jobs, and sends an email notification about the new job listings.

## Features

- **Web Scraping**: Uses Selenium to interact with the web page and BeautifulSoup to parse HTML.
- **Data Management**: Updates an existing Excel file with new job listings, avoiding duplicates.
- **Email Notifications**: Sends an email with details of new job listings without attaching the Excel file.

## Prerequisites

Before running the script, ensure you have the following Python packages installed:

- `beautifulsoup4`
- `selenium`
- `pandas`
- `python-dotenv`
- `openpyxl`

You can install these packages using pip:

```bash
pip install beautifulsoup4 selenium pandas python-dotenv openpyxl
```

## Setup

- **Download ChromeDriver: Make sure you have ChromeDriver installed and available in your system's PATH. You can download it from here.

- **Environment Variables: Create a .env file in the root directory of your project and add the following environment variables:

```env
SENDER_EMAIL=your_email@example.com
RECEIVER_EMAIL=receiver_email@example.com
EMAIL_PASSWORD=your_email_password
```

- **Excel File: The script will create an jobs.xlsx file if it does not already exist. If the file exists, it will be updated with new job listings.
