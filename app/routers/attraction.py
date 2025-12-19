
from fastapi import APIRouter
from app.db_connect import get_connection

router = APIRouter()
PAGE_SIZE=8

@router.get("/api/attractions")
def get_attractions(page: int = 0,
                    keyword: str | None = None, 
                    category: str | None = None
):
    start = page * PAGE_SIZE
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 對於 category及 keyword 給予篩選
    if category and keyword:
        cursor.execute("""
            SELECT * FROM attraction WHERE category = %s AND ( name LIKE %s OR COALESCE(mrt, '') LIKE %s OR category LIKE %s) LIMIT %s OFFSET %s
        """, (category, 
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            PAGE_SIZE + 1,
            start
        ))

    elif category:
        cursor.execute("""
            SELECT * FROM attraction WHERE category = %s LIMIT %s OFFSET %s
        """, (category,
            PAGE_SIZE + 1,
            start
        ))
        
    elif keyword:
        cursor.execute("""
            SELECT * FROM attraction WHERE name LIKE %s OR COALESCE(mrt, '') LIKE %s OR category LIKE %s LIMIT %s OFFSET %s
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
        """, (
            PAGE_SIZE + 1, start
        ))

    rows = cursor.fetchall()   #  rows

    if len(rows) > PAGE_SIZE:
        next_page = page + 1
        rows = rows[:PAGE_SIZE]
    else:
        next_page = None

    attraction_ids = [row["id"] for row in rows]

    images_map = {}
    if attraction_ids:
        image_cursor =  conn.cursor(dictionary=True)
        format_strings = ",".join(["%s"] * len(attraction_ids))
        image_cursor.execute(f"""
            SELECT attraction_id, url
            FROM image
            WHERE attraction_id IN ({format_strings})
        """, attraction_ids)

        for img in image_cursor.fetchall():
            images_map.setdefault(img["attraction_id"], []).append(img["url"])
        image_cursor.close()

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


# 判斷方式: 有category 就用 category篩選; 沒有就用keyword; 兩者都沒有指定就顯示全部; 兩個條件都出現就一起篩選

@router.get("/api/attraction/{attraction_id}")
def get_attraction(attraction_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 查詢景點
    cursor.execute("""
        SELECT id, name, category, description, address, transport, mrt, latitude, longitude FROM attraction WHERE id = %s
    """, (attraction_id,))

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return{
            "error":True,
            "message":"景點編號不正確"
        }
    
    # 查詢圖片
    cursor.execute("""
        SELECT url FROM image WHERE attraction_id = %s
    """, (attraction_id,))

    images = [img["url"] for img in cursor.fetchall()]

    cursor.close()
    conn.close()

    return{
        "data": {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "description": row["description"],
            "address": row["address"],
            "transport": row["transport"],
            "mrt": row["mrt"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "images": images
        }
    }


