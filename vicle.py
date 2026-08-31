# vicle.py - Enhanced Vehicle Information System with Mandatory Proxy
# Author: @KINGFFAIAK47x
# Description: Vehicle details scraper with Webshare proxy (proxy mandatory for every request)

import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

# ===============================================
# PROXY CONFIGURATION FROM WEBSHARE
# ===============================================
PROXY_LIST = [
    {
        "ip": "31.59.20.176",
        "port": "6754",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United Kingdom",
        "city": "London"
    },
    {
        "ip": "45.38.107.97",
        "port": "6014",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United Kingdom",
        "city": "London"
    },
    {
        "ip": "198.105.121.200",
        "port": "6462",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United Kingdom",
        "city": "London"
    },
    {
        "ip": "64.137.96.74",
        "port": "6641",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Spain",
        "city": "Madrid"
    },
    {
        "ip": "198.23.243.226",
        "port": "6361",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United States",
        "city": "Los Angeles"
    },
    {
        "ip": "84.247.60.125",
        "port": "6095",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Poland",
        "city": "Warsaw"
    },
    {
        "ip": "142.111.67.146",
        "port": "5611",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Japan",
        "city": "Tokyo"
    },
    {
        "ip": "191.96.254.138",
        "port": "6185",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United States",
        "city": "Los Angeles"
    },
    {
        "ip": "31.58.9.4",
        "port": "6077",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Germany",
        "city": "Frankfurt"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://vahanx.in/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Store working proxies
WORKING_PROXIES = []
last_test_time = 0

# ===============================================
# PROXY TESTING FUNCTION
# ===============================================
def test_proxy(proxy):
    """Test if proxy is working"""
    try:
        proxy_url = f"socks5://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}/"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        test_response = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxies,
            timeout=10
        )
        
        if test_response.status_code == 200:
            ip_data = test_response.json()
            return {
                "status": "working",
                "proxy_ip": ip_data.get('ip'),
                "proxy": f"{proxy['ip']}:{proxy['port']}",
                "country": proxy['country'],
                "city": proxy['city'],
                "proxy_obj": proxy
            }
        else:
            return {"status": "failed", "proxy": f"{proxy['ip']}:{proxy['port']}"}
    except Exception as e:
        return {"status": "failed", "proxy": f"{proxy['ip']}:{proxy['port']}", "error": str(e)}

def get_working_proxies():
    """Get list of working proxies"""
    global WORKING_PROXIES, last_test_time
    
    # Test proxies if list is empty or last test was more than 5 minutes ago
    current_time = time.time()
    if not WORKING_PROXIES or (current_time - last_test_time) > 300:
        print("🔄 Testing proxies...")
        WORKING_PROXIES = []
        
        for proxy in PROXY_LIST:
            print(f"🔍 Testing {proxy['ip']}:{proxy['port']}...", end=" ")
            result = test_proxy(proxy)
            
            if result['status'] == 'working':
                print(f"✅ WORKING")
                WORKING_PROXIES.append(result)
            else:
                print(f"❌ FAILED")
            
            time.sleep(0.5)
        
        last_test_time = current_time
        print(f"✅ Total working proxies: {len(WORKING_PROXIES)}\n")
    
    return WORKING_PROXIES

# ===============================================
# VEHICLE INFO SCRAPER WITH MANDATORY PROXY
# ===============================================
def get_vehicle_details_with_proxy(rc_number: str):
    """Fetch vehicle details using proxy - proxy is mandatory"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    
    # Get working proxies
    working_proxies = get_working_proxies()
    
    if not working_proxies:
        return {
            "status": "error", 
            "message": "No working proxies available. Please check your proxy configuration."
        }
    
    # Shuffle for rotation
    random.shuffle(working_proxies)
    
    last_error = None
    
    for proxy_info in working_proxies:
        try:
            proxy_obj = proxy_info['proxy_obj']
            proxy_url = f"socks5://{proxy_obj['username']}:{proxy_obj['password']}@{proxy_obj['ip']}:{proxy_obj['port']}/"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            print(f"🔄 Trying proxy: {proxy_obj['ip']}:{proxy_obj['port']} ({proxy_obj['country']})")
            
            response = requests.get(
                url,
                headers=HEADERS,
                proxies=proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Success with proxy: {proxy_obj['ip']}:{proxy_obj['port']}")
                return parse_response(response.text, proxy_obj)
            else:
                last_error = f"Status: {response.status_code}"
                print(f"❌ Failed: {last_error}")
                
        except Exception as e:
            last_error = str(e)
            print(f"❌ Error: {last_error}")
            continue
    
    return {
        "status": "error", 
        "message": f"All proxies failed. Last error: {last_error}"
    }

def parse_response(html_content, proxy_used=None):
    """Parse HTML response and extract vehicle details"""
    soup = BeautifulSoup(html_content, "html.parser")
    
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
    
    def extract_card(label):
        for div in soup.select(".hrcd-cardbody"):
            span = div.find("span")
            if span and label.lower() in span.text.lower():
                p = div.find("p")
                return p.get_text(strip=True) if p else None
        return None
    
    address = extract_card("Address") or get_value("Address")
    city = extract_card("City Name") or get_value("City Name")
    phone = extract_card("Phone") or get_value("Phone")
    
    data = {
        "status": "success",
        "address": address,
        "phone": phone,
        "city": city
    }
    
    if proxy_used:
        data["proxy_used"] = f"{proxy_used['ip']}:{proxy_used['port']} ({proxy_used['country']})"
    
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
        "service": "Vehicle Information API",
        "version": "2.0",
        "author": "@KINGFFAIAK47x",
        "proxy_support": "Webshare Proxies (Mandatory)",
        "proxy_count": len(PROXY_LIST),
        "endpoints": {
            "vehicle_info": "/api/vehicle-info?rc=<RC_NUMBER>",
            "test_proxies": "/api/test-proxies",
            "health": "/health"
        },
        "example": "http://localhost:8888/api/vehicle-info?rc=DL01AB1234"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "api": "active",
        "author": "@KINGFFAIAK47x",
        "working_proxies": len(WORKING_PROXIES),
        "timestamp": time.time()
    })

@app.route("/api/test-proxies", methods=["GET"])
def test_proxies():
    """Test all configured proxies"""
    start_time = time.time()
    working = get_working_proxies()
    response_time_ms = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "status": "success",
        "total_proxies": len(PROXY_LIST),
        "working_proxies_count": len(working),
        "working_proxies": [
            {
                "proxy": p['proxy'],
                "country": p['country'],
                "city": p['city']
            } for p in working
        ],
        "response_time_ms": response_time_ms,
        "author": "@KINGFFAIAK47x"
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
        data = get_vehicle_details_with_proxy(rc)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if data.get("status") == "error":
            data["author"] = "@KINGFFAIAK47x"
            return jsonify(data), 404
        
        # Create ordered response
        ordered_data = {
            "status": data.get("status"),
            "address": data.get("address"),
            "phone": data.get("phone"),
            "city": data.get("city"),
            "response_time_ms": response_time_ms,
            "author": "@KINGFFAIAK47x"
        }
        
        # Add proxy info if available
        if data.get("proxy_used"):
            ordered_data["proxy_used"] = data.get("proxy_used")
        
        # Remove None values
        ordered_data = {k: v for k, v in ordered_data.items() if v is not None and v != ""}
        return jsonify(ordered_data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "author": "@KINGFFAIAK47x"
        }), 500

# ===============================================
# CONSOLE DISPLAY
# ===============================================
def print_banner():
    banner = f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🚗 VEHICLE INFORMATION SYSTEM 🚗                   ║
║                                                           ║
║     Proxy is MANDATORY for every request                  ║
║     Proxy Provider: Webshare                             ║
║     Author: @KINGFFAIAK47x                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"📊 Total Proxies: {len(PROXY_LIST)}")
    print(f"🔍 Testing proxies on startup...\n")
    get_working_proxies()

# ===============================================
# MAIN
# ===============================================
if __name__ == "__main__":
    print_banner()
    print("✅ API Running on: http://localhost:8888")
    print("📡 Test Proxies: http://localhost:8888/api/test-proxies")
    print("🚗 Vehicle Info: http://localhost:8888/api/vehicle-info?rc=DL01AB1234")
    print("\n" + "="*60 + "\n")
    app.run(host="0.0.0.0", port=8888, debug=False)
