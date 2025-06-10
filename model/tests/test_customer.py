import pytest
from pydantic import ValidationError
from model import Customer, CustomerData


class TestCustomerDataValidation:
   
   def test_valid_customer_data(self):
      data = CustomerData(name="John Doe", email="john@example.com")
      assert data.name == "John Doe"
      assert str(data.email) == "john@example.com"
   
   def test_name_validation_empty_string(self):
      with pytest.raises(ValidationError):
         CustomerData(name="", email="john@example.com")
   
   def test_name_validation_whitespace_only(self):
      with pytest.raises(ValidationError):
         CustomerData(name="   ", email="john@example.com")
   
   def test_name_validation_invalid_characters(self):
      with pytest.raises(ValidationError):
         CustomerData(name="John123", email="john@example.com")
   
   def test_name_validation_valid_special_chars(self):
      data = CustomerData(name="José O'Connor-Smith", email="john@example.com")
      assert data.name == "José O'Connor-Smith"
   
   def test_name_strips_whitespace(self):
      data = CustomerData(name="  John Doe  ", email="john@example.com")
      assert data.name == "John Doe"
   
   def test_email_validation_invalid_format(self):
      with pytest.raises(ValidationError):
         CustomerData(name="John", email="invalid-email")
   
   def test_email_validation_multiple_at_symbols(self):
      with pytest.raises(ValidationError):
         CustomerData(name="John", email="john@@example.com")
   
   def test_name_too_long(self):
      long_name = "a" * 101
      with pytest.raises(ValidationError):
         CustomerData(name=long_name, email="john@example.com")


class TestCustomerSerialization:
   
   def test_to_serializable(self):
      customer = Customer("Jane Doe", "jane@example.com")
      serializable = customer.to_serializable()
      assert isinstance(serializable, CustomerData)
      assert serializable.name == "Jane Doe"
      assert str(serializable.email) == "jane@example.com"
   
   def test_from_serializable(self):
      data = CustomerData(name="Bob Smith", email="bob@example.com")
      customer = Customer.from_serializable(data)
      assert customer.name == "Bob Smith"
      assert customer.email == "bob@example.com"
   
   def test_to_dict(self):
      customer = Customer("Alice", "alice@example.com")
      result = customer.to_dict()
      expected = {"name": "Alice", "email": "alice@example.com"}
      assert result == expected
   
   def test_from_dict_valid(self):
      data = {"name": "Charlie", "email": "charlie@example.com"}
      customer = Customer.from_dict(data)
      assert customer.name == "Charlie"
      assert customer.email == "charlie@example.com"
   
   def test_from_dict_invalid(self):
      data = {"name": "", "email": "invalid"}
      with pytest.raises(ValidationError):
         Customer.from_dict(data)
   
   def test_to_json(self):
      customer = Customer("David", "david@example.com")
      json_str = customer.to_json()
      assert '"name":"David"' in json_str
      assert '"email":"david@example.com"' in json_str
   
   def test_from_json_valid(self):
      json_str = '{"name": "Eve", "email": "eve@example.com"}'
      customer = Customer.from_json(json_str)
      assert customer.name == "Eve"
      assert customer.email == "eve@example.com"
   
   def test_from_json_invalid(self):
      json_str = '{"name": "", "email": "invalid"}'
      with pytest.raises(ValidationError):
         Customer.from_json(json_str)


class TestCustomerValidateData:
   
   def test_validate_data_valid(self):
      data = {"name": "Frank", "email": "frank@example.com"}
      errors = Customer.validate_data(data)
      assert errors is None
   
   def test_validate_data_empty_name(self):
      data = {"name": "", "email": "frank@example.com"}
      errors = Customer.validate_data(data)
      assert errors is not None
      assert len(errors) > 0
      assert any(error["field"] == "name" for error in errors)
   
   def test_validate_data_invalid_email(self):
      data = {"name": "Frank", "email": "invalid-email"}
      errors = Customer.validate_data(data)
      assert errors is not None
      assert len(errors) > 0
      assert any(error["field"] == "email" for error in errors)
   
   def test_validate_data_multiple_errors(self):
      data = {"name": "", "email": "invalid"}
      errors = Customer.validate_data(data)
      assert errors is not None
      assert len(errors) >= 2
      field_names = [error["field"] for error in errors]
      assert "name" in field_names
      assert "email" in field_names
   
   def test_validate_data_error_structure(self):
      data = {"name": "", "email": "frank@example.com"}
      errors = Customer.validate_data(data)
      assert errors is not None
      error = errors[0]
      assert "field" in error
      assert "message" in error
      assert "input" in error
      assert error["field"] == "name"
      assert isinstance(error["message"], str)


