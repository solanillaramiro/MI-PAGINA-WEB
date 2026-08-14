import json
import sys

ARCHIVO_SOLICITUDES = "python/solicitudes.json"

def actualizar_estado(id_solicitud):
    with open(ARCHIVO_SOLICITUDES, "r", encoding="utf-8") as f:
        solicitudes = json.load(f)
    
    for s in solicitudes:
        if s["id"] == int(id_solicitud):
            s["estado"] = "atendido"
            break
            
    with open(ARCHIVO_SOLICITUDES, "w", encoding="utf-8") as f:
        json.dump(solicitudes, f, indent=4, ensure_ascii=False)
    print("Estado actualizado")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        actualizar_estado(sys.argv[1])