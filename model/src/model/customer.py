class Customer:
   def __init__(self, name: str, email: str):
      self._name = name
      self._email = email

   @property
   def name(self) -> str:
      return self._name

   def greet(self) -> str:
      return f"Hello, {self._name}! Your email is {self._email}."