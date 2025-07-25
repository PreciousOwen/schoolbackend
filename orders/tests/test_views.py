import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


def test_order_list_requires_auth(client):
    resp = client.get("/api/orders/")
    assert resp.status_code == 403


def test_customer_can_create_and_list_orders(client, user, menu_item):
    client.login(username="alice", password="password123")
    # create
    resp = client.post(
        "/api/orders/",
        {"customer": user.id, "items": [{"menu_item_id": menu_item.id, "quantity": 1}]},
        format="json",
    )
    assert resp.status_code == 201
    # list
    resp = client.get("/api/orders/")
    assert resp.status_code == 200
    assert resp.json()["results"][0]["customer"] == user.id
