from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
import requests
from api.deps import get_current_user
from api.db_connect import get_connection

# TapPay 設定
TAPPAY_PARTNER_KEY = "partner_xxx"
TAPPAY_MERCHANT_ID = "merchant_xxx"
TAPPAY_ENDPOINT = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"

# 定義名稱
class Contact(BaseModel) :
    name: str
    email: str
    phone: str

class Trip(BaseModel):
    attraction: dict
    date: str
    time: str

class OrderData(BaseModel):
    price: int
    trip: Trip
    contact: Contact

class OrderRequest(BaseModel):
    prime: str
    order: OrderData

# Order API
router = APIRouter()

@router.post("/api/orders")
def create_order(
    order_req: OrderRequest,
    user = Depends(get_current_user)    
):
    print("Current USER:", user)

    db = get_connection()
    conn = db
    cursor = conn.cursor(dictionary=True)

    # 建立訂單
    # 產生訂單編號
    order_number = datetime.now().strftime('%Y%m%d') + uuid.uuid4().hex[:6]

    # 建立 UNPAID 訂單
    cursor.execute("""
        INSERT INTO orders (order_number, user_id, price, status) VALUES (%s, %s, %s, 'UNPAID')
    """,(
        order_number,
        user["id"], # "user_id"已經轉換
        order_req.order.price,
        # order_req.order.contact.name,
        # order_req.order.contact.email,
        # order_req.order.contact.phone
    ))
    conn.commit()

    order_id = cursor.lastrowid

    # 如果prime 是測試用就不用真的呼叫TapPay
    tappay_payload = {
        "prime": order_req.prime,
        "partner_key": TAPPAY_PARTNER_KEY,
        "merchant_id": TAPPAY_MERCHANT_ID,
        "details": f"Order {order_number}",
        "amount": order_req.order.price,
        "cardholder": {
            "phone_number": order_req.order.contact.phone,
            "name": order_req.order.contact.name,
            "email": order_req.order.contact.email
        },
        "remember": True
    }
    headers = {
        "Content-Type":"application/json",
        "x-api-key": TAPPAY_PARTNER_KEY
    }
    
    resp = requests.post(
        TAPPAY_ENDPOINT,
        json=tappay_payload,
        headers=headers
    )
    tappay_res = resp.json()

    # 根據結果更新 order
    if tappay_res.get("status") == 0:
        cursor.execute("""
            UPDATE orders SET status='PAID' WHERE id=%s
        """,(order_id,)
        )
    else:
        # 失敗也記錄 payment message
        cursor.execute("""
            INSERT INTO payments (order_id, status, message) VALUES (%s, %s, %s)
        """, (order_id, tappay_res.get("status"), tappay_res.get("msg")))
    conn.commit()


    # if resp.status_code != 200:
    #     raise HTTPException(status_code=500, detail="TapPay service error")

    
    # 回傳給前端
    return {
        "data": { "number": order_number }
    }


    
# 訂單查詢:根據訂單編號取得訂單資訊
@router.get("/api/order/{order_number}")
def get_order(order_number: str, user=Depends(get_current_user)):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                o.order_number,
                o.price,
                o.status,
                b.date,
                b.time,
                a.id AS attraction_id,
                a.name AS attraction_name,
                a.address AS attraction_address,
                GROUP_CONCAT(i.url) AS attraction_images
            FROM orders o
            JOIN booking b ON o.user_id = b.user_id
            JOIN attraction a ON b.attraction_id = a.id
            LEFT JOIN image i ON a.id = i.attraction_id
            WHERE o.order_number = %s AND o.user_id = %s
            GROUP BY 
                o.order_number,
                o.price,
                o.status,
                b.date,
                b.time,
                a.id,
                a.name,
                a.address;
        """,(order_number, user["id"]))

        result = cursor.fetchone()

        if not result:
            return {"data": None}
        
        images = []
        if result["attraction_images"]:
            images = result["attraction_images"].split(",")
        
        return {
            "data": {
                "number": result["order_number"],
                "price": result["price"],
                "status": result["status"],
                "trip": {
                    "attraction": {
                        "id": result["attraction_id"],
                        "name": result["attraction_name"],
                        "address": result["attraction_address"],
                        "image": images[0] if images else None
                    },
                    "date": result["date"],
                    "time": result["time"]
                },
                "contact": {
                    "name": user.get("name", ""),
                    "email": user.get("email", ""),
                    "phone": ""
                }
            }
        }
    finally:
        cursor.close()
        db.close()
