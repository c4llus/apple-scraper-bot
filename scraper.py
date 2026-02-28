import requests
from bs4 import BeautifulSoup
import json
import re

def extraer_modelos_apple():
    print("🤖 Conectando con Apple Support...")
    url = "https://support.apple.com/es-es/HT201296"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    respuesta = requests.get(url, headers=headers)
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    
    # 🕵️‍♂️ TRUCO MAESTRO: Ignoramos el código HTML (div, h2, span) 
    # y extraemos solo el texto puro, como si lo leyera una persona.
    texto_puro = sopa.get_text(separator='\n')
    lineas = [linea.strip() for linea in texto_puro.split('\n') if linea.strip()]
    
    base_de_datos = {}
    nombre_actual = None
    modelos_actuales =[]
    
    for linea in lineas:
        # 1. ¿Es esta línea el nombre de un iPhone?
        # Condición: Contiene "iPhone", es cortita y no es una frase descriptiva
        if "iPhone" in linea and len(linea) < 35 and "modelo" not in linea.lower():
            
            # Guardamos el iPhone anterior si tenía modelos
            if nombre_actual and modelos_actuales:
                guardar_iphone(base_de_datos, nombre_actual, modelos_actuales)
                
            # Empezamos a apuntar el nuevo iPhone
            nombre_actual = linea
            modelos_actuales =[]
            
        elif nombre_actual:
            # 2. Buscamos cualquier código tipo "A2848" en las líneas de abajo
            encontrados = re.findall(r'A\d{4}', linea)
            if encontrados:
                modelos_actuales.extend(encontrados)

    # Guardamos el último de la lista al terminar de leer
    if nombre_actual and modelos_actuales:
        guardar_iphone(base_de_datos, nombre_actual, modelos_actuales)

    # 🚨 Si por algún casual falla, chivarnos qué página nos cargó Apple
    if not base_de_datos:
        titulo_web = sopa.title.string if sopa.title else "Desconocido"
        base_de_datos["error_bot"] = {
             "categoria": "Sistema",
             "nombre": "Error de Lectura",
             "año": 2024,
             "imagen": "",
             "colores": [],
             "capacidades":[],
             "modelos": {"A0000": f"Apple no mostró los modelos. Título de la web: {titulo_web}"}
        }

    with open("datos_apple.json", "w", encoding="utf-8") as archivo:
        json.dump(base_de_datos, archivo, indent=4, ensure_ascii=False)

def guardar_iphone(base_de_datos, nombre, modelos):
    # Quitamos modelos duplicados
    modelos_unicos = list(set(modelos))
    
    # Creamos un ID seguro (ej. "iphone_15_pro")
    id_prod = nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
    
    base_de_datos[id_prod] = {
        "categoria": "iPhone",
        "nombre": nombre,
        "año": "Automático",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png",
        "colores": ["Extraído de Apple.com"],
        "capacidades": ["Varias"],
        "modelos": {m: "Versión oficial extraída de la web" for m in modelos_unicos}
    }

if __name__ == "__main__":
    extraer_modelos_apple()
