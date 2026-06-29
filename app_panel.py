from flask import Flask, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__, static_folder='.')

# Definimos la ruta absoluta al archivo para evitar errores de ubicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python", "solicitudes.json")

# Servir el archivo HTML del panel
@app.route('/')
def index():
    return send_from_directory('.', 'panel-admin.html')

# Servir el JSON
@app.route('/datos')
def get_datos():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Recibir el pedido de "Atendido"
@app.route('/atender/<int:id>', methods=['POST'])
def atender(id):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for item in data:
            if item['id'] == id:
                item['estado'] = 'atendido'
        
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Servidor iniciado. Buscando datos en: {JSON_PATH}")
    app.run(port=5000)