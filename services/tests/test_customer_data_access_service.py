from services import CustomerDataAccessService
from model import Customer

def test_get_returns_non_empty_list():
    service = CustomerDataAccessService()
    entities = service.get()

    assert isinstance(entities, list)
    assert len(entities) > 0
    assert all(isinstance(c, Customer) for c in entities)
