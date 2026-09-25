from pdf2image import convert_from_bytes
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def procesar_pdf_ocr(pdf_bytes):
    ruta_poppler = r"C:\poppler\poppler-24.02.0\Library\bin" 
    
    images = convert_from_bytes(pdf_bytes, poppler_path=ruta_poppler)
    
    texto_completo = ""
    for image in images:
        texto_completo += pytesseract.image_to_string(image, lang='spa')
    
    # NUEVO: Imprimir el texto crudo en la terminal de Uvicorn para depuración
    #print("\n--- TEXTO CRUDO EXTRAÍDO POR OCR ---")
    #print(texto_completo)
    #print("------------------------------------\n")
    
    return extraer_datos_resolucion(texto_completo)

def extraer_datos_resolucion(texto: str):
    texto_limpio = re.sub(r'\s+', ' ', texto)
    print("\n--- TEXTO LIMPIO PARA ANÁLISIS ---")
    print(texto_limpio) 
    print("------------------------------------\n")
    titulo_match = re.search(r'titulado\s*:?\s*(?:["“”\'])?(.*?)(?:["“”\'])?,?\s*elaborado', texto_limpio, re.IGNORECASE)
    titulo_perfil = titulo_match.group(1).strip() if titulo_match else None
    estudiante_match = re.search(r'elaborado (?:y presentado por |por )?(?:el|la)?\s*(?:Lic\.|Ing\.|Univ\.|M\.Sc\.)?\s*([A-ZÁÉÍÓÚa-záéíóú\s]+?)(?:,|participante)', texto_limpio, re.IGNORECASE)
    grado_match = re.search(r'presentado por (?:el|la)?\s*(Lic\.|Ing\.|Univ\.|M\.Sc\.)', texto_limpio, re.IGNORECASE)
    grado_match2 = re.search(r'elaborado por (?:el|la)?\s*(Lic\.|Ing\.|Univ\.|M\.Sc\.)', texto_limpio, re.IGNORECASE)
    grado=None
    if grado_match:
        grado=grado_match.group(1).strip()
    elif grado_match2:
        grado=grado_match2.group(1).strip()

    maestria_match = re.search(r'de la Maestría en\s*["“”\'](.*?)["“”\']?,?\s*,', texto_limpio, re.IGNORECASE)
    maestria_match2 = re.search(r'participante de la\s*["“”\'](.*?)["“”\']?,?\s*,', texto_limpio, re.IGNORECASE)
    maestria=None
    if maestria_match:
        maestria=maestria_match.group(1).strip()
    elif maestria_match2:
        maestria=maestria_match2.group(1).strip()
    estudiante_nombre = None
    estudiante_apPaterno = None
    estudiante_apMaterno = None
    #tutor
    tutor_match = re.search(r'bajo la tutoría\s*(?:del?\s*)?\s*(?:Lic\.|Ing\.|Univ\.|M\.Sc\.|Ph\.D\.|Dr\.)?\s*([A-ZÁÉÍÓÚa-záéíóú\s]+?)y', texto_limpio, re.IGNORECASE)
    gradoT_match = re.search(r'bajo la tutoría\s*(?:del?\s*)?\s*(Lic\.|Ing\.|Univ\.|M\.Sc\.|Ph\.D\.|Dr\.)', texto_limpio, re.IGNORECASE)
    gradoT=gradoT_match.group(1).strip() if gradoT_match else None
    tutorNom=None
    tutorP=None
    tutorM=None

    resolucion_match = re.search(r'RESOLUCI[OÓ]N\s+N[*°ºoO]?\s*([\d/]+)', texto_limpio, re.IGNORECASE)
    resolucion = resolucion_match.group(1).strip() if resolucion_match else None

    patron_tribunal = r'tutoría\s+(?:M\.Sc\.|Ph\.D\.|Ing\.)?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?)\s+y\s+tribunal\s+revisor\s+conformado\s+por\s+los\s+(?:M\.Sc\.|Ph\.D\.|Ing\.)?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?),\s+y\s+el\s+(?:M\.Sc\.|Ph\.D\.|Ing\.)?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?)\.'
    match_tribunal = re.search(patron_tribunal, texto_limpio, re.IGNORECASE)
    presidente = None
    primer_tribunal = None
    segundo_tribunal = None
    if match_tribunal:
        presidente = match_tribunal.group(1).strip()
        primer_tribunal = match_tribunal.group(2).strip()
        segundo_tribunal = match_tribunal.group(3).strip()

    if tutor_match:
        print ("se obtuvo datos del tutor")
        nombreTutorCompleto= tutor_match.group(1).strip().split()
        if len(nombreTutorCompleto) >= 3:
            tutorM = nombreTutorCompleto[-1].upper()
            tutorP = nombreTutorCompleto[-2].upper()
            tutorNom = " ".join(nombreTutorCompleto[:-2]).upper()
        elif len(nombreTutorCompleto) == 2:
            tutorP = nombreTutorCompleto[0].upper()
            tutorM = nombreTutorCompleto[1].upper()
            tutorNom = ""

    if estudiante_match:
        print ("se obtuvo datos del estudiante")
        nombre_completo = estudiante_match.group(1).strip().split()
        
        if len(nombre_completo) >= 3:
            estudiante_apMaterno = nombre_completo[-1].upper()
            estudiante_apPaterno = nombre_completo[-2].upper()
            estudiante_nombre = " ".join(nombre_completo[:-2]).upper()
        elif len(nombre_completo) == 2:
            estudiante_apPaterno = nombre_completo[0].upper()
            estudiante_apMaterno = nombre_completo[1].upper()
            estudiante_nombre = ""

    fecha_match = re.search(r'(?:A|A:|A,|La Paz)\s*(\d{1,2})\s+de\s+([A-Za-z]+)\s+de\s+(\d{4})', texto_limpio, re.IGNORECASE)
    fecha_resolucion = None

    if fecha_match:
        dia = fecha_match.group(1).zfill(2) 
        mes_str = fecha_match.group(2).lower()
        anio = fecha_match.group(3)

        meses = {
            "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
            "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
            "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
        }
        mes = meses.get(mes_str, "01")
        
        fecha_resolucion = f"{anio}-{mes}-{dia}" 

    return {
        "titulo_perfil": titulo_perfil,
        "grado_estudiante": grado,
        "estudiante_nombre": estudiante_nombre,
        "estudiante_apPaterno": estudiante_apPaterno,
        "estudiante_apMaterno": estudiante_apMaterno,
        "fecha_resolucion": fecha_resolucion,
        "maestria": maestria,
        "grado_tutor": gradoT,
        "tutor_nombre": tutorNom,
        "tutor_apPaterno": tutorP, 
        "tutor_apMaterno": tutorM,
        "resolucion": resolucion,
        "presidente_tribunal": presidente,
        "primer_tribunal": primer_tribunal,
        "segundo_tribunal": segundo_tribunal
    }