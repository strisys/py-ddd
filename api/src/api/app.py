from fastapi import FastAPI
from services import CustomerDataAccessService, ProductDataAccessService

app = FastAPI()

@app.get("/customers")
def get_customers() -> list[str]:
    return [c.name for c in CustomerDataAccessService().get()]

@app.get("/products")
def get_products() -> list[str]:
    return [c.name for c in ProductDataAccessService().get()]