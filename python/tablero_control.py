from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Apuntamos a la nueva ruta dentro de la carpeta python
ARCHIVO_SOLICITUDES = "python/solicitudes.json"

def cargar_solicitudes():
    if not os.path.exists(ARCHIVO_SOLICITUDES):
        return []
    with open(ARCHIVO_SOLICITUDES, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route('/')
def home():
    clientes = cargar_solicitudes()
    # Métrica rápida
    total_solicitudes = len(clientes)
    
    return render_template('tablero.html', clientes=clientes, metricas={
        "total": total_solicitudes,
        "pendientes": len([c for c in clientes if c['estado'] == 'pendiente'])
    })

@app.route('/gestionar', methods=['POST'])
def gestionar():
    datos = request.json
    solicitudes = cargar_solicitudes()
    
    # Lógica para actualizar el estado (por ejemplo, de 'pendiente' a 'procesado')
    for s in solicitudes:
        if s['datos_contacto']['nombre'] == datos['nombre']:
            s['estado'] = datos.get('nuevo_estado', 'procesado')
            break
            
    with open(ARCHIVO_SOLICITUDES, "w", encoding="utf-8") as f:
        json.dump(solicitudes, f, indent=4, ensure_ascii=False)
        
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)