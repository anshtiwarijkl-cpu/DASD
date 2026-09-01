# vicle.py - Vehicle Information System for Vercel
# Author: @KINGFFAIAK47x

import requests
from flask import Flask, request, jsonify
import time
import urllib3
import json
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ===============================================
# SCRAPERAPI PROXY CONFIGURATION
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
    """Fetch vehicle details from VahanX API"""
    rc = rc_number.strip().upper()
    
    # Direct API endpoint
    url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    try:
        # Try without proxy first
        response = requests.get(url, headers=HEADERS, verify=False, timeout=30)
        
        if response.status_code == 200:
            return parse_response(response)
        else:
            # Try with ScraperAPI proxy
            return get_with_proxy(rc)
            
    except Exception as e:
        # Try with proxy on error
        return get_with_proxy(rc)

def get_with_proxy(rc_number: str):
    """Fetch using ScraperAPI proxy"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    proxies = {
        "http": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
        "https": f"https://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"
    }
    
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
            return {"status": "error", "message": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def parse_response(response):
    """Parse API response"""
    try:
        data = response.json()
        
        # Check if data is in expected format
        if "status" in data and data["status"] == "success":
            return parse_vehicle_data(data)
        elif "data" in data:
            return parse_vehicle_data(data["data"])
        else:
            return parse_vehicle_data(data)
            
    except json.JSONDecodeError:
        # If not JSON, try HTML parsing
        return parse_html(response.text)

def parse_vehicle_data(data):
    """Parse vehicle data from JSON"""
    result = {
        "status": "success",
        "owner_details": {},
        "vehicle_details": {},
        "insurance_details": {},
        "registration_details": {},
        "important_dates": {},
        "contact_details": {}
    }
    
    # Owner Details
    owner_fields = {
        "owner_name": "Owner Name",
        "owner_serial": "Owner Serial",
        "registered_rto": "Registered RTO",
        "first_owner": "First Owner"
    }
    for key, label in owner_fields.items():
        if key in data and data[key]:
            result["owner_details"][label] = data[key]
    
    # Vehicle Details
    vehicle_fields = {
        "model_name": "Model Name",
        "maker_model": "Maker Model",
        "vehicle_class": "Vehicle Class",
        "fuel_type": "Fuel Type",
        "chassis_number": "Chassis Number",
        "engine_number": "Engine Number"
    }
    for key, label in vehicle_fields.items():
        if key in data and data[key]:
            result["vehicle_details"][label] = data[key]
    
    # Insurance Details
    insurance_fields = {
        "insurance_expiry": "Insurance Expiry",
        "insurance_no": "Insurance Number",
        "insurance_company": "Insurance Company"
    }
    for key, label in insurance_fields.items():
        if key in data and data[key]:
            result["insurance_details"][label] = data[key]
    
    # Registration Details
    reg_fields = {
        "registration_number": "Registration Number",
        "vehicle_age": "Vehicle Age"
    }
    for key, label in reg_fields.items():
        if key in data and data[key]:
            result["registration_details"][label] = data[key]
    
    # Important Dates
    date_fields = {
        "registration_date": "Registration Date",
        "fitness_upto": "Fitness Upto",
        "tax_upto": "Tax Upto",
        "puc_expiry": "PUC Expiry",
        "insurance_upto": "Insurance Upto"
    }
    for key, label in date_fields.items():
        if key in data and data[key]:
            result["important_dates"][label] = data[key]
    
    # Contact Details
    contact_fields = {
        "phone": "Phone",
        "mobile": "Mobile",
        "address": "Address",
        "city": "City",
        "state": "State",
        "pincode": "Pincode"
    }
    for key, label in contact_fields.items():
        if key in data and data[key]:
            result["contact_details"][label] = data[key]
    
    # Remove empty sections
    for key in list(result.keys()):
        if isinstance(result[key], dict) and not result[key]:
            del result[key]
    
    return result

def parse_html(html_content):
    """Parse HTML as fallback"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    result = {
        "status": "success",
        "details": {}
    }
    
    # Extract all divs with labels
    for div in soup.find_all("div", class_=re.compile("info|card|detail")):
        span = div.find("span")
        p = div.find("p")
        if span and p:
            label = span.get_text(strip=True)
            value = p.get_text(strip=True)
            if label and value:
                result["details"][label] = value
    
    return result

# ===============================================
# FLASK ROUTES
# ===============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Vehicle Information API",
        "version": "4.0",
        "author": "@KINGFFAIAK47x",
        "proxy_type": "ScraperAPI + Direct API",
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
        
        if data.get("status") == "error":
            data["author"] = "@KINGFFAIAK47x"
            data["response_time_ms"] = response_time_ms
            return jsonify(data), 404
        
        data["response_time_ms"] = response_time_ms
        data["author"] = "@KINGFFAIAK47x"
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "author": "@KINGFFAIAK47x"
        }), 500

# ===============================================
# VERIFICATION FUNCTION (for testing)
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
    print("🚗 Vehicle Information System v4.0")
    print("👤 Author: @KINGFFAIAK47x")
    print("🔐 Mode: Direct API + ScraperAPI Fallback")
    print("✅ Running on: http://localhost:8888")
    print("\n📋 Test Commands:")
    print("  http://localhost:8888/api/vehicle-info?rc=MH12DE1433")
    print("  http://localhost:8888/health")
    print("  http://localhost:8888/")
    
    # Test automatically
    print("\n🔍 Running test for MH12DE1433...")
    test_vehicle_info("MH12DE1433")
    
    app.run(host="0.0.0.0", port=8888, debug=False)
