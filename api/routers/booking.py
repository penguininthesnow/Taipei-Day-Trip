# GET /api/booking
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from api.deps import get_current_user
from api.db_connect import get_connection
from api.utils.jwt import decode_jwt
from pydantic import BaseModel, field_validator # POST /api/booking

router = APIRouter()

@router.get("/api/booking")
def get_booking(user=Depends(get_current_user)):
    user_id = user["id"]

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                b.date,
                b.time,
                b.price,
                a.id AS attraction_id,
                a.name AS attraction_name,
                a.address AS attraction_address,
                i.url AS image
            FROM booking b
            JOIN attraction a ON b.attraction_id = a.id
            LEFT JOIN image i ON a.id = i.attraction_id
            WHERE b.user_id = %s
                AND b.order_id IS NULL 
            LIMIT 1                       
        """, (user_id,))

        booking = cursor.fetchone()

        # 沒有 booking 顯示{null}
        if not booking:
            return {"data": None}
        
        return {
            "data": {
                "attraction": {
                    "id": booking["attraction_id"],
                    "name": booking["attraction_name"],
                    "address": booking["attraction_address"],
                    "image": booking["image"]
                },
                "date": booking["date"].isoformat(),
                "time": booking["time"],
                "price": booking["price"]
            }
        }
    
    finally:
        cursor.close()
        db.close()

# POST /api/booking
class BookingCreate(BaseModel):
    attractionId: int
    date: datetime.date # 用 "date" 型別，而非"str"
    time: str
    price: int

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: datetime.date):
        if v < datetime.date.today():
            raise ValueError("預定日期不可為過去日期!")
        return v

@router.post("/api/booking")
def create_booking(
    booking: BookingCreate,
    user=Depends(get_current_user)
):
    user_id = user["id"]
    print("CREATE booking for user", user_id)

    db = get_connection()
    cursor = db.cursor()

    try:
        # 如果有舊的就先刪掉，確保只有一筆
        cursor.execute(
            "DELETE FROM booking WHERE user_id = %s AND order_id IS NULL",
            (user_id,)
        )

        # 新增 booking
        cursor.execute("""
            INSERT INTO booking (user_id, attraction_id, date, time, price, order_id) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            booking.attractionId,
            booking.date,
            booking.time,
            booking.price,
            None
        ))

        db.commit()
        return {"ok": True}
    
    
    finally:
        cursor.close()
        db.close()
    
# DELETE /api/booking
@router.delete("/api/booking")
def delete_booking(user=Depends(get_current_user)):
    user_id = user["id"]

    db = get_connection()  
    cursor = db.cursor()

    try:
        cursor.execute(
            "DELETE FROM booking WHERE user_id = %s",
            (user_id,)
        )
        db.commit()

        return {"ok": True}

    finally:
        cursor.close()
        db.close()

