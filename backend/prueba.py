from database.database import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    # Consultamos el esquema real de la tabla resolucion
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'resolucion';")
    columnas = cursor.fetchall()
    
    print("Columnas que ve Python en la tabla 'resolucion':")
    print([col[0] for col in columnas])
    
    conn.close()
except Exception as e:
    print("Error:", e)