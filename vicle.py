# vicle.py - Vehicle Information System for Vercel
# Author: @KINGFFAIAK47x

import os
import requests
from flask import Flask, request, jsonify
import time
import urllib3
import json
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ===============================================
# CONFIGURATION (from Environment Variables)
# ===============================================
SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY', '')
if not SCRAPERAPI_KEY:
    print("⚠️ WARNING: SCRAPERAPI_KEY not set in environment variables")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

# ===============================================
# VEHICLE DETAILS FETCHER
# ===============================================
def get_vehicle_details(rc_number: str):
    """Fetch vehicle details using ScraperAPI"""
    rc = rc_number.strip().upper()
    
    if not SCRAPERAPI_KEY:
        return {
            "status": "error",
            "message": "SCRAPERAPI_KEY not configured",
            "author": "@KINGFFAIAK47x"
        }
    
    url = "https://api.scraperapi.com/"
    target_url = f"https://vahanx.in/api/rc_search/?number={rc}"
    
    params = {
        'api_key': SCRAPERAPI_KEY,
        'url': target_url,
        'render': 'true',
        'country_code': 'in',
        'premium_proxy': 'true',
        'timeout': '60000'
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
            return parse_response(response)
        else:
            return {
                "status": "error",
                "message": f"ScraperAPI returned {response.status_code}",
                "author": "@KINGFFAIAK47x"
            }
            
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timed out. Please try again.",
            "author": "@KINGFFAIAK47x"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "author": "@KINGFFAIAK47x"
        }

def parse_response(response):
    """Parse API response with more details and NA handling"""
    try:
        data = response.json()
        
        if "data" in data:
            data = data["data"]
        
        if not data or isinstance(data, list):
            return {
                "status": "error",
                "message": "No vehicle data found",
                "author": "@KINGFFAIAK47x"
            }
        
        result = {
            "status": "success",
            "registration_number": data.get("registration_number", "NA"),
            "vehicle_details": {},
            "owner_details": {},
            "insurance_details": {},
            "registration_details": {},
            "important_dates": {},
            "additional_details": {},
            "author": "@KINGFFAIAK47x"
        }
        
        # =============================================
        # VEHICLE DETAILS (More Fields)
        # =============================================
        vehicle_fields = {
            "maker_model": "Make/Model",
            "model_name": "Model Name",
            "vehicle_class": "Vehicle Class",
            "body_type": "Body Type",
            "fuel_type": "Fuel Type",
            "engine_number": "Engine Number",
            "chassis_number": "Chassis Number",
            "color": "Colour",
            "seating_capacity": "Seating Capacity",
            "sleeping_capacity": "Sleeping Capacity",
            "cubic_capacity": "Cubic Capacity (CC)",
            "horse_power": "Horse Power",
            "weight": "Weight (kg)",
            "gross_weight": "Gross Weight (kg)",
            "unladen_weight": "Unladen Weight (kg)",
            "axle_weight": "Axle Weight",
            "wheel_base": "Wheel Base",
            "tyre_size": "Tyre Size",
            "number_of_tyres": "Number of Tyres",
            "fuel_type_original": "Original Fuel Type",
            "cng_kit_fitted": "CNG Kit Fitted",
            "emission_norms": "Emission Norms",
            "norms_type": "Norms Type",
            "fitment_details": "Fitment Details"
        }
        
        for key, label in vehicle_fields.items():
            result["vehicle_details"][label] = data.get(key, "NA")
        
        # =============================================
        # OWNER DETAILS
        # =============================================
        owner_fields = {
            "owner_name": "Owner Name",
            "owner_serial": "Owner Serial",
            "first_owner": "First Owner",
            "registered_rto": "Registered RTO",
            "registering_authority": "Registering Authority",
            "owner_ship_type": "Ownership Type",
            "purchase_date": "Purchase Date",
            "financier": "Financier",
            "hypothecation": "Hypothecation"
        }
        
        for key, label in owner_fields.items():
            result["owner_details"][label] = data.get(key, "NA")
        
        # =============================================
        # INSURANCE DETAILS
        # =============================================
        insurance_fields = {
            "insurance_company": "Insurance Company",
            "insurance_type": "Insurance Type",
            "insurance_no": "Insurance Number",
            "insurance_expiry": "Insurance Expiry",
            "policy_number": "Policy Number",
            "insurance_upto": "Insurance Valid Upto",
            "insurance_status": "Insurance Status"
        }
        
        for key, label in insurance_fields.items():
            result["insurance_details"][label] = data.get(key, "NA")
        
        # =============================================
        # REGISTRATION DETAILS
        # =============================================
        reg_fields = {
            "registration_date": "Registration Date",
            "registration_validity": "Registration Validity",
            "vehicle_age": "Vehicle Age (Years)",
            "registered_at": "Registered At",
            "rto_office": "RTO Office",
            "rto_code": "RTO Code",
            "state": "State",
            "district": "District",
            "city": "City"
        }
        
        for key, label in reg_fields.items():
            result["registration_details"][label] = data.get(key, "NA")
        
        # =============================================
        # IMPORTANT DATES
        # =============================================
        date_fields = {
            "registration_date": "Registration Date",
            "fitness_upto": "Fitness Certificate Valid Upto",
            "tax_upto": "Road Tax Valid Upto",
            "puc_expiry": "PUC Expiry Date",
            "insurance_upto": "Insurance Valid Upto",
            "permit_validity": "Permit Validity",
            "national_permit": "National Permit Validity",
            "fc_validity": "FC Validity"
        }
        
        for key, label in date_fields.items():
            result["important_dates"][label] = data.get(key, "NA")
        
        # =============================================
        # ADDITIONAL DETAILS
        # =============================================
        additional_fields = {
            "permit_type": "Permit Type",
            "permit_number": "Permit Number",
            "permit_issued": "Permit Issued Date",
            "permit_validity": "Permit Validity",
            "tax_amount": "Tax Amount",
            "tax_paid_upto": "Tax Paid Upto",
            "fitness_number": "Fitness Certificate Number",
            "fitness_issued": "Fitness Issued Date",
            "fitness_validity": "Fitness Validity",
            "puc_number": "PUC Certificate Number",
            "puc_issued": "PUC Issued Date",
            "puc_validity": "PUC Validity",
            "norm_type": "Norm Type",
            "vehicle_status": "Vehicle Status"
        }
        
        for key, label in additional_fields.items():
            result["additional_details"][label] = data.get(key, "NA")
        
        return result
        
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid response format",
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
        "version": "6.1",
        "author": "@KINGFFAIAK47x",
        "features": [
            "60+ Vehicle Details",
            "NA for missing fields",
            "ScraperAPI Proxy"
        ],
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
        "timestamp": int(time.time())
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
        data["response_time_ms"] = int((time.time() - start_time) * 1000)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
