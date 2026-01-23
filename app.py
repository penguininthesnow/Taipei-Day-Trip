from dotenv import load_dotenv
from pathlib import Path

# .env # "parent":退一層的意思
env_path = Path(__file__).resolve().parent
ENV_path = env_path / ".env"
load_dotenv(dotenv_path=ENV_path)

from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
app=FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


# main.py
from api.routers import attraction, mrt, categories

app.include_router(attraction.router)
app.include_router(mrt.router)
app.include_router(categories.router)