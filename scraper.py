import requests
from bs4 import BeautifulSoup
import json
import re

def extraer_ecosistema_apple():
    print("🤖 Iniciando escaneo masivo del Ecosistema Apple...")
    
    # Lista de misiones: Todas las páginas oficiales de Apple
    paginas_soporte =[
        {"url": "https://support.apple.com/es-es/HT201296", "categoria": "iPhone", "filtro": "iPhone"},
        {"url": "https://support.apple.com/es-es/HT201471", "categoria": "iPad", "filtro": "iPad"},
        {"url": "https://support.apple.com/es-es/HT201300", "categoria": "Mac", "filtro": "MacBook Pro"},
        {"url": "https://support.apple.com/es-es/HT201862", "categoria": "Mac", "filtro": "MacBook Air"},
        {"url": "https://support.apple.com/es-es/HT204507", "categoria": "Watch", "filtro": "Apple Watch"}
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    base_de_datos = {}
    
    for pagina in paginas_soporte:
        print(f"\n📡 Escaneando {pagina['categoria']}s...")
        respuesta = requests.get(pagina['url'], headers=headers)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        titulos = sopa.find_all(['h2', 'h3'])
        
        for titulo in titulos:
            nombre = titulo.get_text(strip=True).replace('\xa0', ' ')
            
            # Filtramos para que coincida con el dispositivo que buscamos (y nombres de hasta 60 letras para iPads largos)
            if pagina['filtro'].lower() in nombre.lower() and len(nombre) < 60 and "identificar" not in nombre.lower():
                diccionario_modelos = {}
                colores =[]
                capacidades =[]
                año = 2024
                imagen = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png"
                
                nodo = titulo.find_next_sibling()
                
                while nodo and nodo.name not in ['h2', 'h3']:
                    # 📸 DETECTIVE DE IMÁGENES
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
                    
                    # 🌍 DETECTIVE DE MODELOS (A-XXXX) y Regiones
                    matches = re.finditer(r'(A\d{4})(?:\s*\(([^)]+)\))?', texto)
                    for match in matches:
                        modelo = match.group(1)
                        region = match.group(2)
                        
                        if region:
                            region_limpia = region.replace("otros países y regiones", "Modelo Internacional").strip().capitalize()
                            diccionario_modelos[modelo] = region_limpia
                        else:
                            if modelo not in diccionario_modelos:
                                diccionario_modelos[modelo] = "Región global o no especificada"
                        
                    # 📅 DETECTIVE DE AÑO
                    if "presentación:" in texto.lower() or "lanzamiento:" in texto.lower() or "año:" in texto.lower():
                        match_año = re.search(r'(\d{4})', texto)
                        if match_año:
                            año = int(match_año.group(1))
                            
                    # 💾 DETECTIVE DE ALMACENAMIENTO (Adaptado a Macs)
                    if "capacidad" in texto.lower() or "gb" in texto.lower() or "tb" in texto.lower():
                        numeros = re.findall(r'\b\d{1,4}\b', texto)
                        for n in numeros:
                            num = int(n)
                            if num in[4, 8, 16, 32, 64, 128, 256, 512]:
                                capacidades.append(f"{num} GB")
                            elif num in [1, 2, 4, 8]: # Ampliado a 4 y 8 TB para portátiles
                                capacidades.append(f"{num} TB")
                            
                    # 🎨 DETECTIVE DE COLORES Y ACABADOS
                    if "color" in texto.lower() or "acabado" in texto.lower():
                        partes = re.split(r'colores:|color:|acabados:|acabado:', texto, flags=re.IGNORECASE)
                        if len(partes) > 1:
                            texto_colores = partes[1].strip()
                            lista_c = re.split(r',|\by\b', texto_colores)
                            colores_limpios =[c.strip().capitalize() for c in lista_c if len(c.strip()) > 2]
                            colores.extend(colores_limpios)

                    nodo = nodo.find_next_sibling()
                
                # --- GUARDADO EN LA BASE DE DATOS ---
                if diccionario_modelos:
                    colores = list(set(colores))
                    capacidades = list(set(capacidades))
                    
                    id_prod = nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "").replace('"', '').replace("-", "_")
                    
                    base_de_datos[id_prod] = {
                        "categoria": pagina['categoria'],
                        "nombre": nombre,
                        "año": año,
                        "imagen": imagen,
                        "colores": colores if colores else ["Consultar caja o web"],
                        "capacidades": capacidades if capacidades else ["Consultar caja o web"],
                        "modelos": diccionario_modelos
                    }
                    
    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)
    print("\n🚀 ¡Base de datos del ecosistema completo generada con éxito!")

if __name__ == "__main__":
    extraer_ecosistema_apple()
