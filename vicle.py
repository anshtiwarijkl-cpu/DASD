# vicle.py - Vehicle Information System for Vercel
# Author: @KINGFFAIAK47x

import requests
from flask import Flask, request, jsonify
import time
import urllib3
import json
import re
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ===============================================
# SCRAPERAPI CONFIGURATION
# ===============================================
SCRAPERAPI_KEY = "14d97e04e110dc29b6c6efc054ecd808"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://vahanx.in/",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ===============================================
# VEHICLE DETAILS FETCHER
# ===============================================
def get_vehicle_details(rc_number: str):
    """Fetch vehicle details from VahanX API with ScraperAPI fallback"""
    rc = rc_number.strip().upper()
    
    # Direct API endpoint
    url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    # Try direct first
    try:
        response = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        if response.status_code == 200:
            return parse_response(response)
    except Exception as e:
        print(f"Direct API failed: {e}")
    
    # If direct fails, use ScraperAPI
    return get_with_scraperapi(rc)

def get_with_scraperapi(rc_number: str):
    """Fetch using ScraperAPI structured API"""
    rc = rc_number.strip().upper()
    url = "https://api.scraperapi.com/structured/web/v1"
    
    # Use ScraperAPI's structured web scraping
    params = {
        'api_key': SCRAPERAPI_KEY,
        'url': f"https://vahanx.in/api/rc_search/?number={rc}",
        'render': 'true',
        'country_code': 'in',
        'premium_proxy': 'true'
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            # Try to parse as JSON
            try:
                data = response.json()
                return parse_response_from_data(data)
            except:
                # If not JSON, try HTML parsing
                return parse_html(response.text)
        else:
            # Fallback to traditional proxy
            return get_with_proxy(rc)
            
    except Exception as e:
        # Last resort: traditional proxy
        return get_with_proxy(rc)

def get_with_proxy(rc_number: str):
    """Fetch using ScraperAPI proxy fallback"""
    rc = rc_number.strip().upper()
    
    # Use ScraperAPI proxy with proper format
    proxy_url = f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"
    
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            proxies=proxies,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            return parse_response(response)
        else:
            return {
                "status": "error", 
                "message": f"HTTP {response.status_code}",
                "author": "@KINGFFAIAK47x"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "author": "@KINGFFAIAK47x"
        }

def parse_response(response):
    """Parse API response"""
    try:
        data = response.json()
        return parse_response_from_data(data)
    except json.JSONDecodeError:
        return parse_html(response.text)

def parse_response_from_data(data):
    """Parse vehicle data from JSON"""
    # If data is already the vehicle info
    if "data" in data:
        data = data["data"]
    
    # Check if we have valid data
    if not data or isinstance(data, list):
        return {
            "status": "error",
            "message": "No vehicle data found",
            "author": "@KINGFFAIAK47x"
        }
    
    result = {
        "status": "success",
        "owner_details": {},
        "vehicle_details": {},
        "insurance_details": {},
        "registration_details": {},
        "important_dates": {},
        "contact_details": {},
        "author": "@KINGFFAIAK47x"
    }
    
    # Map fields from API response
    field_mappings = {
        "owner_details": {
            "owner_name": "Owner Name",
            "owner_serial": "Owner Serial",
            "registered_rto": "Registered RTO",
            "first_owner": "First Owner"
        },
        "vehicle_details": {
            "model_name": "Model Name",
            "maker_model": "Maker Model",
            "vehicle_class": "Vehicle Class",
            "fuel_type": "Fuel Type",
            "chassis_number": "Chassis Number",
            "engine_number": "Engine Number",
            "color": "Color",
            "seating_capacity": "Seating Capacity"
        },
        "insurance_details": {
            "insurance_expiry": "Insurance Expiry",
            "insurance_no": "Insurance Number",
            "insurance_company": "Insurance Company",
            "policy_number": "Policy Number"
        },
        "registration_details": {
            "registration_number": "Registration Number",
            "vehicle_age": "Vehicle Age",
            "registering_authority": "Registering Authority"
        },
        "important_dates": {
            "registration_date": "Registration Date",
            "fitness_upto": "Fitness Upto",
            "tax_upto": "Tax Upto",
            "puc_expiry": "PUC Expiry",
            "insurance_upto": "Insurance Upto"
        },
        "contact_details": {
            "phone": "Phone",
            "mobile": "Mobile",
            "address": "Address",
            "city": "City",
            "state": "State",
            "pincode": "Pincode"
        }
    }
    
    # Populate result from data
    for section, fields in field_mappings.items():
        for key, label in fields.items():
            if key in data and data[key]:
                result[section][label] = data[key]
    
    # Remove empty sections
    for key in list(result.keys()):
        if isinstance(result[key], dict) and not result[key]:
            del result[key]
    
    return result

def parse_html(html_content):
    """Parse HTML as fallback"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        result = {
            "status": "success",
            "details": {},
            "author": "@KINGFFAIAK47x"
        }
        
        # Extract all divs with labels
        for div in soup.find_all(["div", "li", "tr"]):
            text = div.get_text(strip=True)
            if ":" in text:
                parts = text.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    value = parts[1].strip()
                    if label and value:
                        result["details"][label] = value
        
        # If no details found, try extracting from table
        if not result["details"]:
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 2:
                        label = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        if label and value:
                            result["details"][label] = value
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to parse HTML: {str(e)}",
            "author": "@KINGFFAIAK47x"
        }

# ===============================================
# FLASK ROUTES
# ===============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Vehicle Information API",
        "version": "5.0",
        "author": "@KINGFFAIAK47x",
        "proxy_type": "ScraperAPI Structured + Proxy Fallback",
        "endpoints": {
            "vehicle_info": "/api/vehicle-info?rc=<RC_NUMBER>",
            "health": "/health"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "api": "active",
        "author": "@KINGFFAIAK47x",
        "timestamp": time.time()
    })

@app.route("/api/vehicle-info", methods=["GET"])
def get_vehicle_info():
    rc = request.args.get("rc")
    
    if not rc:
        return jsonify({
            "status": "error",
            "message": "Missing rc parameter",
            "usage": "/api/vehicle-info?rc=<RC_NUMBER>",
            "author": "@KINGFFAIAK47x",
            "example": "/api/vehicle-info?rc=MH12DE1433"
        }), 400
    
    start_time = time.time()
    
    try:
        data = get_vehicle_details(rc)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        data["response_time_ms"] = response_time_ms
        data["author"] = "@KINGFFAIAK47x"
        
        if data.get("status") == "error":
            return jsonify(data), 404
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "author": "@KINGFFAIAK47x"
        }), 500

# ===============================================
# VERIFICATION FUNCTION
# ===============================================
def test_vehicle_info(rc_number):
    """Test function to check if API is working"""
    print(f"Testing for RC: {rc_number}")
    result = get_vehicle_details(rc_number)
    print(json.dumps(result, indent=2))
    return result

# ===============================================
# MAIN
# ===============================================
if __name__ == "__main__":
    print("🚗 Vehicle Information System v5.0")
    print("👤 Author: @KINGFFAIAK47x")
    print("🔐 Mode: ScraperAPI Structured + Proxy Fallback")
    print("✅ Running on: http://localhost:8888")
    print("\n📋 Test Commands:")
    print("  http://localhost:8888/api/vehicle-info?rc=MH12DE1433")
    print("  http://localhost:8888/health")
    print("  http://localhost:8888/")
    
    # Test automatically
    print("\n🔍 Running test for MH12DE1433...")
    test_vehicle_info("MH12DE1433")
    
    app.run(host="0.0.0.0", port=8888, debug=False)
