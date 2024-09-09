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

1. **Download ChromeDriver**: Make sure you have ChromeDriver installed and available in your system's PATH. You can download it from here.

2. **Environment Variables**: Create a `.env` file in the root directory of your project and add the following environment variables:

```env
SENDER_EMAIL=your_email@example.com
RECEIVER_EMAIL=receiver_email@example.com
EMAIL_PASSWORD=your_email_password
```

3. **Excel File**: The script will create an `jobs.xlsx` file if it does not already exist. If the file exists, it will be updated with new job listings.

## Usage

1. **Update the URL**: Modify the `URL` variable in the `__main__` section of `scraper.py` to point to the job listings page you want to scrape.

2. **Run the Script**: Execute the script using Python:

```bash
python scraper.py
```

3. **Check Results**: The script will print updates to the console. New jobs will be added to the `jobs.xlsx file`, and you will receive an email notification with details of the new job listings.

## Code Explanation

- **Initialization**: Configures Selenium to run in headless mode and sets up the path for the Excel file.  
- **Selenium Initialization**: Launches a headless browser, accepts cookies, and scrolls to load job listings.
- **BeautifulSoup Initialization**: Parses the page source to extract job details.
- **Scraping Jobs**: Extracts job details and compares them with existing data to avoid duplicates.
- **Filtering New Jobs**: Updates the existing Excel file with new job listings and sends an email notification.
- **Sending Email**: Sends an email with details of new job listings.

## Contributing

Feel free to fork this repository and submit pull requests. If you encounter any issues, please open an issue ticket.

