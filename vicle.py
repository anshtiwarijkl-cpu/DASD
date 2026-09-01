# vicle.py - Vehicle Information System for Vercel with ScraperAPI Proxy
# Author: @KINGFFAIAK47x

import requests
from flask import Flask, request, jsonify
import time
import urllib3
import json

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
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/html, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ===============================================
# DIRECT API CALL TO VAHANX
# ===============================================
def get_vehicle_details(rc_number: str):
    """Fetch vehicle details directly from VahanX API"""
    rc = rc_number.strip().upper()
    
    # VahanX API endpoint
    url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    try:
        # Direct request without proxy first
        response = requests.get(
            url,
            headers=HEADERS,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                return parse_api_response(data)
            except:
                # If direct fails, try with proxy
                return get_vehicle_details_with_proxy(rc)
        else:
            # Try with proxy
            return get_vehicle_details_with_proxy(rc)
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_vehicle_details_with_proxy(rc_number: str):
    """Fetch using ScraperAPI proxy"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    proxies = {
        "https": f"scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"
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
            data = response.json()
            return parse_api_response(data)
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def parse_api_response(data):
    """Parse VahanX API JSON response"""
    try:
        result = {
            "status": "success",
            "owner_details": {},
            "vehicle_details": {},
            "insurance_details": {},
            "registration_details": {},
            "important_dates": {},
            "contact_details": {},
            "challan_info": {},
            "full_data": data  # Keep full data for reference
        }
        
        # Extract owner details
        if "owner_name" in data:
            result["owner_details"]["owner_name"] = data.get("owner_name", "N/A")
        if "owner_serial" in data:
            result["owner_details"]["owner_serial"] = data.get("owner_serial", "N/A")
        if "registered_rto" in data:
            result["owner_details"]["registered_rto"] = data.get("registered_rto", "N/A")
        
        # Extract vehicle details
        vehicle = data.get("vehicle", {})
        if isinstance(vehicle, dict):
            result["vehicle_details"]["model_name"] = vehicle.get("model_name", "N/A")
            result["vehicle_details"]["maker_model"] = vehicle.get("maker_model", "N/A")
            result["vehicle_details"]["vehicle_class"] = vehicle.get("vehicle_class", "N/A")
            result["vehicle_details"]["fuel_type"] = vehicle.get("fuel_type", "N/A")
            result["vehicle_details"]["chassis_number"] = vehicle.get("chassis_number", "N/A")
            result["vehicle_details"]["engine_number"] = vehicle.get("engine_number", "N/A")
        elif isinstance(vehicle, str):
            result["vehicle_details"]["model"] = vehicle
        
        # Extract insurance details
        insurance = data.get("insurance", {})
        if isinstance(insurance, dict):
            result["insurance_details"]["insurance_expiry"] = insurance.get("insurance_expiry", "N/A")
            result["insurance_details"]["insurance_no"] = insurance.get("insurance_no", "N/A")
            result["insurance_details"]["insurance_company"] = insurance.get("insurance_company", "N/A")
            result["insurance_details"]["insurance_status"] = insurance.get("status", "N/A")
        
        # Extract dates
        dates = data.get("dates", {})
        if isinstance(dates, dict):
            result["important_dates"]["registration_date"] = dates.get("registration_date", "N/A")
            result["important_dates"]["fitness_upto"] = dates.get("fitness_upto", "N/A")
            result["important_dates"]["tax_upto"] = dates.get("tax_upto", "N/A")
            result["important_dates"]["puc_expiry"] = dates.get("puc_expiry", "N/A")
            result["important_dates"]["insurance_upto"] = dates.get("insurance_upto", "N/A")
        
        # Extract registration
        reg = data.get("registration", {})
        if isinstance(reg, dict):
            result["registration_details"]["registration_number"] = reg.get("registration_number", rc)
            result["registration_details"]["vehicle_age"] = reg.get("vehicle_age", "N/A")
        
        # Extract contact
        contact = data.get("contact", {})
        if isinstance(contact, dict):
            result["contact_details"]["phone"] = contact.get("phone", "N/A")
            result["contact_details"]["mobile"] = contact.get("mobile", "N/A")
            result["contact_details"]["address"] = contact.get("address", "N/A")
            result["contact_details"]["city"] = contact.get("city", "N/A")
            result["contact_details"]["state"] = contact.get("state", "N/A")
            result["contact_details"]["pincode"] = contact.get("pincode", "N/A")
        
        # Extract challan info
        challan = data.get("challan", {})
        if isinstance(challan, dict):
            result["challan_info"]["total_challan"] = challan.get("total", "N/A")
            result["challan_info"]["pending"] = challan.get("pending", "N/A")
            result["challan_info"]["paid"] = challan.get("paid", "N/A")
        
        # Keep original data for complete info
        result["raw_data"] = data
        
        # Remove empty sections
        for key in list(result.keys()):
            if isinstance(result[key], dict) and not any(v and v != "N/A" for v in result[key].values()):
                del result[key]
        
        # Clean N/A values
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: v for k, v in d.items() if v and v != "N/A" and v != ""}
            return d
        
        result = {k: clean_dict(v) if isinstance(v, dict) else v for k, v in result.items()}
        
        # Remove raw_data if too large
        if "raw_data" in result:
            del result["raw_data"]
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": f"Parse error: {str(e)}"}

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
        "proxy_type": "Direct API + ScraperAPI Fallback",
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
# MAIN
# ===============================================
if __name__ == "__main__":
    print("🚗 Vehicle Information System v4.0")
    print("👤 Author: @KINGFFAIAK47x")
    print("🔐 Mode: Direct API + Proxy Fallback")
    print("✅ Running on: http://localhost:8888")
    app.run(host="0.0.0.0", port=8888, debug=False)
