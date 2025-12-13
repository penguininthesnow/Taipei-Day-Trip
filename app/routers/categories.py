from fastapi import APIRouter
from app.db_connect import get_connection

router = APIRouter()

@router.get("/api/categories")
def get_categories():
    conn= get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT category FROM attraction ORDER BY category")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    categories = [row[0] for row in rows]

    return {"data": categories}
