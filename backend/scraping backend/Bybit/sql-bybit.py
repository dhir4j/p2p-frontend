from datetime import datetime
import json
import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    ElementClickInterceptedException, 
    StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bybit_scraper.log'
)
logger = logging.getLogger(__name__)

# List of fiat currencies to scrape
fiat_currencies = [
    "AED", "AMD", "ARS", "AUD", "AZN", "BDT", "BGN", "BRL",
    "BYN", "CAD", "CLP", "COP", "CZK", "DZD", "EGP", "EUR",
    "GBP", "GEL", "GHS", "HKD", "HUF", "IDR", "ILS", "INR",
    "JOD", "JPY", "KES", "KGS", "KHR", "KWD", "KZT", "LBP", "LKR",
    "MAD", "MDL", "MXN", "MYR", "NGN", "NOK", "NPR",
    "NZD", "PEN", "PHP", "PKR", "PLN", "RON", "RSD", "RUB", "SAR",
    "SEK", "THB", "TJS", "TRY", "TWD", "UAH", "USD", "UZS",
    "VES", "VND", "ZAR"
]

def clean_float_value(value):
    """Clean and validate float values before sending to database."""
    if value is None:
        return 0.0
    try:
        # Remove any currency symbols and commas
        cleaned_value = re.sub(r'[^\d.,]', '', str(value)).replace(',', '')
        float_val = float(cleaned_value)
        if not (-1e308 <= float_val <= 1e308):
            return 0.0
        return float_val
    except (ValueError, TypeError) as e:
        logger.error(f"Error cleaning float value {value}: {e}")
        return 0.0

def handle_warning_popup(driver):
    """Handle potential warning pop-up and click 'Confirm'."""
    try:
        confirm_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-btn-primary')]//span[text()='Confirm']"))
        )
        confirm_button.click()
        logger.info("Warning pop-up handled successfully.")
    except TimeoutException:
        logger.debug("No warning popup found.")
    except Exception as e:
        logger.error(f"Error handling warning popup: {e}")

def close_warning_ad(driver):
    """Close the warning advertisement if present."""
    try:
        close_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".otc-ad-close"))
        )
        close_button.click()
        logger.info("Warning advertisement closed successfully.")
    except TimeoutException:
        logger.debug("No warning ad found.")
    except Exception as e:
        logger.error(f"Error closing warning ad: {e}")

def wait_for_page_to_load(driver, timeout=10):
    """Wait until the page content is fully loaded."""
    try:
        # Wait for multiple conditions to ensure page is fully loaded
        WebDriverWait(driver, timeout).until(
            EC.all_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table')),
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr')),
                EC.presence_of_element_located((By.CLASS_NAME, "advertiser-name"))
            )
        )
        time.sleep(1)  # Short delay to ensure dynamic content loads
        logger.info("Page loaded successfully.")
    except TimeoutException:
        logger.error("Timeout while waiting for the page to load.")

def extract_price(row):
    """Extract price from a row using multiple possible selectors."""
    price_selectors = [
        "span.moly-text.text-[var(--bds-gray-t1-title)].css-fdyb0r.font-[600]",
        ".price-amount",
        "moly-text text-[var(--bds-gray-t1-title)] css-fdyb0r font-[600] block",
        "span.moly-text text-[var(--bds-gray-t1-title)] css-fdyb0r font-[600] block",
        "span.moly-text.text-\\[var\\(--bds-gray-t1-title\\)\\].css-fdyb0r.font-\\[600\\]"  # Add more potential selectors
    ]
    
    for selector in price_selectors:
        try:
            price_elem = row.find_elements(By.CSS_SELECTOR, selector)
            if price_elem:
                price_text = price_elem[0].text.strip().split()[0]
                price = clean_float_value(price_text)
                if price > 0:
                    return price
        except Exception as e:
            logger.debug(f"Failed to extract price with selector {selector}: {e}")
    
    logger.warning("No valid price found, returning 0.0")
    return 0.0

