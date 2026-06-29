import imaplib
import email
import json
import os
from bs4 import BeautifulSoup

EMAIL_USER = "nova.termindinamica.aplicada@gmail.com"
EMAIL_PASS = "norx dutc srvy tnnp"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_SOLICITUDES = os.path.join(BASE_DIR, "solicitudes.json")

def procesar_y_guardar(cuerpo_html, uid):
    soup = BeautifulSoup(cuerpo_html, 'html.parser')
    datos = {}
    for t in soup.find_all('strong'):
        etiqueta = t.get_text(strip=True).replace(":", "").lower()
        valor = t.find_next(['pre', 'div', 'p'])
        if valor:
            datos[etiqueta] = valor.get_text(strip=True)
    
    if not datos: return

    tipo = "mantenimiento" if "especialidad" in datos else "contacto"
    
    if not os.path.exists(ARCHIVO_SOLICITUDES):
        solicitudes = []
    else:
        with open(ARCHIVO_SOLICITUDES, "r", encoding="utf-8") as f:
            try: solicitudes = json.load(f)
            except: solicitudes = []
    
    nueva_solicitud = {
        "uid": uid, # Guardamos el ID único de Gmail
        "id": len(solicitudes) + 1,
        "fecha": "2026-06-28",
        "tipo_origen": tipo,
        "estado": "pendiente",
        "datos": datos
    }
    solicitudes.append(nueva_solicitud)
    
    with open(ARCHIVO_SOLICITUDES, "w", encoding="utf-8") as f:
        json.dump(solicitudes, f, indent=4, ensure_ascii=False)
    print(f"¡Solicitud procesada: {datos.get('nombre', 'Sin nombre')} (UID: {uid})!")

def leer_correos():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, '(FROM "submissions@formsubmit.co")')
        if not messages[0]:
            print("No se encontraron correos nuevos.")
            return

        # Cargamos el archivo una sola vez
        if os.path.exists(ARCHIVO_SOLICITUDES):
            with open(ARCHIVO_SOLICITUDES, 'r', encoding='utf-8') as f:
                try: solicitudes = json.load(f)
                except: solicitudes = []
        else: solicitudes = []

        for num in messages[0].split():
            status, data = mail.fetch(num, "(UID)")
            uid = data[0].decode().split()[2]
            
            # Si el UID ya está en el JSON, lo ignoramos
            if any(sol.get('uid') == uid for sol in solicitudes):
                continue

            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            
            # Buscamos el contenido HTML
            cuerpo_html = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        cuerpo_html = part.get_payload(decode=True).decode()
            else:
                cuerpo_html = msg.get_payload(decode=True).decode()
            
            procesar_y_guardar(cuerpo_html, uid)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    leer_correos()