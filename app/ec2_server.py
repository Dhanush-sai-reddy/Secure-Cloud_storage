import hashlib
from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# The Encrypted Inverted Index
cloud_index = {}

INDEX_FILE = "cloud_index.json"

def load_index():
    """Loads the index from disk if it exists,and isnt  empty."""
     
    if os.path.exists(INDEX_FILE):
        try:
         if os.path.getsize(INDEX_FILE) > 0:
           with open(INDEX_FILE, 'r') as f:
            return json.load(f)
        except:
          print("Cloud_index.json is corrupted , Resetting to Empty")

    return {}

def save_index(index):
    """Saves the current index to a JSON file on the EC2 disk."""
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f)

cloud_index = load_index()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

# ADD THIS: This stops that "Not Found" error in the browser
@app.route('/')
def home():
    return "<h1>Hexie Cloud Server is Online</h1><p>Send POST requests to /update or /search.</p>"

@app.route('/update', methods=['POST'])
def update():
    """Algorithm 2: Update"""
    data = request.json
    c_w = data['c_w']
# Store all metadata including the tag 'v'
    cloud_index[c_w] = {
        'c_a': data['c_a'],
        'c_id': data['c_id'],
'original':data.get('original','unknown'),
'v':data.get('v'),
'f_hash':data.get('f_hash')
    }
    save_index(cloud_index)
    return jsonify({"status": "success"})

@app.route('/search', methods=['POST'])
def search():
    """Algorithm 5: Search"""
    data = request.json
    kt1 = bytes.fromhex(data['kt1'])
    current_pi = bytes.fromhex(data['pi'])
    
    results = []
    stop_signal = b'1' * 16 

    while True:
        c_w = hashlib.sha256(current_pi).hexdigest()
        if c_w not in cloud_index:
            break
            
        entry = cloud_index[c_w]
        c_a = bytes.fromhex(entry['c_a'])
        
        mask = hashlib.sha256(kt1 + current_pi).digest()[:16] 
        r = xor_bytes(c_a, mask)
        
        results.append({
's3_key':entry['c_id'],
'original':entry['original'],
'c_w':c_w,                         # Required for client to re-verify the tag
'v':entry.get('v'),
'f_hash':entry.get('f_hash')
})
        current_pi = xor_bytes(current_pi, r)
        
        if current_pi == stop_signal:
            break

    return jsonify({"results": results,"final_pi":current_pi.hex()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
