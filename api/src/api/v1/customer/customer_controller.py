from services import CustomerDataAccessService


class CustomerController:
   def get(self) -> list[str]:
        return [c.to_json() for c in CustomerDataAccessService().get()]