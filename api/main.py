
from fastapi import FastAPI
from api.routers import attraction, mrt, categories,user


app = FastAPI()

app.include_router(attraction.router)
app.include_router(mrt.router)
app.include_router(categories.router)
app.include_router(user.router)


