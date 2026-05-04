from fastapi import FastAPI
from routers import favorite, news, users
from fastapi.middleware.cors import CORSMiddleware

from utils.exception import register_exception_handlers
from utils.response import success

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  #
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/")
async def root():
    return success(data={"message": "Hello World"})


app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
