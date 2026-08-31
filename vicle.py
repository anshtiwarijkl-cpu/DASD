# vicle.py - Vehicle Information System for Vercel with ScraperAPI Proxy
# Author: @KINGFFAIAK47x

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ===============================================
# SCRAPERAPI PROXY CONFIGURATION
# ===============================================
SCRAPERAPI_KEY = "14d97e04e110dc29b6c6efc054ecd808"

proxies = {
  "https": "scraperapi.output_format=json.autoparse=true:14d97e04e110dc29b6c6efc054ecd808@proxy-server.scraperapi.com:8001"
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
            proxies=PROXY_CONFIG,
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
    """Parse HTML response"""
    soup = BeautifulSoup(html_content, "html.parser")
    
    def extract_card(label):
        for div in soup.select(".hrcd-cardbody"):
            span = div.find("span")
            if span and label.lower() in span.text.lower():
                p = div.find("p")
                return p.get_text(strip=True) if p else None
        return None
    
    def get_value(label):
        try:
            div = soup.find("span", string=label)
            if div:
                div = div.find_parent("div")
                p = div.find("p") if div else None
                return p.get_text(strip=True) if p else None
        except:
            return None
        return None
    
    address = extract_card("Address") or get_value("Address")
    city = extract_card("City Name") or get_value("City Name") or get_value("City")
    phone = extract_card("Phone") or get_value("Phone") or get_value("Mobile")
    
    data = {
        "status": "success",
        "address": address,
        "phone": phone,
        "city": city
    }
    
    if proxy_used:
        data["proxy_used"] = proxy_used
    
    data = {k: v for k, v in data.items() if v is not None and v != ""}
    return data

# ===============================================
# FLASK ROUTES
# ===============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Vehicle Information API",
        "version": "3.0",
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
        
        ordered_data = {
            "status": data.get("status"),
            "address": data.get("address"),
            "phone": data.get("phone"),
            "city": data.get("city"),
            "response_time_ms": response_time_ms,
            "author": "@KINGFFAIAK47x"
        }
        
        ordered_data = {k: v for k, v in ordered_data.items() if v is not None and v != ""}
        return jsonify(ordered_data)
        
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
