from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from users.routes import router as user_router
from settings import settings


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router=user_router)


@app.on_event("startup")
async def init_db():
    await settings.init_connection()


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=8000, reload=True)
