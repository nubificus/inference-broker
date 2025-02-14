from flask import Flask, request, jsonify, send_from_directory
from client import Client
import os
from io import BytesIO

# get os env if set else default to 192.168.11.57
HOST = os.getenv('HOST_ENDPOINT', '192.168.11.57')
PORT = int(os.getenv('PORT', "1234"))

esp_client = Client(HOST, PORT)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    threshold = request.form.get('threshold')
    top_k = request.form.get('topk')
    out = BytesIO()
    file.save(out)
    out.seek(0)
    try:
        threshold = float(threshold) if threshold else None
    except ValueError:
        return jsonify({'error': 'Invalid Top_K value'}), 400
    try:
        top_k = int(top_k) if top_k else None
    except ValueError:
        return jsonify({'error': 'Invalid Top_K value'}), 400
    try:
        result = esp_client.infer(out.read(), threshold, top_k)
        result = result.to_dict()
        result['application_type'] = os.getenv('APPLICATION_TYPE', 'inference')
        print("got result")
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def dump_env():
    print("Dumping ENV variables:")
    for key, value in os.environ.items():
        print(f"{key}={value}")
    
if __name__ == '__main__':
    app.run(port=8001, host='0.0.0.0')
