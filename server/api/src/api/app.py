from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import configure_routes
from .debug_app import print_paths

print_paths()

app = configure_routes(FastAPI(title="My API", version="1.0.0"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to My API v1.0.0"}
