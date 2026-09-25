from fastapi import APIRouter, UploadFile, File, Body
from services.ocr_service import procesar_pdf_ocr
from database.crud import procesar_en_base_de_datos

router = APIRouter()

@router.post("/extraer-datos/")
async def extraer_datos(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    datos_extraidos = procesar_pdf_ocr(pdf_bytes)
    return {"status": "success", "datos": datos_extraidos}

@router.post("/guardar-resolucion/")
def guardar_resolucion(payload: dict = Body(...)):
    # Verificamos si el frontend envió el JSON envuelto en la llave "datos"
    # Si existe, extraemos solo el diccionario interior. Si no, usamos el payload tal cual.
    datos_a_procesar = payload.get("datos", payload)
    
    resultado = procesar_en_base_de_datos(datos_a_procesar)
    return resultado