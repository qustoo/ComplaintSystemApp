from fastapi import FastAPI
import uvicorn
from resources.routes import api_router

app = FastAPI()
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "hello world!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
