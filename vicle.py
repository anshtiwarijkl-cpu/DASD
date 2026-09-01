# vicle.py - Vehicle Information System for Vercel with ScraperAPI Proxy
# Author: @KINGFFAIAK47x

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import time
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ===============================================
# SCRAPERAPI PROXY CONFIGURATION
# ===============================================
SCRAPERAPI_KEY = "14d97e04e110dc29b6c6efc054ecd808"

# ScraperAPI proxy configuration
proxies = {
    "https": f"scraperapi.output_format=json.autoparse=true:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://vahanx.in/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ===============================================
# VEHICLE SCRAPER WITH SCRAPERAPI
# ===============================================
def get_vehicle_details(rc_number: str):
    """Fetch vehicle details using ScraperAPI proxy"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            proxies=proxies,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'html' in data:
                    return parse_response(data['html'], proxy_used="ScraperAPI")
                elif 'body' in data:
                    return parse_response(data['body'], proxy_used="ScraperAPI")
                else:
                    return parse_scraperapi_json(data)
            except:
                return parse_response(response.text, proxy_used="ScraperAPI")
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def parse_scraperapi_json(data):
    """Parse ScraperAPI JSON response"""
    try:
        result = {"status": "success"}
        
        fields = {
            'address': ['address', 'owner_address', 'reg_address', 'Address'],
            'phone': ['phone', 'mobile', 'contact', 'Phone', 'Mobile'],
            'city': ['city', 'district', 'City', 'District']
        }
        
        for key, possible_keys in fields.items():
            for possible in possible_keys:
                if possible in data:
                    result[key] = data[possible]
                    break
                for k, v in data.items():
                    if isinstance(v, dict) and possible in v:
                        result[key] = v[possible]
                        break
        
        result["proxy_used"] = "ScraperAPI"
        return {k: v for k, v in result.items() if v is not None and v != ""}
        
    except Exception as e:
        return {"status": "error", "message": f"Parse error: {str(e)}"}

def parse_response(html_content, proxy_used=None):
    """Parse HTML response with comprehensive details"""
    soup = BeautifulSoup(html_content, "html.parser")
    
    result = {
        "status": "success",
        "vehicle_details": {},
        "owner_details": {},
        "insurance_details": {},
        "registration_details": {},
        "important_dates": {},
        "challan_info": {}
    }
    
    # Helper function to extract text from element
    def get_text(element):
        if element:
            return element.get_text(strip=True)
        return None
    
    # Helper function to find value by label
    def find_value_by_label(label_text):
        # Try to find span with label
        for span in soup.find_all("span"):
            if span and label_text.lower() in span.get_text(strip=True).lower():
                # Get parent div and find value in p tag
                parent = span.find_parent("div")
                if parent:
                    p_tag = parent.find("p")
                    if p_tag:
                        return p_tag.get_text(strip=True)
        return None
    
    # Extract all card data
    cards = soup.find_all("div", class_=re.compile("hrcd-cardbody|card|info-card"))
    
    # Process each card
    for card in cards:
        # Find all span and p pairs
        items = card.find_all("div", recursive=False)
        for item in items:
            span = item.find("span")
            p = item.find("p")
            if span and p:
                label = span.get_text(strip=True)
                value = p.get_text(strip=True)
                
                # Categorize based on label
                label_lower = label.lower()
                
                # Owner Details
                if "owner" in label_lower or "name" in label_lower:
                    result["owner_details"]["owner_name"] = value
                elif "serial" in label_lower or "first owner" in label_lower:
                    result["owner_details"]["owner_serial"] = value
                elif "rto" in label_lower:
                    result["owner_details"]["registered_rto"] = value
                
                # Vehicle Details
                elif "model" in label_lower:
                    if "maker" in label_lower:
                        result["vehicle_details"]["maker_model"] = value
                    else:
                        result["vehicle_details"]["model_name"] = value
                elif "class" in label_lower:
                    result["vehicle_details"]["vehicle_class"] = value
                elif "fuel" in label_lower:
                    result["vehicle_details"]["fuel_type"] = value
                elif "chassis" in label_lower:
                    result["vehicle_details"]["chassis_number"] = value
                elif "engine" in label_lower:
                    result["vehicle_details"]["engine_number"] = value
                
                # Registration Details
                elif "registration" in label_lower or "reg no" in label_lower:
                    if "date" not in label_lower:
                        result["registration_details"]["registration_number"] = value
                
                # Insurance Details
                elif "insurance" in label_lower:
                    if "expiry" in label_lower:
                        result["insurance_details"]["insurance_expiry"] = value
                    elif "no" in label_lower:
                        result["insurance_details"]["insurance_no"] = value
                    elif "company" in label_lower:
                        result["insurance_details"]["insurance_company"] = value
                
                # Important Dates
                elif "date" in label_lower:
                    if "registration" in label_lower:
                        result["important_dates"]["registration_date"] = value
                    elif "fitness" in label_lower:
                        result["important_dates"]["fitness_upto"] = value
                    elif "tax" in label_lower:
                        result["important_dates"]["tax_upto"] = value
                    elif "puc" in label_lower:
                        if "expiry" in label_lower:
                            result["important_dates"]["puc_expiry"] = value
                        else:
                            result["important_dates"]["puc_date"] = value
                
                # Address and Contact
                elif "address" in label_lower:
                    result["address"] = value
                elif "phone" in label_lower or "mobile" in label_lower:
                    result["phone"] = value
                elif "city" in label_lower:
                    result["city"] = value
                elif "website" in label_lower:
                    result["website"] = value
                
                # Challan
                elif "challan" in label_lower:
                    result["challan_info"]["challan_status"] = value
    
    # Extract address from specific div if not found above
    if not result.get("address"):
        address_div = soup.find("div", class_=re.compile("address|Address"))
        if address_div:
            result["address"] = get_text(address_div)
    
    # Extract city from multiple sources
    if not result.get("city"):
        # Try to find city from address
        if result.get("address"):
            # Try to extract city from address
            address_parts = result["address"].split(",")
            if len(address_parts) >= 2:
                result["city"] = address_parts[-2].strip()
        else:
            city_value = find_value_by_label("City")
            if city_value:
                result["city"] = city_value
    
    # Extract phone
    if not result.get("phone"):
        phone_value = find_value_by_label("Phone")
        if not phone_value:
            phone_value = find_value_by_label("Mobile")
        if phone_value:
            result["phone"] = phone_value
    
    # Clean up - remove empty values
    for key in list(result.keys()):
        if isinstance(result[key], dict):
            result[key] = {k: v for k, v in result[key].items() if v and v != "" and v != "None"}
            if not result[key]:
                del result[key]
        elif not result[key] or result[key] == "" or result[key] == "None":
            del result[key]
    
    # Add proxy info
    if proxy_used:
        result["proxy_used"] = proxy_used
    
    return result

# ===============================================
# FLASK ROUTES
# ===============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Vehicle Information API",
        "version": "3.1",
        "author": "@KINGFFAIAK47x",
        "proxy_type": "ScraperAPI",
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
            "author": "@KINGFFAIAK47x"
        }), 400
    
    start_time = time.time()
    
    try:
        data = get_vehicle_details(rc)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if data.get("status") == "error":
            data["author"] = "@KINGFFAIAK47x"
            return jsonify(data), 404
        
        # Add response time
        data["response_time_ms"] = response_time_ms
        data["author"] = "@KINGFFAIAK47x"
        
        # Clean empty values
        data = {k: v for k, v in data.items() if v is not None and v != "" and v != {}}
        
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
    print("🚗 Vehicle Information System")
    print("👤 Author: @KINGFFAIAK47x")
    print("🔐 Proxy: ScraperAPI")
    print("✅ Running on: http://localhost:8888")
    app.run(host="0.0.0.0", port=8888, debug=False)
