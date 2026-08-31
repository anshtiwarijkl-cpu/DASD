# vicle.py - Enhanced Vehicle Information System for Vercel Deployment
# Author: @KINGFFAIAK47x
# Description: Simplified vehicle details scraper focusing on address, phone, city and status with response time

import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, request, jsonify
import time

# ===============================================
# FLASK APP SETUP
# ===============================================
app = Flask(__name__)

# ===============================================
# CONFIGURATION
# ===============================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Referer": "https://vahanx.in/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

# ===============================================
# SIMPLIFIED VEHICLE INFO SCRAPER
# ===============================================
def get_vehicle_details(rc_number: str) -> dict:
    """Simplified scraper focusing only on address, phone, city and status"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch data: {str(e)}"}

    # Helper function to extract value by label
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

    # Helper function to extract from card
    def extract_card(label):
        for div in soup.select(".hrcd-cardbody"):
            span = div.find("span")
            if span and label.lower() in span.text.lower():
                p = div.find("p")
                return p.get_text(strip=True) if p else None
        return None

    # Extract address
    address = extract_card("Address") or get_value("Address")
    
    # Extract city
    city = extract_card("City Name") or get_value("City Name")
    
    # Extract phone
    phone = extract_card("Phone") or get_value("Phone")

    # Compile data in exact order
    data = {
        "status": "success",
        "address": address,
        "phone": phone,
        "city": city
    }

    # Remove None values
    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if v is not None and v != ""}
        return d
    
    return clean_dict(data)

# ===============================================
# FLASK API ROUTES
# ===============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Vehicle Information API (Simplified)",
        "version": "2.0",
        "author": "@KINGFFAIAK47x",
        "response_time": "ms",
        "endpoints": {
            "vehicle_info": "/api/vehicle-info?rc=<RC_NUMBER>",
            "health": "/health"
        },
        "example": "https://your-vercel-app.vercel.app/api/vehicle-info?rc=DL01AB1234"
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

    # Start timer for response time
    start_time = time.time()
    
    try:
        data = get_vehicle_details(rc)
        
        # Calculate response time in milliseconds
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if data.get("status") == "error":
            data["author"] = "@KINGFFAIAK47x"
            return jsonify(data), 404
        
        # Create ordered dictionary with exact sequence: status, address, phone, city, response_time_ms, author
        ordered_data = {
            "status": data.get("status"),
            "address": data.get("address"),
            "phone": data.get("phone"),
            "city": data.get("city"),
            "response_time_ms": response_time_ms,
            "author": "@KINGFFAIAK47x"
        }
        
        # Remove None values from ordered data
        ordered_data = {k: v for k, v in ordered_data.items() if v is not None and v != ""}
        
        return jsonify(ordered_data)
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e),
            "author": "@KINGFFAIAK47x"
        }), 500

# ===============================================
# FOR VERCEL DEPLOYMENT
# ===============================================
# Vercel needs this
app.debug = False

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=False)
