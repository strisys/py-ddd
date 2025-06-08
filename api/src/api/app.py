from fastapi import FastAPI
# from services import CustomerDataAccessService
# from model import Customer  

app = FastAPI()

# Initialize service
# customer_service = CustomerDataAccessService()

# @app.get("/customers")
# def get_customers() -> list[Customer]:
#     return customer_service.get()

@app.get("/customers")
def get_customers() -> list[str]:
    return ['hello']