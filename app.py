from dotenv import load_dotenv
from pathlib import Path
import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from api.routers import attraction, mrt, categories, user, booking, orders

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")

@app.get("/attraction/{id}", include_in_schema=False)
async def attraction_page(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")

@app.get("/booking", include_in_schema=False)
async def booking_page(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")

@app.get("/thankyou", include_in_schema=False)
async def thankyou_page(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")

app.include_router(attraction.router)
app.include_router(mrt.router)
app.include_router(categories.router)
app.include_router(user.router)
app.include_router(booking.router)
app.include_router(orders.router, prefix="/api")

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