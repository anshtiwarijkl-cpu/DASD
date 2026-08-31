# vicle.py - Vehicle Information System for Vercel with HTTP Proxies
# Author: @KINGFFAIAK47x

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

# ===============================================
# HTTP/HTTPS PROXY CONFIGURATION
# ===============================================
PROXY_LIST = [
    {
        "ip": "31.59.20.176",
        "port": "6754",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United Kingdom",
        "city": "London",
        "protocol": "http"
    },
    {
        "ip": "45.38.107.97",
        "port": "6014",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United Kingdom",
        "city": "London",
        "protocol": "http"
    },
    {
        "ip": "198.105.121.200",
        "port": "6462",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United Kingdom",
        "city": "London",
        "protocol": "http"
    },
    {
        "ip": "64.137.96.74",
        "port": "6641",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Spain",
        "city": "Madrid",
        "protocol": "http"
    },
    {
        "ip": "198.23.243.226",
        "port": "6361",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United States",
        "city": "Los Angeles",
        "protocol": "http"
    },
    {
        "ip": "84.247.60.125",
        "port": "6095",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Poland",
        "city": "Warsaw",
        "protocol": "http"
    },
    {
        "ip": "142.111.67.146",
        "port": "5611",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Japan",
        "city": "Tokyo",
        "protocol": "http"
    },
    {
        "ip": "191.96.254.138",
        "port": "6185",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "United States",
        "city": "Los Angeles",
        "protocol": "http"
    },
    {
        "ip": "31.58.9.4",
        "port": "6077",
        "username": "ANSHBR01",
        "password": "BRO12341",
        "country": "Germany",
        "city": "Frankfurt",
        "protocol": "http"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://vahanx.in/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Cache for working proxies
WORKING_PROXIES = []
LAST_TEST_TIME = 0

# ===============================================
# PROXY TESTING
# ===============================================
def test_proxy(proxy):
    """Test HTTP/HTTPS proxy"""
    try:
        # HTTP proxy format
        proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        test_response = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxies,
            timeout=5
        )
        
        if test_response.status_code == 200:
            return {
                "status": "working",
                "proxy": f"{proxy['ip']}:{proxy['port']}",
                "country": proxy['country'],
                "city": proxy['city'],
                "proxy_obj": proxy
            }
        return {"status": "failed"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def get_working_proxies():
    """Get working proxies with caching"""
    global WORKING_PROXIES, LAST_TEST_TIME
    
    current_time = time.time()
    
    # Cache for 5 minutes
    if WORKING_PROXIES and (current_time - LAST_TEST_TIME) < 300:
        return WORKING_PROXIES
    
    print("Testing proxies...")
    WORKING_PROXIES = []
    
    # Test proxies
    for proxy in PROXY_LIST[:5]:  # Test first 5
        result = test_proxy(proxy)
        if result.get('status') == 'working':
            WORKING_PROXIES.append(result)
            print(f"✅ {proxy['ip']}:{proxy['port']} WORKING")
        else:
            print(f"❌ {proxy['ip']}:{proxy['port']} FAILED")
        time.sleep(0.3)
    
    LAST_TEST_TIME = current_time
    print(f"Total working: {len(WORKING_PROXIES)}")
    return WORKING_PROXIES

# ===============================================
# VEHICLE SCRAPER
# ===============================================
def get_vehicle_details(rc_number: str):
    """Fetch vehicle details using HTTP proxy"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    
    working_proxies = get_working_proxies()
    
    # Try without proxy if no working proxies
    if not working_proxies:
        print("No working proxies, trying direct...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return parse_response(response.text)
        except:
            pass
        return {"status": "error", "message": "No working proxies and direct request failed"}
    
    # Try with proxies
    random.shuffle(working_proxies)
    
    for proxy_info in working_proxies[:3]:
        try:
            proxy_obj = proxy_info['proxy_obj']
            proxy_url = f"http://{proxy_obj['username']}:{proxy_obj['password']}@{proxy_obj['ip']}:{proxy_obj['port']}"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            response = requests.get(
                url,
                headers=HEADERS,
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                return parse_response(response.text, proxy_obj)
                
        except Exception as e:
            continue
    
    # Fallback: Try without proxy
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return parse_response(response.text)
    except:
        pass
    
    return {"status": "error", "message": "All requests failed"}

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
        "version": "2.0",
        "author": "@KINGFFAIAK47x",
        "proxy_type": "HTTP/HTTPS",
        "proxy_count": len(PROXY_LIST),
        "endpoints": {
            "vehicle_info": "/api/vehicle-info?rc=<RC_NUMBER>",
            "test_proxies": "/api/test-proxies",
            "health": "/health"
        }
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
    """Test proxies endpoint"""
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
        
        if data.get("proxy_used"):
            ordered_data["proxy_used"] = data.get("proxy_used")
        
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
    app.run(host="0.0.0.0", port=8888, debug=False)
