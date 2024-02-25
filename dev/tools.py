import re
from loguru import logger

def remove_symbol(text):
    symbols = ['$', '€', '£', 'CHF', '¥', '₹', '₨', 'Rs', '₽', 'R']
    for symbol in symbols:
        text = text.replace(symbol, '')
    return text

def get_symbol(text):
    symbols = ['$', '€', '£', 'CHF', '¥', '₹', '₨', 'Rs', '₽', 'R']
    for symbol in symbols:
        if symbol in text:
            return symbol
    return None

def extract_symbol(price: str) -> dict:
    symbols = ['$', '€', '£', 'CHF', '¥', '₹', '₨', 'Rs', '₽', 'R']
    
    symbol = None

    for s in symbols:
        if s in price:
            symbol = s
            price = price.replace(s, '')
            break

    price = price.replace(',','')
    try:
        float(price)
    except Exception as err:
        logger.error(err)
    return (price, symbol)

def retry(max_attempts=5, delay=1, backoff=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= backoff
                    attempts += 1
            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts.")
            return None
        return wrapper
    return decorator