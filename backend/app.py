from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import analyzer
import os
import json
import sys

# Backend klasöründe olduğumuz için analyzer modülünü bulabilmesi için yolu ekleyelim
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Frontend klasörü bir üst dizinde
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=template_dir)
CORS(app)

# Ana sayfa: Frontend'i sunar
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Frontend dosyalarını sunmak için
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/analyze', methods=['GET'])
def run_mapreduce():
    try:
        results = analyzer.run_analysis()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    # analyzer.py'nin oluşturduğu json dosyasının yolunu bulalım
    # analyzer.py ana dizindeki raw_reviews.json'a göre çalışıyor
    results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis_results.json'))
    
    if os.path.exists(results_path):
        with open(results_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({"error": "Henüz analiz yapılmamış."}), 404

if __name__ == '__main__':
    # Flask sunucusunu başlat
    app.run(debug=True, port=5000)
