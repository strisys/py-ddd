from model import Product


class ProductDataAccessService:
    def __init__(self):
      pass
    
    def get(self) -> list[Product]:
        return [
           Product("Glasses"),
           Product("Drone")
        ]