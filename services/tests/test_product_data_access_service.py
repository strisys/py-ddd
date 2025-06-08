from services import ProductDataAccessService
from model import Product

def test_get_returns_non_empty_list():
    service = ProductDataAccessService()
    entities = service.get()

    assert isinstance(entities, list)
    assert len(entities) > 0
    assert all(isinstance(c, Product) for c in entities)
