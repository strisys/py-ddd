from model import Customer

print(">>> USING customer_data_access_service.py FROM:", __file__)

class CustomerDataAccessService:
   async def get(self) -> list[Customer]:
      return [
         Customer("Elon Musk", "elon.musk@x.com"),
         Customer("Bill Gates", "billgates@microsoft.com"),
         Customer("Pichai Sundararajan", "psundararajan@goolge.com")
      ]