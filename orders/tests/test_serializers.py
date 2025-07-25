import pytest

from menu.models import Category, MenuItem
from orders.serializers import OrderSerializer


@pytest.fixture
def menu_item(db, category):
    return MenuItem.objects.create(category=category, name="X", price=5, stock=2)


def test_order_serializer_rejects_overstock(menu_item, user):
    data = {
        "customer": user.id,
        "items": [{"menu_item_id": menu_item.id, "quantity": 3}],
    }
    ser = OrderSerializer(data=data)
    assert not ser.is_valid()
    assert "Only 2 x 'X' available." in str(ser.errors)
