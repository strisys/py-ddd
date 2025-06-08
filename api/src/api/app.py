from fastapi import FastAPI
from services import CustomerDataAccessService
from model import Customer  

app = FastAPI()

customer_service = CustomerDataAccessService()

@app.get("/customers")
def get_customers() -> list[str]:
    return [c.name for c in CustomerDataAccessService().get()]
