from flask import Flask, render_template, request, jsonify
from automata import FiniteAutomata
import database
import webbrowser  # <--- Make sure this is here!
from threading import Timer  # <--- Make sure this is here!

app = Flask(__name__)
fa_engine = FiniteAutomata()

# Initialize Database
database.init_db()

def heuristic_score(text):
    """Calculates a suspiciousness score based on non-keyword features."""
    score = 0
    # 1. Check for excessive caps (Worth 30 points)
    if len(text) > 0 and sum(1 for c in text if c.isupper()) / (len(text) + 1) > 0.4:
        score += 30 
    # 2. Check for excessive exclamation marks (Worth 20 points)
    if text.count('!') > 2:
        score += 20 
    # 3. Check for dollar signs (Worth 50 points)
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
    
    patterns, logs = fa_engine.scan_text(message)
    h_score = heuristic_score(message)
    
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
    """Opens the browser automatically after 1.5 seconds."""
    print("--------------------------------------------------")
    print(">>> LAUNCHING BROWSER NOW: http://127.0.0.1:5000 <<<")
    print("--------------------------------------------------")
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    # The timer waits 1.5 seconds to ensure the server is ready
    Timer(1.5, open_browser).start()
    
    # Note: debug=True allows auto-reload but might sometimes launch two browser tabs.
    # If it opens twice, change to debug=False for your final presentation.
    app.run(debug=False)