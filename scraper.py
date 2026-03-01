import requests
from bs4 import BeautifulSoup
import json
import re
import time

# --- CEREBRO INTERNO PARA ORDENADORES MAC ---
def deducir_numero_a_fisico(nombre):
    n = nombre.lower()
    modelos =[]
    if "imac" in n:
        if "20" in n: modelos.append("A1224")
        elif "21.5" in n or "21,5" in n:
            if any(y in n for y in["2009", "2010", "2011"]): modelos.append("A1311")
            elif any(y in n for y in["2012", "2013", "2014", "2015", "2017"]): modelos.append("A1418")
            elif "2019" in n: modelos.append("A2116")
        elif "24" in n:
            if any(y in n for y in["2007", "2008", "2009"]): modelos.append("A1225")
            elif "m1" in n or "2021" in n: modelos.extend(["A2438", "A2439"])
            elif "m3" in n or "2023" in n: modelos.append("A2902")
        elif "27" in n:
            if any(y in n for y in["2009", "2010", "2011"]): modelos.append("A1312")
            elif any(y in n for y in["2012", "2013", "2014", "2015", "2017"]): modelos.append("A1419")
            elif any(y in n for y in["2019", "2020"]): modelos.append("A2115")
    elif "macbook air" in n:
        if "11" in n:
            if "2010" in n or "2011" in n: modelos.append("A1370")
            else: modelos.append("A1465")
        elif "13" in n:
            if "2010" in n or "2011" in n: modelos.append("A1369")
            elif any(y in n for y in["2012", "2013", "2014", "2015", "2017"]): modelos.append("A1466")
            elif "2018" in n or "2019" in n: modelos.append("A1932")
            elif "2020" in n and "m1" not in n: modelos.append("A2179")
            elif "m1" in n: modelos.append("A2337")
            elif "m2" in n: modelos.append("A2681")
            elif "m3" in n: modelos.append("A3113")
        elif "15" in n:
            if "m2" in n: modelos.append("A2941")
            elif "m3" in n: modelos.append("A3114")
    elif "macbook pro" in n:
        if "13" in n:
            if any(y in n for y in["2009", "2010", "2011", "2012"]) and "retina" not in n: modelos.append("A1278")
            elif "retina" in n and ("2012" in n or "2013" in n): modelos.append("A1425")
            elif "retina" in n and any(y in n for y in["2013", "2014", "2015"]): modelos.append("A1502")
            elif "2016" in n or "2017" in n: modelos.extend(["A1706", "A1708"])
            elif "2018" in n or "2019" in n: modelos.extend(["A1989", "A2159"])
            elif "2020" in n and "m1" not in n: modelos.extend(["A2289", "A2251"])
            elif "m1" in n or "m2" in n: modelos.append("A2338")
        elif "14" in n:
            if "m1" in n: modelos.append("A2442")
            elif "m2" in n: modelos.append("A2779")
            elif "m3" in n: modelos.extend(["A2918", "A2992"])
        elif "15" in n:
            if any(y in n for y in["2006", "2007", "2008"]) and "unibody" not in n: modelos.extend(["A1150", "A1211", "A1226", "A1260"])
            elif any(y in n for y in["2008", "2009", "2010", "2011", "2012"]) and "retina" not in n: modelos.append("A1286")
            elif "retina" in n or any(y in n for y in["2012", "2013", "2014", "2015"]): modelos.append("A1398")
            elif "2016" in n or "2017" in n: modelos.append("A1707")
            elif "2018" in n or "2019" in n: modelos.append("A1990")
        elif "16" in n:
            if "2019" in n: modelos.append("A2141")
            elif "m1" in n: modelos.append("A2485")
            elif "m2" in n: modelos.append("A2780")
            elif "m3" in n: modelos.append("A2991")
        elif "17" in n:
            modelos.extend(["A1151", "A1212", "A1229", "A1261", "A1297"])
    elif "macbook" in n and "pro" not in n and "air" not in n:
        if "12" in n: modelos.append("A1534")
        elif "2008" in n and "aluminio" in n: modelos.append("A1278")
        elif any(y in n for y in ["2009", "2010"]) and ("blanco" in n or "policarbonato" in n): modelos.append("A1342")
        else: modelos.append("A1181")
    elif "mac mini" in n:
        if any(y in n for y in["2006", "2007"]): modelos.append("A1176")
        elif "2009" in n: modelos.append("A1283")
        elif any(y in n for y in["2010", "2011", "2012", "2014"]): modelos.append("A1347")
        elif "2018" in n: modelos.append("A1993")
        elif "m1" in n: modelos.append("A2348")
        elif "m2" in n: modelos.extend(["A2686", "A2816"])
    elif "mac pro" in n:
        if any(y in n for y in["2006", "2007", "2008"]): modelos.append("A1186")
        elif any(y in n for y in["2009", "2010", "2012"]): modelos.append("A1289")
        elif "2013" in n: modelos.append("A1481")
        elif "2019" in n: modelos.append("A1991")
        elif "2023" in n: modelos.append("A2786")
    elif "mac studio" in n:
        if "m1" in n or "2022" in n: modelos.append("A2615")
        elif "m2" in n or "2023" in n: modelos.append("A2901")
    return modelos
