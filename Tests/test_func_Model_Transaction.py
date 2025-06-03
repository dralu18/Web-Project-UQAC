import pytest
from session_Part.Models.Transaction import Transaction


@pytest.fixture
def sample_transaction():
    return Transaction(
        id="trans_123456789",
        success=True,
        amount_charged=1500
    )


def test_load_object_to_json_successful_transaction(sample_transaction):
    result = sample_transaction.load_object_to_json()

    assert isinstance(result, dict), "Le résultat devrait être un dictionnaire"

    assert result["id"] == "trans_123456789"
    assert result["success"] is True
    assert result["amount_charged"] == 1500

    assert len(result) == 3, "Le dictionnaire devrait avoir exactement 3 clés"

    expected_keys = {"id", "success", "amount_charged"}
    assert set(result.keys()) == expected_keys, "Les clés ne correspondent pas aux attributs attendus"


def test_load_object_to_json_failed_transaction():
    failed_transaction = Transaction(
        id="trans_failed_987",
        success=False,
        amount_charged=0
    )

    result = failed_transaction.load_object_to_json()

    assert result["id"] == "trans_failed_987"
    assert result["success"] is False
    assert result["amount_charged"] == 0


def test_load_object_to_json_types():
    transaction = Transaction(
        id="12345",
        success=True,
        amount_charged=9999999
    )

    result = transaction.load_object_to_json()

    assert isinstance(result["id"], str)
    assert isinstance(result["success"], bool)
    assert isinstance(result["amount_charged"], int)


def test_from_dict_and_load_object_to_json():
    initial_data = {
        "id": "trans_test_456",
        "success": True,
        "amount_charged": 2000
    }

    transaction = Transaction.from_dict(initial_data)

    result = transaction.load_object_to_json()

    assert result == initial_data, \
        "Les données après from_dict et load_object_to_json devraient être identiques"


def test_load_object_to_json_large_values():
    large_transaction = Transaction(
        id="trans_" + "9" * 50,
        success=True,
        amount_charged=1000000000
    )

    result = large_transaction.load_object_to_json()

    assert len(result["id"]) == 56
    assert result["amount_charged"] == 1000000000


def test_load_object_to_json_special_characters():
    transaction = Transaction(
        id="trans_special-#@&_123",
        success=True,
        amount_charged=1000
    )

    result = transaction.load_object_to_json()

    assert result["id"] == "trans_special-#@&_123"
    assert isinstance(result["id"], str)


def test_from_dict_with_missing_values():
    incomplete_data = {
        "id": "trans_incomplete"
    }

    transaction = Transaction.from_dict(incomplete_data)
    result = transaction.load_object_to_json()

    assert result["id"] == "trans_incomplete"
    assert result["success"] is None
    assert result["amount_charged"] is None
