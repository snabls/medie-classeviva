from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

BASE_URL = "https://web.spaggiari.eu/rest/v1"
HEADERS = {
    "User-Agent": "CVVS/std/4.1.7 Android/10",
    "Z-Dev-ApiKey": "Tg1NWEwNGIgIC0K",
    "Content-Type": "application/json"
}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    uid = data.get('uid')
    pwd = data.get('pass')
    
    response = requests.post(
        f"{BASE_URL}/auth/login", 
        json={"ident": uid, "pass": pwd, "uid": uid}, 
        headers=HEADERS
    )
    
    # SPIAMO IL LOGIN!
    print("\n--- RISPOSTA LOGIN ---")
    print(f"Status Code: {response.status_code}")
    print(f"Risposta: {response.text[:300]}...")
    print("----------------------\n")
    
    try:
        return jsonify(response.json()), response.status_code
    except:
        return jsonify({"error": "Errore server Spaggiari"}), 502

@app.route('/api/grades/', methods=['GET'])
def get_grades(ident):
    token = request.headers.get('Z-Auth-Token')
    req_headers = HEADERS.copy()
    req_headers["Z-Auth-Token"] = token
    
    print(f"\n--- CHIAMATA VOTI ---")
    print(f"Richiedo voti per ID esatto: {ident}")
    
    response = requests.get(
        f"{BASE_URL}/students/{ident}/grades", 
        headers=req_headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Risposta: {response.text[:200]}...\n")
    
    try:
        return jsonify(response.json()), response.status_code
    except:
        return jsonify({"error": "Errore voti"}), 502

if __name__ == '__main__':
    app.run(debug=True, port=5000)