from fastapi import APIRouter
from .customer_controller import CustomerController

router = APIRouter(redirect_slashes=True)
controller = CustomerController()

@router.get("", response_model=list[str])
@router.get("/", response_model=list[str])
async def get_customers() -> list[str]:
    return await controller.get()