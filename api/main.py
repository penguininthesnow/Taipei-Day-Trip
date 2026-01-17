
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from api.routers import attraction, mrt, categories,user,booking, orders
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# 首頁
@app.get("/")
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

#連結景點頁面
@app.get("/attraction/{attractionId}")
def attraction_page(attractionId: int):
    return FileResponse(os.path.join("static", "attraction.html"))

# 連結 booking 頁面
@app.get("/booking")
def booking_page():
    return FileResponse(os.path.join("static", "booking.html"))

# API routers
app.include_router(attraction.router)
app.include_router(mrt.router)
app.include_router(categories.router)
app.include_router(user.router)
app.include_router(booking.router) # from booking.py
app.include_router(orders.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)