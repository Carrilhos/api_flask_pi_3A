from app.database import get_connection


def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produto")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows