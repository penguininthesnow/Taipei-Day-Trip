from fastapi import APIRouter
from app.db_connect import get_connection

router = APIRouter()
PAGE_SIZE=8

@router.get("/api/attractions")
def get_attractions(page: int = 0, keyword: str | None = None):
    start = page * PAGE_SIZE

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if keyword:
        cursor.execute("""
            SELECT *
            FROM attraction
            WHERE name LIKE %s
               OR COALESCE(mrt, '') LIKE %s
               OR category LIKE %s
            LIMIT %s OFFSET %s
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            PAGE_SIZE + 1,
            start
        ))
    else:
        cursor.execute("""
            SELECT *
            FROM attraction
            LIMIT %s OFFSET %s
        """, (PAGE_SIZE + 1, start))

    rows = cursor.fetchall()   #  rows

    if len(rows) > PAGE_SIZE:
        next_page = page + 1
        rows = rows[:PAGE_SIZE]
    else:
        next_page = None

    attraction_ids = [row["id"] for row in rows]

    images_map = {}
    if attraction_ids:
        format_strings = ",".join(["%s"] * len(attraction_ids))
        cursor.execute(f"""
            SELECT attraction_id, url
            FROM image
            WHERE attraction_id IN ({format_strings})
        """, attraction_ids)

        for img in cursor.fetchall():
            images_map.setdefault(img["attraction_id"], []).append(img["url"])

    data = []
    for row in rows:
        data.append({
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "description": row["description"],
            "address": row["address"],
            "transport": row["transport"],
            "mrt": row["mrt"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "images": images_map.get(row["id"], [])
        })

    cursor.close()
    conn.close()

    return {
        "nextPage": next_page,
        "data": data
    }
