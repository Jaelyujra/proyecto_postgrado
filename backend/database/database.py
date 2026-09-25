import psycopg2

DATABASE_URL = "postgresql://usuario:password@localhost:5433/postgrado"

def get_db_connection():
    return psycopg2.connect(
        host="localhost", 
        database="Postgrado", 
        user="postgres", 
        password="123456", 
        port="5433"  
    )