class TestCustomerValidateAndThrow:
   
   def test_validate_and_throw_valid(self):
      data = {"name": "Grace", "email": "grace@example.com"}
      Customer.validate_and_throw(data)
   
   def test_validate_and_throw_invalid_name(self):
      data = {"name": "", "email": "grace@example.com"}
      with pytest.raises(ValidationError):
         Customer.validate_and_throw(data)
   
   def test_validate_and_throw_invalid_email(self):
      data = {"name": "Grace", "email": "invalid"}
      with pytest.raises(ValidationError):
         Customer.validate_and_throw(data)
   
   def test_validate_and_throw_multiple_errors(self):
      data = {"name": "", "email": "invalid"}
      with pytest.raises(ValidationError):
         Customer.validate_and_throw(data)


class TestCustomerValidateInstance:
   
   def test_validate_valid_customer(self):
      customer = Customer("Henry", "henry@example.com")
      errors = customer.validate()
      assert errors is None
   
   def test_validate_invalid_name_after_creation(self):
      customer = Customer("Henry", "henry@example.com")
      customer._name = ""
      errors = customer.validate()
      assert errors is not None
      assert len(errors) > 0
      assert any(error["field"] == "name" for error in errors)
   
   def test_validate_invalid_email_after_creation(self):
      customer = Customer("Henry", "henry@example.com")
      customer._email = "invalid-email"
      errors = customer.validate()
      assert errors is not None
      assert len(errors) > 0
      assert any(error["field"] == "email" for error in errors)
   
   def test_validate_multiple_errors_after_creation(self):
      customer = Customer("Henry", "henry@example.com")
      customer._name = ""
      customer._email = "invalid"
      errors = customer.validate()
      assert errors is not None
      assert len(errors) >= 2
      field_names = [error["field"] for error in errors]
      assert "name" in field_names
      assert "email" in field_names


class TestCustomerValidationEdgeCases:
   
   def test_validate_data_missing_fields(self):
      data = {"name": "Test"}
      errors = Customer.validate_data(data)
      assert errors is not None
      assert any(error["field"] == "email" for error in errors)
   
   def test_validate_data_extra_fields(self):
      data = {
         "name": "Test User",
         "email": "test@example.com",
         "extra_field": "should be ignored"
      }
      errors = Customer.validate_data(data)
      assert errors is None
   
   def test_validate_data_none_values(self):
      data = {"name": None, "email": None}
      errors = Customer.validate_data(data)
      assert errors is not None
      assert len(errors) >= 2
   
   def test_validate_complex_name_patterns(self):
      valid_names = [
         "Mary-Jane Smith",
         "José María",
         "O'Connor",
         "Jean-Luc Picard",
         "Anne-Marie St. Pierre"
      ]
      
      for name in valid_names:
         data = {"name": name, "email": "test@example.com"}
         errors = Customer.validate_data(data)
         assert errors is None, f"Name '{name}' should be valid"
   
   def test_validate_invalid_name_patterns(self):
      invalid_names = [
         "John123",
         "Mary@Smith",
         "Test#User",
         "User$Name",
         "123Numbers"
      ]
      
      for name in invalid_names:
         data = {"name": name, "email": "test@example.com"}
         errors = Customer.validate_data(data)
         assert errors is not None, f"Name '{name}' should be invalid"
   
   def test_validate_various_email_formats(self):
      valid_emails = [
         "user@domain.com",
         "user.name@domain.co.uk",
         "user+tag@domain.org",
         "123@domain.net",
         "test-email@sub.domain.com"
      ]
      
      for email in valid_emails:
         data = {"name": "Test User", "email": email}
         errors = Customer.validate_data(data)
         assert errors is None, f"Email '{email}' should be valid"


@pytest.fixture
def sample_customer():
   return Customer("Sample User", "sample@example.com")


@pytest.fixture
def invalid_customer_data():
   return [
      {"name": "", "email": "test@example.com"},
      {"name": "Test", "email": "invalid-email"},
      {"name": "", "email": "invalid"},
      {"name": "Test123", "email": "test@example.com"}
   ]


class TestCustomerWithFixtures:
   
   def test_sample_customer_validation(self, sample_customer):
      errors = sample_customer.validate()
      assert errors is None
   
   def test_invalid_data_validation(self, invalid_customer_data):
      for data in invalid_customer_data:
         errors = Customer.validate_data(data)
         assert errors is not None
         assert len(errors) > 0