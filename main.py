from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resources.routes import api_router
import uvicorn

app = FastAPI()
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
