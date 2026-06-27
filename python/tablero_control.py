import json
import os

ARCHIVO_DB = "base_datos_clientes.json"
# Simulamos el archivo temporal que generaría tu formulario web cuando alguien se registra
ARCHIVO_WEB_ENTRADA = "registro_formulario_web.json" 

VALOR_ABONO_POR_EQUIPO = 20000

def cargar_datos():
    if not os.path.exists(ARCHIVO_DB):
        # Si no existe la DB, arrancamos vacíos o con datos iniciales
        with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return []
    with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(lista_clientes):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(lista_clientes, f, indent=4, ensure_ascii=False)

# =====================================================================
# NUEVO: EL PUENTE WEB -> BACKEND (OPCIÓN A)
# =====================================================================
def sincronizar_datos_web(clientes_locales):
    print("\n🌐 [Sincronizador Web] Buscando nuevas solicitudes de mantenimiento...")
    
    # Verificamos si la web dejó algún archivo con clientes nuevos
    if not os.path.exists(ARCHIVO_WEB_ENTRADA):
        print("ℹ️ No hay registros nuevos en la cola del formulario web por el momento.")
        return clientes_locales

    try:
        with open(ARCHIVO_WEB_ENTRADA, "r", encoding="utf-8") as f:
            nuevos_registros = json.load(f)
        
        print(f"📥 ¡Se encontraron {len(nuevos_registros)} solicitudes nuevas desde la web!")
        
        # Procesamos y validamos cada cliente que vino de internet
        for nuevo in nuevos_registros:
            # Validación básica: Nos aseguramos de que no esté duplicado por nombre
            existe = any(c["nombre"].lower() == nuevo["nombre"].lower() for c in clientes_locales)
            
            if not existe:
                # Forzamos que el estado inicial de la web sea siempre 'Pendiente'
                nuevo["estado_revision"] = "Pendiente"
                clientes_locales.append(nuevo)
                print(f"✅ Sincronizado e incorporado: {nuevo['nombre']} ({nuevo['zona']})")
            else:
                print(f"⚠️ Omitido: {nuevo['nombre']} ya existe en la base de datos.")
        
        # Guardamos la base de datos actualizada
        guardar_datos(clientes_locales)
        
        # PASO CLAVE: Una vez absorbidos, borramos el archivo temporal de la web 
        # para no procesar los mismos clientes la próxima vez que abramos el programa.
        os.remove(ARCHIVO_WEB_ENTRADA)
        print("🗑️ Cola de entrada web limpia y procesada.")
        
    except Exception as e:
        print(f"❌ Error al procesar los datos de la web: {e}")
        
    return clientes_locales

# Mantener las funciones anteriores (Tablero, Rutas, Métricas) igual que antes...
def mostrar_tablero_completo(clientes):
    print("\n" + "="*70)
    print("                 NOVA - TABLERO GENERAL DE ABONADOS")
    print("="*70)
    if not clientes:
        print(" Sin clientes registrados actualmente. ¡Esperando sincronización web!")
    for i, c in enumerate(clientes, start=1):
        print(f"[{i}] 👤 {c['nombre'].ljust(25)} | 📍 {c['zona'].ljust(12)} | 🛠️ Equipos: {str(c['equipos'])} | 📦 {c['estado_revision']}")
    print("="*70)

def optimizar_ruta_sabado(clientes):
    zona_elegida = input("\n🔍 Ingresá la zona para el sábado: ").strip().lower()
    print("\n" + "~"*70)
    print(f"🚀 HOJA DE RUTA RECOMENDADA PARA EL SÁBADO: ZONA {zona_elegida.upper()}")
    print("~"*70)
    conteo = 0
    for c in clientes:
        if c["zona"] == zona_elegida and c["estado_revision"] == "Pendiente":
            print(f"📍 VISITAR A: {c['nombre']} ({c['tipo']}) - {c['equipos']} equipo(s).")
            conteo += c["equipos"]
    print(f"\n💡 Total de equipos en ruta: {conteo}" if conteo > 0 else "✨ Sin revisiones pendientes.")
    print("~"*70)

def mostrar_metricas_financieras(clientes):
    print("\n" + "📈"*25)
    total_equipos = sum(c["equipos"] for c in clientes)
    mrr_actual = total_equipos * VALOR_ABONO_POR_EQUIPO
    print(f"📊 Total de Equipos Protegidos: {total_equipos}")
    print(f"💰 MRR actual (Ingreso Mensual):  ${mrr_actual:,.2f} ARS")
    print("📈"*25)

# =====================================================================
# BUCLE PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    clientes_actuales = cargar_datos()
    
    while True:
        print("\n" + "░"*50)
        print("          SISTEMA OPERATIVO DE CONTROL - NOVA")
        print("░"*50)
        print("1. 📊 Ver Tablero General de Abonados")
        print("2. 🚀 Optimizar Hoja de Ruta (Sábados)")
        print("3. 🌐 Sincronizar Nuevos Clientes desde la Web") # Nuestra nueva opción
        print("4. 📈 Ver Métricas Financieras y MRR")
        print("5. ❌ Salir del Sistema")
        print("░"*50)
        
        opcion = input("👉 Seleccioná una opción [1-5]: ").strip()
        
        if opcion == "1":
            mostrar_tablero_completo(clientes_actuales)
        elif opcion == "2":
            optimizar_ruta_sabado(clientes_actuales)
        elif opcion == "3":
            clientes_actuales = sincronizar_datos_web(clientes_actuales)
        elif opcion == "4":
            mostrar_metricas_financieras(clientes_actuales)
        elif opcion == "5":
            print("\n👋 Saliendo del sistema de NOVA. ¡Buen viaje!")
            break
        else:
            print("❌ Opción inválida.")
        
        input("\nPresioná ENTER para volver...")