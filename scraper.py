import requests
from bs4 import BeautifulSoup
import json
import re

def extraer_modelos_apple():
    print("🤖 Buscando especificaciones completas en Apple...")
    url = "https://support.apple.com/es-es/HT201296"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    respuesta = requests.get(url, headers=headers)
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    base_de_datos = {}
    
    titulos = sopa.find_all(['h2', 'h3'])
    
    for titulo in titulos:
        nombre = titulo.get_text(strip=True).replace('\xa0', ' ')
        
        if "iPhone" in nombre and len(nombre) < 35 and "modelo" not in nombre.lower():
            modelos = []
            colores = []
            capacidades =[]
            año = 2024
            imagen = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png"
            
            nodo = titulo.find_next_sibling()
            
            while nodo and nodo.name not in ['h2', 'h3']:
                
                # 📸 1. DETECTIVE DE IMÁGENES
                if nodo.name == 'img':
                    img_tag = nodo
                else:
                    img_tag = nodo.find('img')
                    
                if img_tag and img_tag.get('src'):
                    src = img_tag.get('src')
                    if "image/svg" not in src and "icon" not in src:
                        if src.startswith('/'):
                            imagen = "https://support.apple.com" + src
                        elif src.startswith('http'):
                            imagen = src

                texto = nodo.get_text(" ", strip=True)
                
                # 🔍 2. DETECTIVE DE MODELOS (A-XXXX)
                encontrados_a = re.findall(r'A\d{4}', texto)
                if encontrados_a:
                    modelos.extend(encontrados_a)
                    
                # 📅 3. DETECTIVE DE AÑO
                if "presentación:" in texto.lower() or "lanzamiento:" in texto.lower():
                    match_año = re.search(r'(\d{4})', texto)
                    if match_año:
                        año = int(match_año.group(1))
                        
                # 💾 4. DETECTIVE DE ALMACENAMIENTO (Inteligente)
                # Si la línea habla de capacidad, extraemos todos los números lógicos
                if "capacidad" in texto.lower() or "gb" in texto.lower() or "tb" in texto.lower():
                    numeros = re.findall(r'\b\d{1,4}\b', texto)
                    for n in numeros:
                        num = int(n)
                        # Almacenamientos típicos en GB
                        if num in[4, 8, 16, 32, 64, 128, 256, 512]:
                            capacidades.append(f"{num} GB")
                        # Almacenamientos típicos en TB
                        elif num in [1, 2]:
                            capacidades.append(f"{num} TB")
                        
                # 🎨 5. DETECTIVE DE COLORES
                if "color" in texto.lower() or "colores:" in texto.lower():
                    partes = texto.split(":")
                    if len(partes) > 1:
                        texto_colores = partes[1].strip()
                        lista_c = re.split(r',|\by\b', texto_colores)
                        # Añadimos colores que tengan más de 2 letras
                        colores_limpios =[c.strip().capitalize() for c in lista_c if len(c.strip()) > 2]
                        colores.extend(colores_limpios)

                nodo = nodo.find_next_sibling()
            
            # --- GUARDADO FINAL DEL IPHONE ---
            if modelos:
                # Limpiamos duplicados 
                modelos = list(set(modelos))
                colores = list(set(colores))
                capacidades = list(set(capacidades))
                
                id_prod = nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
                
                base_de_datos[id_prod] = {
                    "categoria": "iPhone",
                    "nombre": nombre,
                    "año": año,
                    "imagen": imagen,
                    "colores": colores if colores else ["Consultar caja"],
                    "capacidades": capacidades if capacidades else ["Consultar caja"],
                    "modelos": {m: "Versión oficial extraída" for m in modelos}
                }
                
    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    extraer_modelos_apple()
