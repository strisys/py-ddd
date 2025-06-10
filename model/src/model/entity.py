class BaseEntity:   
   def __eq__(self, other) -> bool:
      if self is other:
         return True
      
      if type(self) != type(other):
         return False
      
      return self._get_comparable_attrs() == other._get_comparable_attrs()

   def __hash__(self) -> int:
      attrs = self._get_comparable_attrs()
      attrs_tuple = tuple(sorted(attrs.items()))
      return hash((type(self).__name__, attrs_tuple))

   def __repr__(self) -> str:
      attrs = self._get_comparable_attrs()
      attr_str = ", ".join(f"{k}='{v}'" for k, v in attrs.items())
      return f"{type(self).__name__}({attr_str})"

   def _get_comparable_attrs(self) -> dict:
      attrs = {}

      for attr_name in dir(self):
         if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
               attr_value = getattr(type(self), attr_name, None)
               if isinstance(attr_value, property):
                  attrs[attr_name] = getattr(self, attr_name)

      return attrs

   def throw_if_empty_string(self, value: str) -> str:
      value = (value or "").strip()
   
      if not value:
         raise ValueError("value cannot be empty")
      
      return value

   def __bool__(self) -> bool:
      attrs = self._get_comparable_attrs()
      return any(bool(value) for value in attrs.values())