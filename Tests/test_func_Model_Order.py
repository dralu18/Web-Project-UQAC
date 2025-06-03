import pytest
from session_Part.Models.Order import Order
from session_Part.Models.Product import Product
from session_Part.Models.CreditCard import CreditCard
from session_Part.Models.Shipping_information import Shipping_information
from session_Part.Models.Transaction import Transaction


@pytest.fixture
def sample_order():
    product = Product(id=1, price=1000, name="Test Product")
    order = Order(
        id=1,
        product=product,
        quantity=2,
        total_price=2000,
        total_price_tax=2300,
        email="test@example.com",
        shipping_price=500,
        paid=False
    )
    return order


def test_load_object_to_json_basic(sample_order):
    result = sample_order.load_object_to_json()

    assert isinstance(result, dict)
    assert "order" in result
    order_data = result["order"]

    assert order_data["id"] == 1
    assert order_data["total_price"] == 2000
    assert order_data["total_price_tax"] == 2300
    assert order_data["email"] == "test@example.com"
    assert order_data["shipping_price"] == 500
    assert order_data["paid"] is False
    assert order_data["credit_card"] == {}
    assert order_data["shipping_information"] == {}
    assert order_data["transaction"] == {}
    assert order_data["product"]["id"] == 1
    assert order_data["product"]["quantity"] == 2


def test_load_object_to_json_full(sample_order):
    credit_card = CreditCard(
        name="John Doe",
        first_digits=4532,
        last_digits=1234,
        expiration_year=2025,
        expiration_month=12
    )

    shipping_info = Shipping_information(
        country="Canada",
        address="123 Test St",
        postal_code="G7X 2B2",
        city="Chicoutimi",
        province="QC"
    )

    transaction = Transaction(
        success=True,
        amount_charged=2500
    )

    sample_order.credit_card = credit_card
    sample_order.shipping_information = shipping_info
    sample_order.transaction = transaction

    result = sample_order.load_object_to_json()
    order_data = result["order"]

    assert order_data["credit_card"] == credit_card.load_object_to_json()
    assert order_data["shipping_information"] == shipping_info.load_object_to_json()
    assert order_data["transaction"] == transaction.load_object_to_json()


def test_is_valid_email():
    order = Order()

    assert order.is_valid_email("test@example.com") is True
    assert order.is_valid_email("user.name@domain.co.uk") is True
    assert order.is_valid_email("user-name@domain.com") is True

    assert order.is_valid_email("test@") is False
    assert order.is_valid_email("test@.com") is False
    assert order.is_valid_email("@domain.com") is False
    assert order.is_valid_email("testdomain.com") is False
    assert order.is_valid_email("") is False
    assert order.is_valid_email(None) is False
    assert order.is_valid_email(123) is False


def test_is_valid_province():
    order = Order()

    assert order.is_valid_province("QC") is True
    assert order.is_valid_province("qc") is True
    assert order.is_valid_province("ON") is True
    assert order.is_valid_province("AB") is True
    assert order.is_valid_province("BC") is True
    assert order.is_valid_province("NS") is True

    assert order.is_valid_province("QB") is False
    assert order.is_valid_province("") is False
    assert order.is_valid_province(None) is False
    assert order.is_valid_province(123) is False
    assert order.is_valid_province("QUEBEC") is False
    assert order.is_valid_province("XX") is False