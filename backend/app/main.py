from fastapi import FastAPI
from backend.app.api.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "GravityWork API"}
