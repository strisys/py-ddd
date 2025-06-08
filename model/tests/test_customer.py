import pytest
from model import customer

@pytest.fixture
def sample_customer():
    return customer.Customer("Test", "test@example.com")

def test_customer_init(sample_customer):
    assert sample_customer._name == "Test"
    assert sample_customer._email == "test@example.com"

def test_customer_greet(sample_customer):
    assert sample_customer.greet() == "Hello, Test! Your email is test@example.com."
