from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
# List of fiat currencies
fiat_currencies = [
    "AED", "AMD", "AOA", "ARS", "AUD", "AZN", "BDT", "BHD", "BIF", "BND",
    "BOB", "BRL", "BWP", "BYN", "CAD", "CDF", "CHF", "CLP", "CNY", "COP",
    "CRC", "CZK", "DOP", "DZD", "EGP", "ETB", "EUR", "GBP", "GEL", "GHS",
    "GMD", "GNF", "GTQ", "HKD", "HNL", "HUF", "IDR", "INR", "IQD", "JOD",
    "JPY", "KES", "KGS", "KHR", "KWD", "KZT", "LAK", "LBP", "LKR", "MAD",
    "MDL", "MGA", "MOP", "MRU", "MXN", "MZN", "NIO", "NOK", "NPR", "OMR",
    "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD",
    "RWF", "SAR", "SDG", "SEK", "SLL", "THB", "TJS", "TND", "TRY", "TWD", 
    "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES", "VND", "XAF", "XOF",
    "YER", "ZAR", "ZMW"
]

# fiat_currencies = [
#      "LKR"
# ]

# ---- Data Retrieval ----
def scrape_page(driver):
    """Scrape data from the current page."""
    advertisers = []
    prices = []
    amounts = []
    payment_methods = []
    timestamps = []

    rows = driver.find_elements(By.CSS_SELECTOR, 'tr')

    if not rows:
        print("No rows found on the page.")
        return advertisers, prices, available_amount, payment_methods
    
    for row_index, row in enumerate(rows[1:], start=1):
        try:
            # Use XPath to extract the advertiser name
            name_elem = row.find_element(By.CSS_SELECTOR, "a[href^='/en/advertiserDetail']")
            advertiser_name = name_elem.text

            # Extract price (convert to float)
            price_elem = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2) .headline5')
            price = price_elem.text.replace(',', '')  # Remove any commas from numbers
            price = float(price)  # Convert string to float

            # Extract available amount (clean up "USDT" text and convert to float)
            amount_elem = row.find_element(By.CSS_SELECTOR, 'td:nth-child(3) .body3')
            available_amount = amount_elem.text.replace(' USDT', '').replace(',', '')  # Remove "USDT" and commas
            available_amount = float(available_amount)  # Convert string to float

            # Extract payment methods
            payment_methods_elems = row.find_elements(By.CSS_SELECTOR, 'td:nth-child(4) .PaymentMethodItem__text')
            payment_methods_list = [pm.text for pm in payment_methods_elems]
            payment_methods_str = ', '.join(payment_methods_list)
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Append data to lists
            advertisers.append(advertiser_name)
            prices.append(price)
            amounts.append(available_amount)
            payment_methods.append(payment_methods_str)
            timestamps.append(timestamp)

            print(f"Row {row_index} - Advertiser: {advertiser_name}, "
                      f"Price: {price}, "
                      f"Available Amount: {available_amount} USDT, "
                      f"Payment Methods: {payment_methods_str}")
        except NoSuchElementException:
            None
        except Exception as e:
            print(f"Error occurred while processing a row: {e}")

    return advertisers, prices, amounts, payment_methods, timestamps

def paginate_and_load_pages(driver):
    """Handle pagination by clicking the next page button."""
    all_advertisers = []
    all_prices = []
    all_amounts = []
    all_payment_methods = []
    all_timestamps = []

    # Explicitly wait for the first page to fully load
    wait_for_page_to_load(driver)

    # Get the maximum page number from the pagination
    page_numbers = get_page_numbers(driver)
    max_pages = max(page_numbers) if page_numbers else 1
    print(f"Detected maximum page number: {max_pages}")

    # Scrape the first page
    current_page_num = 1
    print(f"Scraping page {current_page_num} (first page)...")
    advertisers, prices, amounts, payment_methods, timestamps = scrape_page(driver)
    all_advertisers.extend(advertisers)
    all_prices.extend(prices)
    all_amounts.extend(amounts)
    all_payment_methods.extend(payment_methods)
    all_timestamps.extend(timestamps)

    # Handle pagination by clicking the next button until no more pages or max page is reached
    while current_page_num < max_pages:
        # Close any potential overlays
        close_overlays(driver)

        # Locate and click the "Next Page" button
        try:
            print("Clicking next page...")
            next_button_xpath = "//div[@class='bn-pagination-next' and not(@aria-disabled='true')]"
            click_element(driver, next_button_xpath)

            # Explicitly wait for the page to load
            wait_for_page_to_load(driver)

            # Increment page number
            current_page_num += 1
            print(f"Scraping page {current_page_num}...")
            advertisers, prices, amounts, payment_methods, timestamps = scrape_page(driver)
            all_advertisers.extend(advertisers)
            all_prices.extend(prices)
            all_amounts.extend(amounts)
            all_payment_methods.extend(payment_methods)
            all_timestamps.extend(timestamps)

        except NoSuchElementException:
            print("No more pages to scrape. Stopping pagination.")
            break  # Break if the next page button is not found

    print(f"Stopped scraping after reaching max page limit of {max_pages} pages.")
    return all_advertisers, all_prices, all_amounts, all_payment_methods, all_timestamps



def get_page_numbers(driver):
    """Retrieve the available page numbers from the pagination."""
    try:
        # Wait for the pagination items to be present
        page_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='bn-pagination-item' and not(contains(text(), '...'))]"))
        )
        # Extract the page numbers and convert them to integers
        return [int(elem.text) for elem in page_elements if elem.text.isdigit()]
    except TimeoutException:
        print("Timeout while waiting for pagination elements.")
        return []


def wait_for_page_to_load(driver, timeout=5):
    """Wait until the page content is fully loaded."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/en/advertiserDetail']"))
        )
        print("Page loaded successfully.")
    except TimeoutException:
        print("Timeout while waiting for the page to load.")

def close_overlays(driver):
    """Close any overlays or pop-ups that may obstruct the pagination elements."""
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='onetrust-close-btn-container']"))
        ).click()
    except (TimeoutException, NoSuchElementException):
        # print("No overlay found or unable to close overlay.")
        None

def click_element(driver, xpath):
    """Click an element using JavaScript if standard click fails."""
    try:
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", element)
    except NoSuchElementException as e:
        print(f"Error occurred while locating element: {e}")

def create_database_and_tables():
    conn = sqlite3.connect("C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\database\\binance_data.db")
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
    with open('C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Binance\\fiat2country.json', 'r') as file:
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


# ---- Main Function to Load and Scrape Pages ----
def main():
    # Configure Firefox options
    options = Options()
    options.headless = True # Set to True to run the browser in headless mode

    # Set up the Firefox WebDriver
    service = Service('C:\Program Files\GeckoDriver\geckodriver.exe')  # Path to your geckodriver
    driver = webdriver.Firefox(service=service, options=options)

    conn, cursor = create_database_and_tables()
    processed_data = {}  # To store liquidity data for logs

    with open('C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Binance\\fiat2country.json', 'r') as file:
        fiat_to_country = json.load(file)
    
    for fiat_currency in fiat_currencies:
        clear_table_for_fiat(cursor, fiat_currency)
        clear_dashboard_for_fiat(cursor, fiat_currency)
        # Print the message before scraping
        print(f"Scraping {fiat_currency}...")

            # Construct the URL dynamically for each currency
        driver.get(f"https://p2p.binance.com/en/trade/all-payments/USDT?fiat={fiat_currency}")

# Handle pagination and data extraction
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