import threading, time, random, json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from kafka_controller import kafka_helper
from loguru import logger
from tools import extract_symbol

cryptocurrencies = ['bitcoin', 'solana']#, 'xrp', 'cardano', 'dogecoin']

# cryptocurrencies = os.environ.get('CRYPTOCURRENCIES')
# cryptocurrencies = ast.literal_eval(cryptocurrencies)

def make_get_request(cryptocurrency, value): 
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    #server = "http://192.168.24.1:3000"
    price, symbol = extract_symbol(value)
    data = {
        '@timestamp': current_time,
        'cryptocurrency': cryptocurrency,
        'price': price,
        'symbol': symbol,
    }
    message = json.dumps(data)
    kafka_helper.add_message(f"{cryptocurrency}_topic", message)


def start_scraping(index):
    time.sleep(random.randint(5, 30))
    cryptocurrency = cryptocurrencies[index]
    print(f'Starting scraping for {cryptocurrency}')

    chrome_options = Options()
    # chrome_options.binary_location = "/mnt/c/Users/lahce/Downloads/chrome-linux64/chrome"
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--remote-debugging-port=9222')
    # Path to the ChromeDriver

    # Initialize the ChromeDriver with the specified options
    driver = webdriver.Chrome(options=chrome_options)
    while True:
        try:
            driver.get('https://coinmarketcap.com/currencies/' + cryptocurrency)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.sc-f70bb44c-0.jxpCgO.base-text')))
            price_element = driver.find_element(By.CSS_SELECTOR, 'span.sc-f70bb44c-0.jxpCgO.base-text')
            price_text = price_element.text
            if price_text:
                make_get_request(cryptocurrency, price_text)
            else:
                logger.warning(f"{cryptocurrency}: No content found, retrying...")
        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"{cryptocurrency}: Exception encountered: {e}, retrying...")
        except Exception as e:
            print(f"{cryptocurrency}: An unexpected error occurred: {e}")
            break
        time.sleep(random.randint(5, 15))
    driver.quit()

def thread_function(index):
    # Ajout d'un délai aléatoire avant de lancer le scraping
    start_scraping(index)

if __name__ == "__main__":
    threads = []
    for i in range(len(cryptocurrencies)):
        thread = threading.Thread(target=thread_function, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logger.info("Scraping completed for all cryptocurrencies.")
