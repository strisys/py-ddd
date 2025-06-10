from fastapi import FastAPI
from .router import configure_routes

app = configure_routes(FastAPI(title="My API", version="1.0.0"))

@app.get("/")
def root():
    return {"message": "Welcome to My API"}
