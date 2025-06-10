from fastapi import APIRouter
from .customer_controller import CustomerController

router = APIRouter()

@router.get("/", response_model=list[str])
def get_customers() -> list[str]:
    return CustomerController().get()