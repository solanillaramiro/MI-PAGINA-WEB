from flask import Flask, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__, static_folder='.')
# Ruta apunta a la carpeta /python/solicitudes.json
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python", "solicitudes.json")

@app.route('/')
def index():
    return send_from_directory('.', 'panel-admin.html')

@app.route('/datos')
def get_datos():
    try:
        if not os.path.exists(JSON_PATH): return jsonify([])
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/atender/<int:id>', methods=['POST'])
def atender(id):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            if item.get('id') == id: item['estado'] = 'atendido'
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return jsonify({"status": "ok"})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)