from flask import Flask, render_template, request, jsonify
from automata import FiniteAutomata
import database
import webbrowser
from threading import Timer
import re # Used for finding URLs
import requests # Used for the API
import os
import base64 # Needed for VirusTotal encoding

app = Flask(__name__)
fa_engine = FiniteAutomata()

# Initialize Database
database.init_db()

# --- API CONFIGURATION ---
# PASTE YOUR LONG CODE INSIDE THE QUOTES BELOW:
VIRUSTOTAL_API_KEY = "2798da73429d2f69f08cafc67aa4fd9e6871758bebfa33751241368cc3984eab"

def extract_urls(text):
    """Finds all URLs in a message using Regex."""
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.findall(text)

def check_url_api(url):
    """
    Checks a URL against a Demo Blocklist AND the VirusTotal API.
    Returns: (is_malicious, reason)
    """
    # 1. DEMO MODE: Immediate triggers for your presentation (Works without Internet)
    demo_blocklist = [
        "malicious.com",
        "phishing-login.com",
        "free-money-now.net",
        "claim-prize.xyz"
    ]
    
    for bad_site in demo_blocklist:
        if bad_site in url:
            return True, f"Known Malicious Site ({bad_site})"

    # 2. REAL API MODE: VirusTotal (Requires Internet)
    if VIRUSTOTAL_API_KEY:
        try:
            print(f"Scanning URL via VirusTotal: {url}...") # Log to terminal
            headers = {"x-apikey": VIRUSTOTAL_API_KEY}
            
            # VirusTotal requires the URL to be Base64 Encoded
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            # Send request to VirusTotal
            response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                stats = data['data']['attributes']['last_analysis_stats']
                
                # Check if any security vendor flagged it as malicious
                malicious_count = stats.get('malicious', 0)
                if malicious_count > 0:
                    return True, f"Flagged by {malicious_count} Security Vendors (VirusTotal)"
            elif response.status_code == 404:
                print("URL not found in VirusTotal database (New URL).")
            else:
                print(f"VirusTotal Error: {response.status_code}")
                
        except Exception as e:
            print(f"API Connection Failed: {e}")
            
    return False, "Safe"

def heuristic_score(text):
    """Calculates a suspiciousness score based on non-keyword features."""
    score = 0
    if len(text) > 0 and sum(1 for c in text if c.isupper()) / (len(text) + 1) > 0.4:
        score += 30
    if text.count('!') > 2:
        score += 20
    if '$' in text:
        score += 50
    return min(score, 100)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    message = data.get('message', '')
    
    # 1. Automata Check
    patterns, logs = fa_engine.scan_text(message)
    
    # 2. Heuristic Check
    h_score = heuristic_score(message)
    
    # 3. URL API Check
    urls = extract_urls(message)
    
    for url in urls:
        is_bad, reason = check_url_api(url)
        if is_bad:
            patterns.append(f"DANGEROUS URL: {url} ({reason})")
            h_score = 100 # Instant 100% Risk
    
    # 4. Final Decision
    is_spam = False
    classification = "Legitimate (Ham)"
    
    if patterns or h_score > 20:
        is_spam = True
        classification = "SPAM DETECTED"
    
    database.log_scan(message, classification, patterns)
    
    return jsonify({
        "classification": classification,
        "is_spam": is_spam,
        "patterns_found": patterns,
        "heuristic_score": h_score,
        "automata_logs": logs
    })

@app.route('/history')
def history():
    scans = database.get_recent_scans()
    return jsonify(scans)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Stops double-opening
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()
    app.run(debug=False)