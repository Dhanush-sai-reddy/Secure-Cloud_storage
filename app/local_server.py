from flask import Flask, request, jsonify
import hashlib
import json
import os

app = Flask(__name__)
INDEX_FILE = "cloud_index.json"

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    return {}

def save_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=4)

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    c_w = data.get('c_w')
    index = load_index()
    index[c_w] = {
        "c_a": data.get('c_a'),
        "c_id": data.get('c_id'),
        "original": data.get('original'),
        "v": data.get('v'),
        "f_hash": data.get('f_hash')
    }
    save_index(index)
    return jsonify({"success": True})

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    kt1 = bytes.fromhex(data.get('kt1'))
    current_pi_hex = data.get('pi')
    current_pi = bytes.fromhex(current_pi_hex)
    
    index = load_index()
    results = []
    
    while True:
        c_w = hashlib.sha256(current_pi).hexdigest()
        if c_w not in index:
            break
            
        entry = index[c_w]
        results.append({
            "c_w": c_w,
            "s3_key": entry['c_id'],
            "original": entry['original'],
            "v": entry['v'],
            "f_hash": entry['f_hash']
        })
        
        # Unmask to find next link
        c_a = bytes.fromhex(entry['c_a'])
        mask = hashlib.sha256(kt1 + current_pi).digest()[:16]
        r = xor_bytes(c_a, mask)
        
        # Step back in chain
        current_pi = xor_bytes(current_pi, r)
        
    return jsonify({
        "results": results,
        "final_pi": current_pi.hex()
    })

if __name__ == '__main__':
    print("Local Hexie Index Server running on port 5000...")
    app.run(port=5000)
