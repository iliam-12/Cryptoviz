import time, random, json, argparse, sys, requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from kafka_producer import KafkaHelper
from loguru import logger
from tools import extract_symbol, remove_symbol, get_symbol
from bs4 import BeautifulSoup


class Scrapper:
    def __init__(self):
        self.kafka = KafkaHelper()
        topics = self.kafka.get_list_topics()

    def scraper(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        rows = soup.find('tbody').find_all('tr')

        dataset = []
        for row in rows:
            try:
                data = {}
                columns = row.find_all('td')

                data['Rank'] = columns[1].find('p').text.strip()
                data['Cryptocurrency'] = columns[2].find('p').text.strip()
                data['Devise'] = columns[9].find('div').find('p').text.strip().split(" ")[1]
                data['Price'] = remove_symbol(columns[3].find('span').text.strip().replace(",",""))
                data['Symbol'] = get_symbol(columns[3].find('span').text.strip().replace(",",""))
                data['1h %'] = columns[4].find('span').text.strip().replace("%", "")
                data['24h %'] = columns[5].find('span').text.strip().replace("%", "")
                data['7d %'] = columns[6].find('span').text.strip().replace("%", "")
                data['Market Cap'] = remove_symbol(columns[7].find_all('span')[1].text.replace(",", ""))
                data['Volume(24h)'] = remove_symbol(columns[8].find('p').text.strip().replace(",",""))
                data['Circulating Supply'] = columns[9].find('div').find('p').text.strip().split(" ")[0].replace(",", "")
                data['@timestamp'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

                dataset.append(data)
            except Exception as err:
                logger.error(err)
                pass
        logger.info("scraping finish")
        self.kafka.add_message("cryptocurrencies_topic", json.dumps(dataset))


    def run(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--incognito')

        hub_url = "http://chrome-webdriver:4444/wd/hub"

        driver = webdriver.Remote(command_executor=hub_url, options=chrome_options)
        # driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://coinmarketcap.com/coins/')

        print(f'Selenium starting...')

        while True:
            try:
                height = driver.execute_script("return document.body.scrollHeight")
                start = 0
                for i in range(10, 0, -1):
                    driver.execute_script(f"window.scrollTo({start}, {height/i})")
                    start = height/i
                    time.sleep(1)
                html_content = driver.page_source

                self.scraper(html_content)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    Scrapper().run()
    logger.info("Scraping completed for all cryptocurrencies.")
