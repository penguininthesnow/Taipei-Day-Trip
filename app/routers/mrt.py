from fastapi import APIRouter
from app.db_connect import get_connection

router = APIRouter()

@router.get("/api/mrts")
def get_mrts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT mrt.name AS mrt, COUNT(*) AS count FROM mrt GROUP BY mrt.name ORDER BY count DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {"data": [row["mrt"] for row in rows]}