def scrape_page(driver):
    """Scrape data from the current page on Bybit."""
    advertisers = []
    prices = []
    available_amounts = []
    payment_methods = []
    timestamps = []

    try:
        # Wait for rows to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr'))
        )
    except TimeoutException:
        logger.error("Timeout waiting for rows to load")
        return [], [], [], [], []

    rows = driver.find_elements(By.CSS_SELECTOR, 'tr')
    if len(rows) <= 1:
        logger.warning("No data rows found on page")
        return [], [], [], [], []

    for row_index in range(1, len(rows)):
        retry_count = 3
        while retry_count > 0:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, 'tr')
                row = rows[row_index]
                
                # Log raw HTML for debugging
                logger.debug(f"Row {row_index} HTML: {row.get_attribute('innerHTML')}")

                # Extract advertiser name
                advertiser_name_elem = row.find_elements(By.CLASS_NAME, "advertiser-name")
                advertiser_name = advertiser_name_elem[0].text if advertiser_name_elem else 'N/A'

                # Extract price using the new function
                price = extract_price(row)

                # Extract available amount
                try:
                    available_amount_elem = row.find_element(By.XPATH, ".//div[contains(@class, 'ql-value')][1]")
                    amount_text = re.findall(r'[\d,.]+', available_amount_elem.text)[0]
                    available_amount = clean_float_value(amount_text)
                except Exception as e:
                    logger.error(f"Error extracting available amount: {e}")
                    available_amount = 0.0

                # Extract payment methods
                payment_methods_elems = row.find_elements(By.CSS_SELECTOR, '.trade-list-tag')
                payment_methods_list = [pm.text for pm in payment_methods_elems]
                payment_methods_str = ', '.join(payment_methods_list) if payment_methods_list else 'N/A'

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Only append valid data
                if advertiser_name != 'N/A' or price > 0 or available_amount > 0 or payment_methods_str != 'N/A':
                    advertisers.append(advertiser_name)
                    prices.append(price)
                    available_amounts.append(available_amount)
                    payment_methods.append(payment_methods_str)
                    timestamps.append(timestamp)

                logger.info(f"Successfully scraped row {row_index}")
                break

            except StaleElementReferenceException:
                logger.warning(f"Stale element encountered at row {row_index}, retrying...")
                retry_count -= 1
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing row {row_index}: {e}")
                break

    return advertisers, prices, available_amounts, payment_methods, timestamps

def paginate_and_load_pages(driver):
    """Navigate through all pages and collect data."""
    all_advertisers = []
    all_prices = []
    all_amounts = []
    all_payment_methods = []
    all_timestamps = []

    wait_for_page_to_load(driver)
    current_page_num = 1

    while True:
        logger.info(f"Scraping page {current_page_num}")
        
        advertisers, prices, amounts, payment_methods, timestamps = scrape_page(driver)
        all_advertisers.extend(advertisers)
        all_prices.extend(prices)
        all_amounts.extend(amounts)
        all_payment_methods.extend(payment_methods)
        all_timestamps.extend(timestamps)

        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "li.pagination-next button[aria-label='next page']")
                )
            )
            
            # Try standard click first
            try:
                next_button.click()
            except ElementClickInterceptedException:
                # If standard click fails, try JavaScript click
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", next_button)

            logger.info(f"Moving to page {current_page_num + 1}")
            wait_for_page_to_load(driver)
            current_page_num += 1

        except (NoSuchElementException, TimeoutException):
            logger.info("No more pages available")
            break
        except Exception as e:
            logger.error(f"Error during pagination: {e}")
            break

    return all_advertisers, all_prices, all_amounts, all_payment_methods, all_timestamps

