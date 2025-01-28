from flask import Flask, request, jsonify
import sqlite3
import json
from flask_cors import CORS
from datetime import datetime
import re
import os

app = Flask(__name__)
CORS(app)

# Load country-to-fiat mapping
def load_country_fiat_mapping(exchange_name):
    file_path = os.path.join(os.path.expanduser('~'), 'database', exchange_name, 'fiat2country.json')
    with open(file_path, "r") as f:
        return json.load(f)

# Database connection function
def get_db_connection(exchange_name):
    db_path = os.path.join(os.path.expanduser('~'), 'database', f'{exchange_name}_data.db')
    return sqlite3.connect(db_path)

# Root path handler
@app.route('/')
def home():
    return "Server is running"

# Rest of your existing code remains the same
def calculate_liquidity(fiat_table, payment_methods, exchange_name):
    conn = get_db_connection(exchange_name)
    cursor = conn.cursor()
    
    query = f"""
    SELECT price, available_amount, payment_methods
    FROM {fiat_table}
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        conn.close()
        raise ValueError(f"Table '{fiat_table}' does not exist in the database.")
    finally:
        conn.close()
    
    total_liquidity = 0
    weighted_price_sum = 0
    for row in rows:
        price, available_amount, methods = row
        methods_set = set(method.strip() for method in methods.split(","))
        
        processed = False
        
        if "Bank Transfer" in payment_methods:
            if any("bank" in method.lower() for method in methods_set):
                if not processed:
                    total_liquidity += available_amount
                    weighted_price_sum += price * available_amount
                    processed = True
        
        if not processed and methods_set.intersection(payment_methods):
            total_liquidity += available_amount
            weighted_price_sum += price * available_amount
            processed = True

    vwap = weighted_price_sum / total_liquidity if total_liquidity > 0 else 0

    return {"specific_liquidity": f"{total_liquidity:.2f}", "specific_vwap": f"{vwap:.2f}"}

def fetch_and_format_data(exchange_name):
    conn = get_db_connection(exchange_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT date_time, country, fiat_currency, total_liquidity, volume_weighted_price, exchange_rate, spread, available_payment_methods FROM dashboard")
    rows = cursor.fetchall()
    conn.close()
    
    formatted_data = []
    for row in rows:
        raw_payment_methods = row[7]
        payment_methods_list = []
        date_time = row[0]
        formatted_date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        
        for method in raw_payment_methods.split(','):
            method = method.strip()
            if '(' in method and ')' in method:
                parts = method.split('(')
                method_name = parts[0].strip()
                liquidity = parts[1].split(')')[0].strip()
                vwap = parts[2].split(')')[0].strip() if len(parts) > 2 else None
                payment_methods_list.append({"method": method_name, "liquidity": liquidity, "vwap": vwap})
        
        formatted_data.append({
            "date_time": formatted_date_time,
            "country": row[1],
            "fiat_currency": row[2],
            "total_liquidity": row[3],
            "volume_weighted_price": row[4],
            "exchange_rate": row[5],
            "spread": row[6],
            "available_payment_methods": payment_methods_list
        })
    
    return formatted_data

def fetch_data_from_db(exchange_name):
    conn = get_db_connection(exchange_name)
    cursor = conn.cursor()
    cursor.execute("SELECT country, total_liquidity, spread, available_payment_methods FROM dashboard")
    data = cursor.fetchall()
    conn.close()
    return data

@app.route('/calculate', methods=['GET'])
def calculate_dashboard_metrics():
    exchange_name = request.args.get('exchange', 'okx')
    data = fetch_data_from_db(exchange_name)
    
    total_liquidity = 0
    total_spread = 0
    total_countries = set()
    unique_payment_methods = set()
    seen_payment_methods = set()

    for row in data:
        country, liquidity, spread, payment_methods = row
        total_liquidity += liquidity
        spread_value = float(re.sub(r'[^\d.]', '', spread))
        total_spread += spread_value
        total_countries.add(country)
        
        methods = re.findall(r'\b[\w\s]+(?:\(\d+\.\d+\))?', payment_methods)
        for method in methods:
            method_name = method.split('(')[0].strip()
            if method_name not in seen_payment_methods:
                seen_payment_methods.add(method_name)
                unique_payment_methods.add(method_name)
    
    avg_spread = total_spread / len(data) if data else 0

    result = {
        'total_liquidity': total_liquidity,
        'average_spread': avg_spread,
        'total_countries': len(total_countries),
        'unique_payment_methods_count': len(unique_payment_methods)
    }

    return jsonify(result)

@app.route('/get_liquidity', methods=['POST'])
def get_liquidity():
    try:
        data = request.json
        country = data.get('country')
        payment_methods = data.get('payment_methods', [])
        
        if not country or not payment_methods:
            return jsonify({"error": "Country and payment methods are required"}), 400
        
        fiat_table = None
        exchange_name = request.args.get('exchange', 'okx')
        
        COUNTRY_TO_FIAT = load_country_fiat_mapping(exchange_name)
        for fiat, mapped_country in COUNTRY_TO_FIAT.items():
            if mapped_country.lower() == country.lower():
                fiat_table = fiat
                break
        
        if not fiat_table:
            return jsonify({"error": f"Country '{country}' is not recognized"}), 404

        payment_methods = set(payment_methods)
        result = calculate_liquidity(fiat_table, payment_methods, exchange_name)
        return jsonify(result)
    
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        exchange_name = request.args.get('exchange', 'okx')
        data = fetch_and_format_data(exchange_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/logs', methods=['GET'])
def get_logs():
    exchange_name = request.args.get('exchange')

    if not exchange_name:
        return jsonify({"error": "Exchange name is required"}), 400

    conn = get_db_connection(exchange_name)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(logs)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'timestamp' not in columns:
            return jsonify({"error": "'timestamp' column is missing in the logs table"}), 500

        query = "SELECT * FROM logs ORDER BY timestamp DESC"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"message": "No data found"}), 404

        response_data = []
        for row in rows:
            log_entry = {}
            for idx, column in enumerate(columns):
                if column == 'timestamp':
                    log_entry[column] = datetime.strptime(row[idx], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
                else:
                    log_entry[column] = row[idx]
            response_data.append(log_entry)

        return jsonify(response_data), 200  

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)