# ---------------------------------------------------------------------------------

def extraer_ecosistema_apple():
    print("🤖 Iniciando escaneo masivo (Con lectura de Negritas e Inyección Clásica)...")
    paginas_soporte =[
        {"url": "https://support.apple.com/es-es/HT201296", "categoria": "iPhone", "filtro": "iPhone"},
        {"url": "https://support.apple.com/es-es/HT201471", "categoria": "iPad", "filtro": "iPad"},
        {"url": "https://support.apple.com/es-es/HT201300", "categoria": "Mac", "filtro": "MacBook Pro"},
        {"url": "https://support.apple.com/es-es/HT201862", "categoria": "Mac", "filtro": "MacBook Air"},
        {"url": "https://support.apple.com/es-es/HT201608", "categoria": "Mac", "filtro": "MacBook"},
        {"url": "https://support.apple.com/es-es/HT201634", "categoria": "Mac", "filtro": "iMac"},
        {"url": "https://support.apple.com/es-es/HT201894", "categoria": "Mac", "filtro": "Mac mini"},
        {"url": "https://support.apple.com/es-es/HT202888", "categoria": "Mac", "filtro": "Mac Pro"},
        {"url": "https://support.apple.com/es-es/HT213073", "categoria": "Mac", "filtro": "Mac Studio"},
        {"url": "https://support.apple.com/es-es/HT204507", "categoria": "Watch", "filtro": "Apple Watch"}
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    base_de_datos = {}
    
    for pagina in paginas_soporte:
        print(f"\n📡 Escaneando: {pagina['url']}...")
        respuesta = requests.get(pagina['url'], headers=headers)
        
        if respuesta.status_code != 200:
            print(f"⚠️ Error {respuesta.status_code}. Saltando página...")
            time.sleep(3)
            continue
            
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        # 🔥 TRUCO 1: Buscar títulos y Textos en Negrita (donde Apple esconde a los abuelos)
        titulos_brutos = sopa.find_all(['h2', 'h3', 'strong'])
        
        for titulo in titulos_brutos:
            # Evitar leer el doble si un texto negrita está dentro de un título
            if titulo.name == 'strong' and titulo.parent and getattr(titulo.parent, 'name', None) in['h2', 'h3']:
                continue
                
            nombre = titulo.get_text(strip=True).replace('\xa0', ' ')
            
            if pagina['filtro'].lower() in nombre.lower() and len(nombre) < 60 and "identificar" not in nombre.lower():
                diccionario_modelos = {}
                colores = []
                capacidades =[]
                año = 2024
                imagen = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png"
                url_specs = pagina['url'] 
                
                if pagina['categoria'] == 'Mac':
                    codigos_fisicos = deducir_numero_a_fisico(nombre)
                    for cod in codigos_fisicos:
                        diccionario_modelos[cod] = "Número de chasis (Físico)"

                if titulo.name == 'strong':
                    nodo = titulo.parent.find_next_sibling()
                else:
                    nodo = titulo.find_next_sibling()
                
                while nodo and getattr(nodo, 'name', None) not in ['h2', 'h3']:
                    # Cortar si chocamos con otro ordenador antiguo en negrita
                    if getattr(nodo, 'name', None) == 'p' and nodo.find('strong'):
                        strong_txt = nodo.find('strong').get_text(strip=True)
                        if pagina['filtro'].lower() in strong_txt.lower() and len(strong_txt) < 60:
                            break
                            
                    if getattr(nodo, 'name', None):
                        enlaces = nodo.find_all('a', href=True)
                        for a in enlaces:
                            if "especificaci" in a.text.lower() or "sp" in a['href'].lower() or "specs" in a.text.lower():
                                href = a['href']
                                if href.startswith('http'): url_specs = href
                                else: url_specs = "https://support.apple.com" + href
                                
                    if getattr(nodo, 'name', None) == 'img': img_tag = nodo
                    else: img_tag = nodo.find('img') if getattr(nodo, 'name', None) else None
                        
                    if img_tag and img_tag.get('src'):
                        src = img_tag.get('src')
                        if "image/svg" not in src and "icon" not in src:
                            if src.startswith('/'): imagen = "https://support.apple.com" + src
                            elif src.startswith('http'): imagen = src

                    texto = nodo.get_text(" ", strip=True)
                    
                    matches_a = re.finditer(r'(A\d{4})(?:\s*\(([^)]+)\))?', texto)
                    for match in matches_a:
                        modelo = match.group(1)
                        region = match.group(2)
                        if region: diccionario_modelos[modelo] = region.replace("otros países y regiones", "Modelo Internacional").strip().capitalize()
                        else: 
                            if modelo not in diccionario_modelos: diccionario_modelos[modelo] = "Región global o no especificada"
                    
                    if pagina['categoria'] == 'Mac':
                        match_id = re.search(r'identificador(?:es)? d[e|el] modelo:\s*([^.]+)', texto, re.IGNORECASE)
                        if match_id:
                            for i in re.split(r',|\by\b', match_id.group(1)):
                                if len(i.strip()) > 4: diccionario_modelos[i.strip()] = "Identificador interno (Sistema)"
                            
                        match_pieza = re.search(r'pieza:\s*([^.]+)', texto, re.IGNORECASE)
                        if match_pieza:
                            for p in re.split(r',|\by\b|\s+', match_pieza.group(1)):
                                if len(p.strip()) > 4 and any(c.isdigit() for c in p.strip()): diccionario_modelos[p.strip()] = "Número de pieza comercial"

                    if "presentación:" in texto.lower() or "lanzamiento:" in texto.lower() or "año:" in texto.lower():
                        match_año = re.search(r'(\d{4})', texto)
                        if match_año: año = int(match_año.group(1))
                            
                    if "capacidad" in texto.lower() or "gb" in texto.lower() or "tb" in texto.lower() or "almacenamiento" in texto.lower():
                        for n in re.findall(r'\b\d{1,4}\b', texto):
                            num = int(n)
                            if num in[4, 8, 16, 32, 64, 128, 256, 512]: capacidades.append(f"{num} GB")
                            elif num in[1, 2, 4, 8]: capacidades.append(f"{num} TB")
                            
                    if "color" in texto.lower() or "acabado" in texto.lower():
                        partes = re.split(r'colores:|color:|acabados:|acabado:', texto, flags=re.IGNORECASE)
                        if len(partes) > 1:
                            colores_limpios =[c.strip().capitalize() for c in re.split(r',|\by\b', partes[1].strip()) if len(c.strip()) > 2]
                            colores.extend(colores_limpios)

                    nodo = nodo.find_next_sibling()
                
                if diccionario_modelos:
                    id_prod = nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "").replace('"', '').replace("-", "_")
                    base_de_datos[id_prod] = {
                        "categoria": pagina['categoria'],
                        "nombre": nombre,
                        "año": año,
                        "imagen": imagen,
                        "url_specs": url_specs,
                        "colores": list(set(colores)) if colores else["Consultar Especificaciones"],
                        "capacidades": list(set(capacidades)) if capacidades else["Consultar Especificaciones"],
                        "modelos": diccionario_modelos
                    }
                    
        time.sleep(3)

    # 🔥 TRUCO 2: LA CAJA FUERTE (Inyección de los modelos que Apple borró del todo)
    clasicos = {
        "imac_vintage_a1225": {
            "categoria": "Mac", "nombre": "iMac (24 pulgadas, Clásico)", "año": 2007,
            "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png",
            "url_specs": "https://support.apple.com/es-es/112573",
            "colores": ["Plata (Aluminio)"], "capacidades":["250 GB", "320 GB", "500 GB"],
            "modelos": {"A1225": "Número de chasis (Físico)", "MA878": "Número de pieza comercial"}
        },
        "imac_vintage_a1311": {
            "categoria": "Mac", "nombre": "iMac (21.5 pulgadas, Clásico)", "año": 2009,
            "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png",
            "url_specs": "https://support.apple.com/es-es/112469",
            "colores": ["Plata (Aluminio)"], "capacidades":["500 GB", "1 TB"],
            "modelos": {"A1311": "Número de chasis (Físico)", "MB950": "Número de pieza comercial"}
        },
        "macbook_vintage_a1181": {
            "categoria": "Mac", "nombre": "MacBook (13 pulgadas, Policarbonato Clásico)", "año": 2006,
            "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png",
            "url_specs": "https://support.apple.com/es-es/112602",
            "colores": ["Blanco", "Negro"], "capacidades":["60 GB", "80 GB", "120 GB"],
            "modelos": {"A1181": "Número de chasis (Físico)", "MA254": "Número de pieza comercial"}
        }
    }
    
    # Comprobamos si el modelo A1225 o A1311 falta, y si es así, ¡lo metemos a la fuerza!
    for key, data in clasicos.items():
        if not any(key in bd['modelos'] for bd in base_de_datos.values()):
            base_de_datos[key] = data

    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)
    print("\n🚀 ¡Base de datos completada al 100%!")

if __name__ == "__main__":
    extraer_ecosistema_apple()
