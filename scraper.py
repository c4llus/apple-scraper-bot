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
    
    # Encontramos todos los bloques de la página web
    titulos = sopa.find_all(['h2', 'h3'])
    
    for titulo in titulos:
        nombre = titulo.get_text(strip=True).replace('\xa0', ' ')
        
        # Comprobamos que sea un título de un iPhone real
        if "iPhone" in nombre and len(nombre) < 35 and "modelo" not in nombre.lower():
            
            # Preparamos las variables en blanco para este móvil
            modelos =[]
            colores = []
            capacidades =[]
            año = 2024
            # Imagen por defecto por si Apple no ha puesto foto en ese modelo
            imagen = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png"
            
            # Exploramos todos los párrafos que hay debajo de este iPhone
            nodo = titulo.find_next_sibling()
            
            while nodo and nodo.name not in ['h2', 'h3']:
                
                # 📸 1. DETECTIVE DE IMÁGENES
                if nodo.name == 'img':
                    img_tag = nodo
                else:
                    img_tag = nodo.find('img')
                    
                if img_tag and img_tag.get('src'):
                    src = img_tag.get('src')
                    # Filtramos para no coger iconos minúsculos de la web
                    if "image/svg" not in src and "icon" not in src:
                        if src.startswith('/'):
                            imagen = "https://support.apple.com" + src
                        elif src.startswith('http'):
                            imagen = src

                # Extraemos el texto de este párrafo concreto
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
                        
                # 💾 4. DETECTIVE DE ALMACENAMIENTO (GB / TB)
                if "capacidad" in texto.lower() or "gb" in texto.lower() or "tb" in texto.lower():
                    caps = re.findall(r'\b\d{2,4}\s?[GgTt][Bb]\b', texto, re.IGNORECASE)
                    if caps:
                        # Lo convertimos a mayúsculas para que quede bonito: "128 GB"
                        for c in caps:
                            capacidades.append(c.upper())
                        
                # 🎨 5. DETECTIVE DE COLORES
                if "color" in texto.lower() or "colores:" in texto.lower():
                    partes = texto.split(":")
                    if len(partes) > 1:
                        texto_colores = partes[1].strip()
                        # Cortamos la frase por las comas (,) o la letra 'y'
                        lista_c = re.split(r',|\by\b', texto_colores)
                        # Limpiamos los espacios y ponemos la primera letra en mayúscula
                        colores =[c.strip().capitalize() for c in lista_c if len(c.strip()) > 2]

                # Pasamos al siguiente párrafo
                nodo = nodo.find_next_sibling()
            
            # --- GUARDADO FINAL DEL IPHONE ---
            if modelos:
                # Limpiamos duplicados (a veces Apple repite el mismo modelo 2 veces)
                modelos = list(set(modelos))
                capacidades = list(set(capacidades))
                
                id_prod = nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
                
                base_de_datos[id_prod] = {
                    "categoria": "iPhone",
                    "nombre": nombre,
                    "año": año,
                    "imagen": imagen,
                    # Si no encuentra colores o capacidades, pone un texto de aviso
                    "colores": colores if colores else ["Consultar en Apple"],
                    "capacidades": capacidades if capacidades else ["Consultar caja"],
                    "modelos": {m: "Extraído de la web oficial" for m in modelos}
                }
                
    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    extraer_modelos_apple()
