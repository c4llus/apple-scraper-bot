import requests
from bs4 import BeautifulSoup
import json
import re

def extraer_ecosistema_apple():
    print("🤖 Iniciando escaneo masivo del Ecosistema Apple...")
    
    # Hemos añadido los iMac y los Mac mini al escaneo
    paginas_soporte =[
        {"url": "https://support.apple.com/es-es/HT201296", "categoria": "iPhone", "filtro": "iPhone"},
        {"url": "https://support.apple.com/es-es/HT201471", "categoria": "iPad", "filtro": "iPad"},
        {"url": "https://support.apple.com/es-es/HT201300", "categoria": "Mac", "filtro": "MacBook Pro"},
        {"url": "https://support.apple.com/es-es/HT201862", "categoria": "Mac", "filtro": "MacBook Air"},
        {"url": "https://support.apple.com/es-es/HT201634", "categoria": "Mac", "filtro": "iMac"},
        {"url": "https://support.apple.com/es-es/HT201894", "categoria": "Mac", "filtro": "Mac mini"},
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
                    
                    # 🌍 DETECTIVE DE MODELOS (A-XXXX para iPhone/iPad/Watch)
                    matches_a = re.finditer(r'(A\d{4})(?:\s*\(([^)]+)\))?', texto)
                    for match in matches_a:
                        modelo = match.group(1)
                        region = match.group(2)
                        if region:
                            region_limpia = region.replace("otros países y regiones", "Modelo Internacional").strip().capitalize()
                            diccionario_modelos[modelo] = region_limpia
                        else:
                            if modelo not in diccionario_modelos:
                                diccionario_modelos[modelo] = "Región global o no especificada"
                    
                    # 💻 DETECTIVE DE MACS (Identificadores y Part Numbers)
                    if pagina['categoria'] == 'Mac':
                        
                        # 1. Busca el "Identificador de modelo" (Ej: MacBookPro16,1)
                        match_id = re.search(r'identificador(?:es)? d[e|el] modelo:\s*([^.]+)', texto, re.IGNORECASE)
                        if match_id:
                            ids_raw = match_id.group(1)
                            # A veces hay varios separados por comas
                            ids = re.split(r',|\by\b', ids_raw)
                            for i in ids:
                                i_clean = i.strip()
                                if len(i_clean) > 4:
                                    diccionario_modelos[i_clean] = "Identificador interno (Sistema Mac)"
                            
                        # 2. Busca los "Números de pieza" de las tiendas (Ej: MVVK2xx/A)
                        match_pieza = re.search(r'pieza:\s*([^.]+)', texto, re.IGNORECASE)
                        if match_pieza:
                            piezas_raw = match_pieza.group(1)
                            piezas = re.split(r',|\by\b|\s+', piezas_raw)
                            for p in piezas:
                                p_clean = p.strip()
                                # Aseguramos que sea un código con letras y números
                                if len(p_clean) > 4 and any(c.isdigit() for c in p_clean):
                                    diccionario_modelos[p_clean] = "Número de pieza comercial (Caja)"

                    # 📅 DETECTIVE DE AÑO
                    if "presentación:" in texto.lower() or "lanzamiento:" in texto.lower() or "año:" in texto.lower():
                        match_año = re.search(r'(\d{4})', texto)
                        if match_año:
                            año = int(match_año.group(1))
                            
                    # 💾 DETECTIVE DE ALMACENAMIENTO
                    if "capacidad" in texto.lower() or "gb" in texto.lower() or "tb" in texto.lower() or "almacenamiento" in texto.lower():
                        numeros = re.findall(r'\b\d{1,4}\b', texto)
                        for n in numeros:
                            num = int(n)
                            if num in[4, 8, 16, 32, 64, 128, 256, 512]:
                                capacidades.append(f"{num} GB")
                            elif num in [1, 2, 4, 8]:
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
                        "colores": colores if colores else ["Consultar especificaciones"],
                        "capacidades": capacidades if capacidades else ["Consultar especificaciones"],
                        "modelos": diccionario_modelos
                    }
                    
    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)
    print("\n🚀 ¡Base de datos del ecosistema completo generada con éxito!")

if __name__ == "__main__":
    extraer_ecosistema_apple()
