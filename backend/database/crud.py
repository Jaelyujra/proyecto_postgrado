import psycopg2
from database.database import get_db_connection

def verificar_existencia(cursor, datos):
    """
    Verifica si la resolución ya fue registrada previamente en el sistema.
    Realiza un JOIN entre resolucion, perfilTesis y estudiantePostgrado con la nueva estructura.
    """
    query_verificacion = """
        SELECT r.id_resolucion 
        FROM resolucion r
        JOIN perfilTesis pt ON r.id_perfil = pt.id_perfilTesis
        JOIN estudiantePostgrado ep ON pt.id_estudiante = ep.id_estudiantePostgrado
        WHERE ep.nombre = %s AND ep.apellido_Paterno = %s AND pt.titulo = %s
    """
    cursor.execute(query_verificacion, (
        datos['estudiante_nombre'], 
        datos['estudiante_apPaterno'], 
        datos['titulo_perfil']
    ))
    
    return cursor.fetchone() is not None

def procesar_en_base_de_datos(datos):
    """
    Maneja la transacción jerárquica para guardar los datos de la resolución.
    Si cualquier inserción falla, se ejecuta un rollback general.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existe en la base de datos
        if verificar_existencia(cursor, datos):
            return {"status": "warning", "message": "La resolución ya existe en la base de datos."}
        
        # 1. Procesar Estudiante
        cursor.execute("""
            SELECT id_estudiantePostgrado FROM estudiantePostgrado 
            WHERE nombre = %s AND apellido_Paterno = %s AND apellido_Materno = %s;
        """, (datos['estudiante_nombre'], datos['estudiante_apPaterno'], datos['estudiante_apMaterno']))
        
        resultado_estudiante = cursor.fetchone()
        if resultado_estudiante:
            id_estudiante = resultado_estudiante[0]
        else:
            cursor.execute("""
                INSERT INTO estudiantePostgrado (nombre, apellido_Paterno, apellido_Materno, grado_Academico) 
                VALUES (%s, %s, %s, %s) RETURNING id_estudiantePostgrado;
            """, (datos['estudiante_nombre'], datos['estudiante_apPaterno'], datos['estudiante_apMaterno'], datos['grado_estudiante'] or 'N/A'))
            id_estudiante = cursor.fetchone()[0]

        # 2. Procesar Tutor
        # Se requiere verificar o insertar al tutor ya que la tabla perfilTesis ahora depende de él
        cursor.execute("""
            SELECT id_tutor FROM tutor 
            WHERE nombre = %s AND apellido_Paterno = %s AND apellido_Materno = %s;
        """, (datos['tutor_nombre'], datos['tutor_apPaterno'], datos['tutor_apMaterno']))
        
        resultado_tutor = cursor.fetchone()
        if resultado_tutor:
            id_tutor = resultado_tutor[0]
        else:
            cursor.execute("""
                INSERT INTO tutor (nombre, apellido_Paterno, apellido_Materno, grado_Academico) 
                VALUES (%s, %s, %s, %s) RETURNING id_tutor;
            """, (datos['tutor_nombre'], datos['tutor_apPaterno'], datos['tutor_apMaterno'], datos['grado_tutor'] or 'N/A'))
            id_tutor = cursor.fetchone()[0]

        # 3. Procesar Perfil de Tesis
        # Incluye las nuevas columnas obtenidas del OCR: maestría y los integrantes del tribunal
        cursor.execute("""
            INSERT INTO perfilTesis (titulo, nombre_Maestria, presidente, primerTribunal, segundoTribunal, id_estudiante, id_tutor) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_perfilTesis;
        """, (
            datos['titulo_perfil'], 
            datos['maestria'], 
            datos['presidente_tribunal'], 
            datos['primer_tribunal'], 
            datos['segundo_tribunal'], 
            id_estudiante, 
            id_tutor
        ))
        id_perfil = cursor.fetchone()[0]

        # 4. Procesar Resolución
        cursor.execute("""
            INSERT INTO resolucion (fecha, nro_resolucion, id_perfil) 
            VALUES (%s, %s, %s) RETURNING id_resolucion;
        """, (datos['fecha_resolucion'], datos['resolucion'], id_perfil))
        
        # Confirmar toda la transacción
        conn.commit()
        return {"status": "success", "message": "Resolución procesada y guardada correctamente."}
        
    except Exception as e:
        conn.rollback() 
        return {"status": "error", "message": f"Error en la base de datos: {str(e)}"}
    finally:
        cursor.close()
        conn.close()