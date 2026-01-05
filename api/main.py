
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from api.routers import attraction, mrt, categories,user


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# 首頁
@app.get("/")
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

#連結景點頁面
@app.get("/attraction/{id}")
def attraction_page(id: int):
    return FileResponse(os.path.join("static", "attraciton.html"))


# API routers
app.include_router(attraction.router)
app.include_router(mrt.router)
app.include_router(categories.router)
app.include_router(user.router)


