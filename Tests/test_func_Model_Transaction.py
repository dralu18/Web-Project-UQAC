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
    # Test d'une transaction réussie
    result = sample_transaction.load_object_to_json()

    # Vérification du type de retour
    assert isinstance(result, dict), "Le résultat devrait être un dictionnaire"

    # Vérification des valeurs
    assert result["id"] == "trans_123456789"
    assert result["success"] is True
    assert result["amount_charged"] == 1500

    # Vérification du nombre de clés
    assert len(result) == 3, "Le dictionnaire devrait avoir exactement 3 clés"

    # Vérification des clés attendues
    expected_keys = {"id", "success", "amount_charged"}
    assert set(result.keys()) == expected_keys, "Les clés ne correspondent pas aux attributs attendus"


def test_load_object_to_json_failed_transaction():
    # Test d'une transaction échouée
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
    # Test des types de données
    transaction = Transaction(
        id="12345",  # ID numérique comme string
        success=True,
        amount_charged=9999999  # Grand montant
    )

    result = transaction.load_object_to_json()

    # Vérification des types
    assert isinstance(result["id"], str)
    assert isinstance(result["success"], bool)
    assert isinstance(result["amount_charged"], int)


def test_from_dict_and_load_object_to_json():
    # Test de l'intégration entre from_dict et load_object_to_json
    initial_data = {
        "id": "trans_test_456",
        "success": True,
        "amount_charged": 2000
    }

    # Création d'un objet via from_dict
    transaction = Transaction.from_dict(initial_data)

    # Conversion en JSON
    result = transaction.load_object_to_json()

    # Vérification que les données sont identiques
    assert result == initial_data, \
        "Les données après from_dict et load_object_to_json devraient être identiques"


def test_load_object_to_json_large_values():
    # Test avec des valeurs extrêmes
    large_transaction = Transaction(
        id="trans_" + "9" * 50,  # ID très long
        success=True,
        amount_charged=1000000000  # Montant très élevé
    )

    result = large_transaction.load_object_to_json()

    assert len(result["id"]) == 56
    assert result["amount_charged"] == 1000000000


def test_load_object_to_json_special_characters():
    # Test avec des caractères spéciaux dans l'ID
    transaction = Transaction(
        id="trans_special-#@&_123",
        success=True,
        amount_charged=1000
    )

    result = transaction.load_object_to_json()

    assert result["id"] == "trans_special-#@&_123"
    assert isinstance(result["id"], str)


def test_from_dict_with_missing_values():
    # Test de from_dict avec des valeurs manquantes
    incomplete_data = {
        "id": "trans_incomplete"
        # success et amount_charged manquants
    }

    transaction = Transaction.from_dict(incomplete_data)
    result = transaction.load_object_to_json()

    assert result["id"] == "trans_incomplete"
    assert result["success"] is None
    assert result["amount_charged"] is None
