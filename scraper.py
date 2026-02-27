import requests
from bs4 import BeautifulSoup
import json
import re

def extraer_modelos_apple():
    print("🤖 Conectando con Apple Support...")
    # URL oficial de Apple donde listan los modelos
    url = "https://support.apple.com/es-es/112025"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    respuesta = requests.get(url, headers=headers)
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    base_de_datos = {}
    
    # Apple suele poner los nombres de los iPhone en etiquetas <h2>
    titulos = sopa.find_all('h2')
    
    for titulo in titulos:
        nombre_iphone = titulo.get_text(strip=True)
        
        # Filtramos para asegurarnos de que es un iPhone
        if "iPhone" in nombre_iphone:
            # Buscamos todo el texto que hay debajo de ese título
            texto_contenido =[]
            nodo_actual = titulo.find_next_sibling()
            
            # Extraemos texto hasta llegar al siguiente iPhone
            while nodo_actual and nodo_actual.name not in ['h2']:
                texto_contenido.append(nodo_actual.get_text(" ", strip=True))
                nodo_actual = nodo_actual.find_next_sibling()
                
            texto_completo = " ".join(texto_contenido)
            
            # 🔍 MAGIA: Buscamos cualquier palabra que empiece por 'A' seguida de 4 números (Ej: A2848)
            modelos_a = re.findall(r'A\d{4}', texto_completo)
            modelos_unicos = list(set(modelos_a))
            
            # Buscamos el año
            año_match = re.search(r'año de presentación:\s*(\d{4})', texto_completo, re.IGNORECASE)
            año = int(año_match.group(1)) if año_match else 2024
            
            # Si hemos encontrado modelos 'A', lo guardamos en la base de datos
            if modelos_unicos:
                id_producto = nombre_iphone.lower().replace(" ", "_").replace('"', '')
                diccionario_modelos = {}
                for m in modelos_unicos:
                    diccionario_modelos[m] = "Versión extraída de Apple.com"
                    
                base_de_datos[id_producto] = {
                    "categoria": "iPhone",
                    "nombre": nombre_iphone,
                    "año": año,
                    "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png",
                    "colores": ["Extraído automáticamente"],
                    "capacidades": ["Varias"],
                    "modelos": diccionario_modelos
                }
                print(f"✅ Encontrado: {nombre_iphone} con {len(modelos_unicos)} variantes.")

    # Guardamos el resultado en un archivo JSON
    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)
    print("🚀 Archivo datos_apple.json creado con éxito!")

if __name__ == "__main__":
    extraer_modelos_apple()
