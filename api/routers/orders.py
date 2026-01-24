import os
from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
import requests
from api.deps import get_current_user
from api.db_connect import get_connection


# TapPay 設定
TAPPAY_PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
TAPPAY_MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID")
TAPPAY_ENDPOINT = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"

if not TAPPAY_PARTNER_KEY or not TAPPAY_MERCHANT_ID:
    raise RuntimeError("Tappay keys are not set in enviroment variables")

# 定義名稱
class Contact(BaseModel) :
    name: str
    email: EmailStr
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):
        if not re.fullmatch(r"09\d{8}", v):
            raise ValueError("手機號碼格式錯誤!")
        return v

class Attraction(BaseModel):
    id: int
    name: str
    address: str
    image: Optional[str]    

class Trip(BaseModel):
    attraction: Attraction
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

@router.post("/orders")
def create_order(
    order_req: OrderRequest,
    user = Depends(get_current_user)    
):
    print("Current USER:", user)

    # =============== 後端驗證 =================
    if not order_req.prime:
        raise HTTPException(
            status_code=400,
            detail="缺少信用卡付款資訊~"
        )
    
    contact = order_req.order.contact
    if not contact.name or not contact.email or not contact.phone:
        raise HTTPException(
            status_code=400,
            detail="聯絡資訊不完整!"
        )
    # =======================================

    db = get_connection()
    conn = db
    cursor = conn.cursor(dictionary=True)

    # 建立訂單
    # 產生訂單編號
    try:
        order_number = datetime.now().strftime('%Y%m%d') + uuid.uuid4().hex[:6]

        # 建立 UNPAID 訂單
        cursor.execute("""
            INSERT INTO orders (order_number, user_id, price, status) VALUES (%s, %s, %s, 'UNPAID')
        """,(
            order_number,
            user["id"], # "user_id"已經轉換
            order_req.order.price
        ))
        conn.commit()

        order_id = cursor.lastrowid

        cursor.execute("""
            UPDATE booking SET order_id = %s WHERE user_id = %s AND order_id IS NULL
        """, (order_id, user["id"]))
        conn.commit()

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
            cursor.execute(
                "UPDATE orders SET status='PAID' WHERE id=%s", (order_id,)
            )
            # 訂單付款完後刪除原本訂單
            cursor.execute(
                "DELETE FROM booking WHERE order_id=%s", (order_id,)
            )
            conn.commit()

            print("Deleted booking rows =", cursor.rowcount)
            
        else:
            # 失敗也記錄 payment message
            cursor.execute("""
                INSERT INTO payments (order_id, status, message) VALUES (%s, %s, %s)
            """, (order_id, tappay_res.get("status"), tappay_res.get("msg")))
            conn.commit()

        
    
        # 回傳給前端
        return {
            "data": { "number": order_number }
        }
    finally:
        cursor.close()
        conn.close()



    
# 訂單查詢:根據訂單編號取得訂單資訊
@router.get("/order/{order_number}")
def get_order(order_number: str, user=Depends(get_current_user)):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                o.order_number AS number,
                o.price,
                o.status,
                b.date,
                b.time,
                a.id AS attraction_id,
                a.name AS attraction_name,
                a.address AS attraction_address,
                GROUP_CONCAT(i.url) AS attraction_images
            FROM orders o
            LEFT JOIN booking b ON b.order_id = o.id AND b.user_id = o.user_id
            LEFT JOIN attraction a ON b.attraction_id = a.id
            LEFT JOIN image i ON a.id = i.attraction_id
            WHERE o.order_number = %s  AND o.user_id = %s 
            GROUP BY
                o.order_number,
                o.price,
                o.status,
                b.date,
                b.time,
                a.id,
                a.name,
                a.address; 
        """, (order_number, user["id"]))

        result = cursor.fetchone()

        if not result:
            return {"data": None}
        
        images = []
        if result.get("attraction_images"):
            images = result["attraction_images"].split(",")
        
        return {
            "data": {
                "number": result["number"],
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