# Database functions remain largely the same, but with added logging
def create_database_and_tables():
    try:
        conn = sqlite3.connect("C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\database\\bybit_data.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard (
                country TEXT,
                fiat_currency TEXT,
                total_liquidity REAL,
                volume_weighted_price REAL,
                exchange_rate REAL,
                spread REAL,
                available_payment_methods TEXT,
                advertiser_count REAL,
                date_time TEXT,
                PRIMARY KEY (fiat_currency, date_time)
            )
        """)

        conn.commit()
        logger.info("Database and tables created successfully")
        return conn, cursor
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise
def process_payment_methods(prices, available_amounts, payment_methods):
    payment_dict = {}
    payment_vwap = {}

    for i, methods in enumerate(payment_methods):
        price = prices[i]
        amount = available_amounts[i]
        counted_bank = False

        for method in methods.split(","):
            method = method.strip()

            # Aggregate all methods with "bank" into "Bank Transfer"
            if "bank" in method.lower():
                if not counted_bank:
                    method_key = "Bank Transfer"
                    payment_dict[method_key] = payment_dict.get(method_key, 0) + amount
                    payment_vwap[method_key] = payment_vwap.get(method_key, 0) + price * amount
                    counted_bank = True
            else:
                # Add the amount and calculate VWAP for other methods
                if method:
                    payment_dict[method] = payment_dict.get(method, 0) + amount
                    payment_vwap[method] = payment_vwap.get(method, 0) + price * amount

    # Final VWAP calculations
    for method in payment_dict:
        if payment_dict[method] > 0:
            payment_vwap[method] = payment_vwap[method] / payment_dict[method]
        else:
            payment_vwap[method] = 0

    # Format the payment methods string
    sorted_methods = sorted(payment_dict.items(), key=lambda x: x[1], reverse=True)
    formatted_payment_methods = ", ".join(
        f"{method} ({amount:.2f}) ({vwap:.2f})"
        for method, amount, vwap in sorted([(k, payment_dict[k], payment_vwap[k]) for k in payment_dict], key=lambda x: x[1], reverse=True)
    )

    return formatted_payment_methods


def update_dashboard(cursor, fiat_currency, advertisers, available_amounts, prices, exchange_rate, payment_methods):
    total_available_amount = sum(available_amounts)
    weighted_sum = sum(price * amt for price, amt in zip(prices, available_amounts))
    vw_price = weighted_sum / total_available_amount if total_available_amount > 0 else 0

    # Process and format payment methods with VWAP
    payment_methods_str = process_payment_methods(prices, available_amounts, payment_methods)

    # Define country and current timestamp
    with open('C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Bybit\\fiat2country.json', 'r') as file:
        fiat_to_country = json.load(file)
    country = fiat_to_country.get(fiat_currency.upper())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate spread
    spread = f"{abs((exchange_rate / vw_price - 1) * 100):.2f}%" if vw_price > 0 else "0.00%"

    advertiser_count = len(advertisers)

    # Insert data into the dashboard table
    cursor.execute("""
        INSERT OR REPLACE INTO dashboard (
            country, fiat_currency, date_time, total_liquidity, 
            volume_weighted_price, exchange_rate, spread, available_payment_methods, advertiser_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (country, fiat_currency, timestamp, total_available_amount, vw_price, exchange_rate, spread, payment_methods_str, advertiser_count))

def clear_table_for_fiat(cursor, fiat_currency):
    try:
        """Clear the table for a specific fiat currency."""
        cursor.execute(f"DELETE FROM {fiat_currency}")
        print(f"Cleared existing data in {fiat_currency} table.")
    except Exception as E:
        print(E)

def clear_dashboard_for_fiat(cursor, fiat_currency):
    """Clear the dashboard for a specific fiat currency."""
    cursor.execute(f"DELETE FROM dashboard WHERE fiat_currency = ?", (fiat_currency,))
    print(f"Cleared existing data for {fiat_currency} in the dashboard.")


