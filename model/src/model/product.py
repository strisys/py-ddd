from .entity import BaseEntity

class Product(BaseEntity):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = self.throw_if_empty_string(value)

    def __str__(self) -> str:
        return self.name