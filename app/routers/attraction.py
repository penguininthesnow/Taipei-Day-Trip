from fastapi import APIRouter
from app.db_connect import get_connection

router = APIRouter()

PAGE_SIZE = 8

@router.get("/api/attractions")
def get_attractions(page: int=0, keyword: str=None):
    start = page * PAGE_SIZE

    conn = get_connection()
    cursor= conn.cursor(dictionary=True)

    # 搜尋條件,(使用COALESCE進行搜尋)
    if keyword:
        query = """
            SELECT * FROM attraction WHERE name LIKE %s OR COALESCE(mrt, '') LIKE %s OR category LIKE %s LIMIT %s OFFSET %s
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", PAGE_SIZE + 1, start
        ))
    else:
        query = """
            SELECT * FROM attraction LIMIT %s OFFSET %s
        """
        cursor.execute(query, (PAGE_SIZE +1, start))
    
    # (先抓 Attraction)
    attractions = cursor.fetchall()

    # 判斷如果超過8筆，是否到下一頁
    if len(rows) > PAGE_SIZE:
        next_page = page + 1
        rows = rows[:PAGE_SIZE]
    else:
        next_page = None

    # 取出 Attraction IDs 用於查詢圖片 (attractions)
    attraction_ids = [row["id"] for row in attractions]
    if attraction_ids:
        cursor.execute(
            "SELECT attraction_id, url FROM image WHERE attraction_id IN (%s)" % ",".join (["%s"] * len(attraction_ids)),
            attraction_ids
        )
        image_attractions = cursor.fetchall()
        # //
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
    else:
        images_map = {}

    # 組回傳資料 //
    data = []
    for row in attractions[:PAGE_SIZE]:
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

    return{"nextPage": next_page, "data":data}

# /api/attraction/{id}
@router.get("/api/attraction/{attraction_id}")
def get_attraction(attraction_id: int):
    
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)

    # 查景點
    cursor.execute("SELECT * FROM attraction WHERE id= %s", (attraction_id,))
    row = cursor.fetchone()

    if not row:
        return{"error": True, "message": "景點編號不正確"}
    
    # 查圖片
    cursor.execute("SELECT url FROM image WHERE attraction_id = %s", (attraction_id,))
    images = [img["url"] for img in cursor.fetchall()]

    cursor.close()
    conn.close()

    return{
        "data":{
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