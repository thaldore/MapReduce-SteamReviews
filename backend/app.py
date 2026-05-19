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
        import boto3
        try:
            session = boto3.Session(profile_name='MapReduce-admin')
        except Exception:
            session = boto3.Session()
        lambda_client = session.client('lambda', region_name=session.region_name or 'eu-central-1')
        # S3'e dosyalar manuel atıldığı için Map tamamlandı kabul ediyoruz. Sadece Reducer tetiklenir.
        response = lambda_client.invoke(
            FunctionName='steam-reducer',
            InvocationType='RequestResponse'
        )
        result = json.loads(response['Payload'].read().decode('utf-8'))
        return jsonify({"message": "Bulut MapReduce (Reducer) tetiklendi!", "aws_response": result})
    except Exception as e:
        # Fallback
        results = analyzer.run_analysis()
        return jsonify(results)

@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        import boto3
        try:
            session = boto3.Session(profile_name='MapReduce-admin')
        except Exception:
            session = boto3.Session()
        s3 = session.client('s3', region_name=session.region_name or 'eu-central-1')
        bucket_name = 'steam-mapreduce-tolga-2026-v2'
        
        response = s3.get_object(Bucket=bucket_name, Key='final-output/analysis_results.json')
        data = json.loads(response['Body'].read().decode('utf-8'))
        return jsonify(data)
    except Exception as e:
        results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis_results.json'))
        if os.path.exists(results_path):
            with open(results_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({"error": "Bulutta sonuç yok ve yerel sonuç da bulunamadı."}), 404

if __name__ == '__main__':
    # Flask sunucusunu başlat
    app.run(debug=True, port=5000)
