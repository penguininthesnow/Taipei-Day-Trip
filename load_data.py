import json
import mysql.connector
import re

#  連線 MySQL
db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="taipei_day_trip"
)
cursor=db.cursor()

# 讀取 JSON
with open("data/taipei-attractions.json", "r", encoding="utf-8") as file:
    data=json.load(file)["result"]["results"]

# 過濾JPG/PNG的圖片 url
def filter_image_urls(file_str):
    urls =re.findall(r'(https://.*?\.(?:jpg|png|JPG|PNG))', file_str)
    return [url for url in urls if url.lower().endswith(("jpg", "png"))]

# 匯入資料
for item in data:
    # attraction 表
    cursor.execute("""
        INSERT INTO attraction (name, category, description, address, transport, mrt, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,(
        item["name"], 
        item["CAT"], 
        item["description"], 
        item["address"], 
        item["direction"], 
        item["MRT"], 
        item["latitude"], 
        item["longitude"]
    ))
    attraction_id = cursor.lastrowid

    # image表
    urls= filter_image_urls(item["file"])
    print("DEBUG urls:", urls)

    for url in urls:
        cursor.execute(
            "INSERT INTO image (attraction_id, url) VALUES (%s, %s)", (attraction_id, url)
        )

    # MRT表
    if item["MRT"]:
        cursor.execute(
            "INSERT INTO mrt (name, attraction_id) VALUES (%s, %s)", (item["MRT"], attraction_id)
        )

db.commit()
cursor.close()
db.close()

print("匯入完成!")