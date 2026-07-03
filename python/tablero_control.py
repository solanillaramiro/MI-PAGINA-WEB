import imaplib
import email
import json
import os
from bs4 import BeautifulSoup

EMAIL_USER = "nova.termodinamica.aplicada@gmail.com"
EMAIL_PASS = "norx dutc srvy tnnp"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ahora siempre apunta a la carpeta /python/solicitudes.json
ARCHIVO_SOLICITUDES = os.path.join(BASE_DIR, "solicitudes.json")

def procesar_y_guardar(cuerpo_html, uid):
    soup = BeautifulSoup(cuerpo_html, 'html.parser')
    datos = {}
    for t in soup.find_all('strong'):
        etiqueta = t.get_text(strip=True).replace(":", "").lower()
        valor = t.find_next(['pre', 'div', 'p'])
        if valor: datos[etiqueta] = valor.get_text(strip=True)
    
    if not datos: return

    tipo = "mantenimiento" if "especialidad" in datos else "contacto"
    solicitudes = []
    if os.path.exists(ARCHIVO_SOLICITUDES):
        with open(ARCHIVO_SOLICITUDES, "r", encoding="utf-8") as f:
            try: solicitudes = json.load(f)
            except: solicitudes = []
    
    nueva_solicitud = {
        "uid": uid,
        "id": len(solicitudes) + 1,
        "fecha": "2026-06-28",
        "tipo_origen": tipo,
        "estado": "pendiente",
        "datos": datos
    }
    solicitudes.append(nueva_solicitud)
    with open(ARCHIVO_SOLICITUDES, "w", encoding="utf-8") as f:
        json.dump(solicitudes, f, indent=4, ensure_ascii=False)
    print(f"¡Solicitud procesada: {datos.get('nombre', 'Sin nombre')}!")

def leer_correos():
    # Archivo auxiliar para llevar cuenta de los UIDs ya procesados
    ARCHIVO_PROCESADOS = os.path.join(BASE_DIR, "procesados.txt")
    
    # Cargamos los IDs ya procesados
    procesados = []
    if os.path.exists(ARCHIVO_PROCESADOS):
        with open(ARCHIVO_PROCESADOS, "r") as f:
            procesados = [line.strip() for line in f.readlines()]

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        status, messages = mail.search(None, '(FROM "submissions@formsubmit.co")')
        if not messages[0]: return

        for num in messages[0].split():
            status, data = mail.fetch(num, "(UID)")
            uid = data[0].decode().split()[2]
            
            # FILTRO INFALIBLE: Si el UID está en el txt, lo ignoramos
            if uid in procesados:
                continue

            # Si es nuevo, lo procesamos
            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            
            cuerpo_html = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        cuerpo_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                cuerpo_html = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            procesar_y_guardar(cuerpo_html, uid)
            
            # Guardamos el UID como procesado para que no se repita nunca más
            with open(ARCHIVO_PROCESADOS, "a") as f:
                f.write(f"{uid}\n")
            procesados.append(uid)
            
        mail.logout()
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    leer_correos()