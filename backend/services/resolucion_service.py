from database.crud import procesar_en_base_de_datos
from services.ocr_service import procesar_pdf_ocr

def procesar_nueva_resolucion(pdf_bytes):
    datos_extraidos = procesar_pdf_ocr(pdf_bytes)
    resultado = procesar_en_base_de_datos(datos_extraidos)
    return resultado