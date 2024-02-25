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
