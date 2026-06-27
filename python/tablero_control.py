from flask import Flask, render_template
import json
import os

# Al definir app así, Flask busca automáticamente en la carpeta 'templates'
app = Flask(__name__)

ARCHIVO_DB = "base_datos_clientes.json"

def cargar_datos():
    if not os.path.exists(ARCHIVO_DB):
        return []
    with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route('/')
def home():
    clientes = cargar_datos() # Esto lee tu base de datos JSON
    # Metricas calculadas de verdad
    total_equipos = sum(c.get("equipos", 0) for c in clientes)
    
    return render_template('tablero.html', clientes=clientes, metricas={
        "equipos": total_equipos,
        "mrr": "$ -", 
        "mora": "$ -"
    })
    
    @app.route('/gestionar', methods=['POST'])
    def gestionar():
        datos = request.json
        clientes = cargar_datos()
        # Filtramos la lista para excluir al que diste de baja
        clientes = [c for c in clientes if c['nombre'] != datos['nombre']]
    
        with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
            json.dump(clientes, f, indent=4, ensure_ascii=False)
        
        return jsonify({"status": "ok"})
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)