from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import resoluciones

app = FastAPI(title="API de Resoluciones")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resoluciones.router, prefix="/api")