def update_logs_table(cursor, fiat_to_country, processed_data):
    """
    Batch update logs table with data from all processed fiats.
    :param cursor: SQLite cursor object
    :param fiat_to_country: Mapping of fiat currencies to country names
    :param processed_data: Dictionary containing fiat_currency and total_liquidity
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare a row with all country names set to 0 initially
    logs_data = {country: 0 for country in fiat_to_country.values()}

    # Map processed data to country names
    for fiat, liquidity in processed_data.items():
        country = fiat_to_country.get(fiat)
        if country:
            logs_data[country] = liquidity

    # Escape column names with double quotes
    columns = ["timestamp"] + [f'"{country}"' for country in logs_data.keys()]  # Add "timestamp" explicitly
    values = [timestamp] + list(logs_data.values())  # Add timestamp as the first value

    # Check if the number of values matches the number of columns
    print(f"Number of columns: {len(columns)}")
    print(f"Number of values: {len(values)}")

    # Check if a log already exists for this timestamp
    cursor.execute("SELECT timestamp FROM logs WHERE timestamp = ?", (timestamp,))
    existing_log = cursor.fetchone()

    if not existing_log:
        # Insert a new row with the timestamp and all country data
        placeholders = ", ".join(["?"] * len(columns))
        cursor.execute(f"""
            INSERT INTO logs ({', '.join(columns)})
            VALUES ({placeholders})
        """, values)
    else:
        print(f"Logs for timestamp {timestamp} already exist. Skipping insertion.")

    print(f"Logs updated for timestamp {timestamp}.")

def save_data_to_db(cursor, fiat_currency, advertisers, prices, available_amounts, payment_methods, timestamps):
    # Create table for the specific fiat currency if it doesn't exist
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {fiat_currency} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        advertiser_name TEXT,
        price REAL,
        available_amount REAL,
        payment_methods TEXT,
        timestamp TEXT
    )
    """)

    # Insert data into the currency table
    for i in range(len(advertisers)):
        cursor.execute(f"""
        INSERT INTO {fiat_currency} (advertiser_name, price, available_amount, payment_methods, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (advertisers[i], prices[i], available_amounts[i], payment_methods[i], timestamps[i]))

def main():
    logger.info("Starting Bybit P2P scraper")
    
    # Configure Firefox options
    options = Options()
    options.headless = True
    
    # Set up the Firefox WebDriver
    try:
        service = Service('C:\Program Files\GeckoDriver\geckodriver.exe')
        driver = webdriver.Firefox(service=service, options=options)
        logger.info("WebDriver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        return

    try:
        conn, cursor = create_database_and_tables()
        processed_data = {}

        with open('C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Bybit\\fiat2country.json', 'r') as file:
            fiat_to_country = json.load(file)
        
        for fiat_currency in fiat_currencies:
            logger.info(f"Processing {fiat_currency}")
            
            try:
                clear_table_for_fiat(cursor, fiat_currency)
                clear_dashboard_for_fiat(cursor, fiat_currency)
                
                url = f"https://www.bybit.com/en/fiat/trade/otc/buy/USDT/{fiat_currency}"
                driver.get(url)
                logger.info(f"Navigated to {url}")
                
                handle_warning_popup(driver)
                close_warning_ad(driver)
                
                advertisers, prices, available_amounts, payment_methods, timestamps = paginate_and_load_pages(driver)
                
                if advertisers:  # Only process if we have data
                    save_data_to_db(cursor, fiat_currency, advertisers, prices, available_amounts, payment_methods, timestamps)
                    
                    # Load exchange rates
                    with open("C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Binance\\exchange_rates\\exchange_rates.json", "r") as file:
                        exchange_rates_data = json.load(file)
                    
                    exchange_rate = 1 if fiat_currency == "USD" else exchange_rates_data["quotes"].get(f'USD{fiat_currency}', 0)
                    
                    update_dashboard(cursor, fiat_currency, advertisers, available_amounts, prices, exchange_rate, payment_methods)
                    processed_data[fiat_currency] = sum(available_amounts)
                
                conn.commit()
                logger.info(f"Successfully processed {fiat_currency}")
                
            except Exception as e:
                logger.error(f"Error processing {fiat_currency}: {e}")
                continue

        update_logs_table(cursor, fiat_to_country, processed_data)
        conn.commit()
        logger.info("All processing completed successfully")

    except Exception as e:
        logger.error(f"Main processing error: {e}")
    
    finally:
        driver.quit()
        conn.close()
        logger.info("Resources cleaned up, scraper shutting down")

if __name__ == "__main__":
    main()