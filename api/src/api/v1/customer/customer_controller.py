from services import CustomerDataAccessService

service = CustomerDataAccessService()

class CustomerController:
   async def get(self) -> list[str]:
        values = await service.get_all()
        return [c.to_json() for c in values]