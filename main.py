from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

class MojPosaoScraper():
    def __init__(self) -> None:
        '''Initializes the scraper with necessary configurations such as headless mode for Selenium and sets the Excel file path.'''
        self.options = Options()
        self.options.add_argument('--headless=new')
        self.driver = None 
        self.excel_file = 'jobs.xlsx'

    def selenium_initialization(self, URL):
        '''Launches a headless Chrome browser using Selenium, accepts cookies on the page, and scrolls to load job listings.'''
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(URL)
        self.driver.maximize_window()

        # Accept cookies
        try:
            self.accept_cookies = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="teleport"]/div[2]/div/div/div/button')))
            self.accept_cookies.click()
        except TimeoutException:
            print("No accept cookies button found.")

        time.sleep(2)

        # Scroll down the page to load all job listings
        self.scroll_increment = 0
        while self.scroll_increment < 500: 
            self.driver.execute_script(f"window.scrollTo(0, {self.scroll_increment * 10});")
            time.sleep(0.75)
            self.scroll_increment += 100

        time.sleep(2)

        # After loading the page, initialize BeautifulSoup for further scraping
        self.bs4_initialization()

    def bs4_initialization(self):
        '''Fetches the page source using Selenium and initializes BeautifulSoup for parsing the HTML content.'''
        self.page_source = self.driver.page_source
        self.driver.quit()

        self.soup = BeautifulSoup(self.page_source, "html.parser")

        # Scrape job listings
        self.scrape_jobs()

    def scrape_jobs(self):
        '''Extracts job details such as position, company, location, application deadline, and link from the page using BeautifulSoup.'''
        self.data = []

        # Find all content boxes and corresponding image boxes
        self.content_boxes = self.soup.find_all("div", class_="mp-card mp-card--border-light-only mp-card--corners-round-md job-card mp-box mp-box--shade-60 mp-box--shadow-shallow mp-card mp-card--border-light-only mp-card--corners-round-md job-card") 
        self.image_boxes = self.soup.find_all("div", class_="logo-container")

        # Loop through each content_box and corresponding image_box
        for content_box, image_box in zip(self.content_boxes, self.image_boxes):
            # Extract the company name
            self.company = image_box.find("img", class_="logo-container__image").get("alt")

            # Find all the nested content elements within each content_box
            nested_content_boxes = content_box.find_all("div", class_="content")
            
            for nested_content in nested_content_boxes:
                # Extract job title, location, application date, and link
                self.title = nested_content.find("h3", class_="header__title mp-text mp-text__h5 mp-text__h5--bold mp-text--link-card header__title")
                self.location = nested_content.find("span", class_="mp-text mp-text__default mp-text__default--regular mp-text--no-margin")
                self.application_date = nested_content.find("time", class_="mp-text mp-text__default mp-text__default--bold mp-text--no-margin")
                self.link = nested_content.find("div", class_="content__header header").find("a")

                # Only append to data if all elements are found
                if self.title and self.location and self.application_date and self.link:
                    self.data.append({
                        'Pozicija': self.title.getText() if self.title else 'Data not found',
                        'Firma': self.company if self.company else 'Data not found',
                        'Lokacija': self.location.getText() if self.location else 'Data not found',
                        'Datum prijave do': self.application_date.getText() if self.application_date else 'Data not found',
                        'Link': f'https://mojposao.hr{self.link.get("href")}' if self.link else 'Data not found'
                    })


        # Load existing data and compare
        self.filter_new_jobs()

    def filter_new_jobs(self):
        '''Compares the new job listings with the existing Excel file to avoid duplicates. Updates the existing file with new listings.'''
        if os.path.exists(self.excel_file):
            existing_jobs = pd.read_excel(self.excel_file)

            # Convert the new data to a DataFrame
            new_jobs_df = pd.DataFrame(self.data)

            # Check for duplicates by comparing Pozicija, Firma, and Lokacija
            merged_jobs = pd.merge(existing_jobs, new_jobs_df, on=['Pozicija', 'Firma', 'Lokacija'], how='right', indicator=True)

            # Filter out the rows that already exist in the Excel file
            new_jobs_only = merged_jobs[merged_jobs['_merge'] == 'right_only'].drop(columns='_merge')

            # Remove any extra columns (_x, _y) and retain only the necessary columns
            new_jobs_only = new_jobs_only[['Pozicija', 'Firma', 'Lokacija', 'Datum prijave do_y', 'Link_y']]
            new_jobs_only.columns = ['Pozicija', 'Firma', 'Lokacija', 'Datum prijave do', 'Link']  # Rename the columns

            if not new_jobs_only.empty:
                # Update the existing Excel file with new jobs
                with pd.ExcelWriter(self.excel_file, mode='a', if_sheet_exists='overlay') as writer:
                    new_jobs_only.to_excel(writer, index=False, header=False, startrow=len(existing_jobs)+1)

                print(f"{len(new_jobs_only)} new job(s) found and added to {self.excel_file}.")
                # Send new jobs by email
                self.send_email(new_jobs_only)
            else:
                print("No new jobs found.")
        else:
            # If the Excel file doesn't exist, save all the new jobs
            self.save_to_excel()

    def save_to_excel(self):
        '''Saves the scraped data to an Excel file if it does not exist.'''
        df = pd.DataFrame(self.data)
        df.to_excel(self.excel_file, index=False)
        print(f"Data has been saved to {self.excel_file}.")

    def send_email(self, new_jobs):
        '''Sends an email with information about new job listings.'''
        load_dotenv()

        # Email setup
        sender_email = os.getenv('SENDER_EMAIL')
        receiver_email = os.getenv('RECEIVER_EMAIL')
        subject = "Novi poslovi na mojposao.hr"
        password = os.getenv('EMAIL_PASSWORD')

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Prepare the email body
        num_new_jobs = len(new_jobs)
        body = f"""\Bok,

        Dodana su {num_new_jobs} nova posla:
        """

        # Append details of each new job to the email body
        for index, job in new_jobs.iterrows():
            body += f"""
        Pozicija: {job['Pozicija']}
        Firma: {job['Firma']}
        Lokacija: {job['Lokacija']}
        Datum prijave do: {job['Datum prijave do']}
        Link: {job['Link']}
            """

        body += """\Lp, Frane"""

        msg.attach(MIMEText(body, 'plain'))

        # Sending the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")

if __name__ == "__main__":
    # URL for job scraping
    URL = "https://mojposao.hr/pretraga-poslova?positions=IT,+telekomunikacije&locations=Grad+Zagreb+i+Zagreba%C4%8Dka+%C5%BEupanija"
    
    scraper = MojPosaoScraper()
    scraper.selenium_initialization(URL)
