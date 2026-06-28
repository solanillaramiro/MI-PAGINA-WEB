import imaplib
import email
import json
import os
from bs4 import BeautifulSoup

# CONFIGURACIÓN
EMAIL_USER = "nova.termodinamica.aplicada@gmail.com"
EMAIL_PASS = "norx dutc srvy tnnp"
ARCHIVO_SOLICITUDES = "python/solicitudes.json"

def cargar_solicitudes():
    if not os.path.exists(ARCHIVO_SOLICITUDES): return []
    with open(ARCHIVO_SOLICITUDES, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_solicitudes(solicitudes):
    with open(ARCHIVO_SOLICITUDES, "w", encoding="utf-8") as f:
        json.dump(solicitudes, f, indent=4, ensure_ascii=False)

def procesar_y_guardar(cuerpo_html, asunto):
    soup = BeautifulSoup(cuerpo_html, 'html.parser')
    
    # 1. Extraer datos dinámicamente de cualquier campo <strong>
    datos = {}
    titulos = soup.find_all('strong')
    for t in titulos:
        etiqueta = t.get_text(strip=True).replace(":", "").lower()
        valor = t.find_next(['pre', 'div', 'p'])
        if valor:
            datos[etiqueta] = valor.get_text(strip=True)
    
    # 2. CLASIFICACIÓN INTELIGENTE
    # Si el formulario tiene "especialidad", es mantenimiento. Si no, contacto.
    if "especialidad" in datos:
        tipo = "mantenimiento"
    else:
        tipo = "contacto"
    
    # 3. Guardar con estructura limpia
    solicitudes = cargar_solicitudes()
    nueva_solicitud = {
        "id": len(solicitudes) + 1,
        "fecha": "2026-06-28",
        "tipo_origen": tipo,
        "estado": "pendiente",
        "datos": datos
    }
    
    solicitudes.append(nueva_solicitud)
    guardar_solicitudes(solicitudes)
    print(f"¡Solicitud guardada con éxito! (Tipo: {tipo})")

def leer_correos():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    
    status, messages = mail.search(None, '(UNSEEN SUBJECT "New submission")')
    
    for num in messages[0].split():
        status, data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        # Obtenemos el asunto del mail para clasificarlo
        asunto = str(msg.get("Subject"))
        
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                cuerpo = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                procesar_y_guardar(cuerpo, asunto)
    
    mail.logout()

if __name__ == "__main__":
    leer_correos()