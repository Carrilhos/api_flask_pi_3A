from app.database import get_connection

def find_all_categories():
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute(
    """
    SELECT id,
           nome,
           descricao
    FROM categoria
    """
  )

  rows = cursor.fetchall()
  cursor.close()
  conn.close()

  categories = []

  for row in rows:
    categories.append(
      {
        "id": row[0],
        "nome": row[1],
        "descricao": row[2]
      }
    )

  return categories

def find_category_by_id(id_category):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute(
    """
    SELECT id,
           nome,
           descricao
    FROM categoria
    WHERE id = %s
    """,
    (id_category,),
  )

  row = cursor.fetchone()
  cursor.close()
  conn.close()

  if not row:
    return None
  
  return {
    "id": row[0],
    "nome": row[1],
    "descricao": row[2]
  }