import sqlite3
from datetime import datetime
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

fiat_currencies = [
    "AED", "AMD", "ARS", "AUD", "AZN", "BGN", "BHD",
    "BRL", "BWP", "BYN", "CAD", "CHF", "CLP", "CNY", "COP", "CZK", "DKK", 
    "DOP", "EGP", "ETB", "EUR", "GBP", "GEL", "GHS", "HUF", "IDR", 
    "ILS", "INR", "IQD", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KWD",
    "KZT", "LAK", "LKR", "MAD", "MDL", "MOP",
    "MXN", "NOK", "NZD", "OMR", "PEN", "PKR", 
    "PLN", "PYG", "QAR", "RON", "RSD", "RWF", "SAR", "SDG", "SEK", "THB", "TJS", "TND", 
    "TRY", "TTD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES", "VND", "XAF", "XOF", 
    "ZAR", "ZMW"
]

# fiat_currencies = ["INR", "NZD", "GHS"]

def wait_for_page_to_load(driver, timeout=5):
    time.sleep(1)
    """Wait until the page content is fully loaded."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "merchant-name"))
        )
        print("Page loaded successfully.")
    except TimeoutException:
        print("Timeout while waiting for the page to load.")

def click_element(driver, xpath):
    """Click an element using JavaScript if standard click fails."""
    try:
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", element)
    except NoSuchElementException as e:
        print(f"Error occurred while locating element: {e}")

def scrape_page(driver):
    """Scrape data from the current page on OKX."""
    advertisers = []
    prices = []
    available_amounts = []
    payment_methods = []
    timestamps = []

    rows = driver.find_elements(By.CSS_SELECTOR, "tr.custom-table-row")

    if not rows:
        print("No rows found on the page.")
        return advertisers, prices, available_amounts, payment_methods, timestamps

    for row_index, row in enumerate(rows[1:], start=1):
        try:
            # Extract advertiser name
            advertiser_name_elem = row.find_element(
                By.CSS_SELECTOR, ".merchant-name a"
            )
            advertiser_name = advertiser_name_elem.text

            # Extract price
            price_elem = row.find_element(By.CSS_SELECTOR, ".price")
            price = re.sub(r"[^\d.]", "", price_elem.text).strip()
            price = float(price)

            # Extract available amount
            available_amount_elem = row.find_element(
                By.CSS_SELECTOR, ".quantity-and-limit .show-item:first-child"
            )
            available_amount = re.sub(r"[^\d.]", "", available_amount_elem.text).strip()
            available_amount = float(available_amount)

            # Extract payment methods
            payment_methods_elems = row.find_elements(
                By.CSS_SELECTOR, ".payment-item .pay-method"
            )
            payment_methods_list = [pm.text.strip() for pm in payment_methods_elems]
            payment_methods_str = ", ".join(payment_methods_list)

            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Append data to lists
            advertisers.append(advertiser_name)
            prices.append(price)
            available_amounts.append(available_amount)
            payment_methods.append(payment_methods_str)
            timestamps.append(timestamp)

            if advertisers and price and available_amount and payment_methods:
                print(f"Row {row_index} - Advertiser: {advertiser_name}, "
                      f"Price: {price}, "
                      f"Available Amount: {available_amount} USDT, "
                      f"Payment Methods: {payment_methods_str}")
        except Exception as e:
            print(f"Error occurred while processing row {row_index}: {e}")

    return advertisers, prices, available_amounts, payment_methods, timestamps

def paginate_and_load_pages(driver):
    all_advertisers = []
    all_prices = []
    all_amounts = []
    all_payment_methods = []
    all_timestamps = []

    wait_for_page_to_load(driver)
    current_page_num = 1

    print(f"Scraping page {current_page_num} (first page)...")
    advertisers, prices, amounts, payment_methods, timestamps = scrape_page(driver)
    all_advertisers.extend(advertisers)
    all_prices.extend(prices)
    all_amounts.extend(amounts)
    all_payment_methods.extend(payment_methods)
    all_timestamps.extend(timestamps)

    while True:
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.okui-pagination-next"))
            )

            # Check if the next button is disabled
            next_button_class = next_button.get_attribute("class")
            if "okui-pagination-disabled" in next_button_class:
                print("Next button is disabled. Reached the last page.")
                break

            # Add delay before moving to next page
            time.sleep(2)

            next_button.click()
            print(f"Clicked next page button. Now scraping page {current_page_num + 1}...")

            wait_for_page_to_load(driver)
            current_page_num += 1

            advertisers, prices, amounts, payment_methods, timestamps = scrape_page(driver)
            all_advertisers.extend(advertisers)
            all_prices.extend(prices)
            all_amounts.extend(amounts)
            all_payment_methods.extend(payment_methods)
            all_timestamps.extend(timestamps)

        except ElementClickInterceptedException:
            print("Next button is obscured. Trying to scroll...")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.5)  # Delay after scrolling
            try:
                # Add delay before moving to next page
                time.sleep(5)

                driver.execute_script("arguments[0].click();", next_button)
                print(
                    f"Clicked next page button after scrolling. Now scraping page {current_page_num + 1}..."
                )

                wait_for_page_to_load(driver)
                current_page_num += 1

                advertisers, prices, amounts, payment_methods, timestamps = scrape_page(driver)
                all_advertisers.extend(advertisers)
                all_prices.extend(prices)
                all_amounts.extend(amounts)
                all_payment_methods.extend(payment_methods)
                all_timestamps.extend(timestamps)

            except Exception as e:
                print(f"Failed to click next button after scrolling: {e}")
                break

        except (NoSuchElementException, TimeoutException):
            print("No more pages or unable to click the next page button.")
            break

    return all_advertisers, all_prices, all_amounts, all_payment_methods, all_timestamps

def create_database_and_tables():
    conn = sqlite3.connect("C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\database\\okx_data.db")
    cursor = conn.cursor()

    # Create Dashboard table
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
    return conn, cursor

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
    # sorted_methods = sorted(payment_dict.items(), key=lambda x: x[1], reverse=True)
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
    with open('C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\okx\\fiat2country.json', 'r') as file:
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

def main():
    options = Options()
    options.headless = False
    service = Service("C:\\Program Files\\GeckoDriver\\geckodriver.exe")
    driver = webdriver.Firefox(service=service, options=options)

    conn, cursor = create_database_and_tables()
    processed_data = {}  # To store liquidity data for logs
    # Load fiat-to-country mapping
    with open('C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\okx\\fiat2country.json', 'r') as file:
        fiat_to_country = json.load(file)

    for fiat_currency in fiat_currencies:
        # Clear existing data for this fiat currency
        clear_table_for_fiat(cursor, fiat_currency)
        clear_dashboard_for_fiat(cursor, fiat_currency)

        # Fetch data from the website
        driver.get(f"https://www.okx.com/p2p-markets/{fiat_currency}/buy-usdt")
        wait_for_page_to_load(driver)
        
        advertisers, prices, available_amounts, payment_methods, timestamps = paginate_and_load_pages(driver)
        
        # Save scraped data to the database
        save_data_to_db(cursor, fiat_currency, advertisers, prices, available_amounts, payment_methods, timestamps)
        
        # Update the dashboard with aggregated data
                # Load exchange rates
        with open("C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Binance\\exchange_rates\\exchange_rates.json", "r") as file:
            data = json.load(file)
        if fiat_currency == "USD":
            exchange_rate = 1
        else:
            new_fiat_currency = f'USD{fiat_currency}'
            exchange_rate = data["quotes"].get(new_fiat_currency)
            
        update_dashboard(cursor, fiat_currency, advertisers, available_amounts, prices, exchange_rate, payment_methods)
        
        processed_data[fiat_currency] = sum(available_amounts)

    update_logs_table(cursor, fiat_to_country, processed_data)    
    conn.commit()

    driver.quit()
    conn.close()

if __name__ == "__main__":
    main()
