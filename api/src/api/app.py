from fastapi import FastAPI
from services import CustomerDataAccessService

app = FastAPI()

@app.get("/customers", response_model=list[str])
def get_customers() -> list[str]:
    return [c.to_json() for c in CustomerDataAccessService().get()]