import pytest

from menu.models import Category, MenuItem


@pytest.fixture
def category(db):
    return Category.objects.create(name="Test Cat")


def test_stock_zero_disables_availability(category):
    item = MenuItem.objects.create(category=category, name="Foo", price=2.5, stock=0)
    assert item.available is False


def test_stock_above_zero_keeps_available(category):
    item = MenuItem.objects.create(category=category, name="Bar", price=3.0, stock=5)
    assert item.available is True
