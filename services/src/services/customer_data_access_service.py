from model import Customer


class CustomerDataAccessService:
    def __init__(self):
      pass
    
    def get(self) -> list[Customer]:
        return [
           Customer("Elon Musk", "elon.musk@x.com"),
           Customer("Bill Gates", "billgates@microsoft.com")
        ]