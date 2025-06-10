import sys
from fastapi import FastAPI
from .router import configure_routes

print(">>> sys.path:\n", "\n".join(sys.path))
# sys.path = [p for p in sys.path if not p.startswith("/app")]

app = configure_routes(FastAPI(title="My API", version="1.0.0"))

@app.get("/")
def root():
    return {"message": "Welcome to My API"}
