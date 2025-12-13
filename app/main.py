from fastapi import FastAPI
from app.routers import attraction, mrt, categories

app = FastAPI()

app.include_router(attraction.router)
app.include_router(mrt.router)
app.include_router(categories.router)
