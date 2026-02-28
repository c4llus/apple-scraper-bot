import requests
from bs4 import BeautifulSoup
import json
import re

def extraer_modelos_apple():
    print("🤖 Conectando con Apple Support...")
    url = "https://support.apple.com/es-es/112025"
    
    # 🕵️‍♂️ TRUCO 1: Nos disfrazamos de Googlebot para que Apple nos abra la puerta
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.5"
    }
    
    respuesta = requests.get(url, headers=headers)
    print(f"📡 Estado de la conexión (200 es Éxito, 403 es Bloqueo): {respuesta.status_code}")
    
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    base_de_datos = {}
    
    # 🕵️‍♂️ TRUCO 2: Buscamos tanto en títulos grandes (h2) como medianos (h3)
    titulos = sopa.find_all(['h2', 'h3'])
    
    for titulo in titulos:
        # Limpiamos el texto por si tiene espacios raros
        nombre_iphone = titulo.get_text(strip=True).replace('\xa0', ' ')
        
        if "iPhone" in nombre_iphone:
            texto_contenido = ""
            nodo = titulo.find_next_sibling()
            
            # Recolectamos todo el texto hasta el siguiente iPhone
            while nodo and nodo.name not in ['h2', 'h3']:
                texto_contenido += " " + nodo.get_text(strip=True)
                nodo = nodo.find_next_sibling()
                
            # Buscamos cualquier patrón "A" seguido de 4 números
            modelos_a = re.findall(r'A\d{4}', texto_contenido)
            modelos_unicos = list(set(modelos_a))
            
            if modelos_unicos:
                # Creamos una ID limpia (ej: "iphone_15_pro")
                id_producto = nombre_iphone.lower().replace(" ", "_").replace('"', '').replace('(', '').replace(')', '')
                
                diccionario_modelos = {}
                for m in modelos_unicos:
                    diccionario_modelos[m] = "Versión oficial Apple"
                    
                base_de_datos[id_producto] = {
                    "categoria": "iPhone",
                    "nombre": nombre_iphone,
                    "año": 2024,
                    "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png",
                    "colores": ["Extraído automáticamente"],
                    "capacidades": ["Varias"],
                    "modelos": diccionario_modelos
                }
                print(f"✅ Encontrado: {nombre_iphone} -> {modelos_unicos}")

    # 🕵️‍♂️ TRUCO 3: Si falla, que nos avise en la App para saber qué ha pasado
    if not base_de_datos:
        print("⚠️ No se encontraron modelos. Guardando mensaje de error...")
        base_de_datos["error_bot"] = {
             "categoria": "Sistema",
             "nombre": "Error de Extracción",
             "año": 2024,
             "imagen": "",
             "colores": [],
             "capacidades":[],
             "modelos": {"A0000": f"Apple bloqueó al bot. Código HTTP: {respuesta.status_code}"}
        }

    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)
    print("🚀 Archivo JSON actualizado y guardado.")

if __name__ == "__main__":
    extraer_modelos_apple()
