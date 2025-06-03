import pytest
from session_Part.Models.Shipping_information import Shipping_information


@pytest.fixture
def sample_shipping_info():
    return Shipping_information(
        country="Canada",
        address="123 Rue Test",
        postal_code="G7X 2B2",
        city="Chicoutimi",
        province="QC"
    )


def test_load_object_to_json_complete(sample_shipping_info):
    # Test avec toutes les informations remplies
    result = sample_shipping_info.load_object_to_json()

    # Vérification du type de retour
    assert isinstance(result, dict), "Le résultat devrait être un dictionnaire"

    # Vérification des valeurs
    assert result["country"] == "Canada"
    assert result["address"] == "123 Rue Test"
    assert result["postal_code"] == "G7X 2B2"
    assert result["city"] == "Chicoutimi"
    assert result["province"] == "QC"

    # Vérification du nombre de clés
    assert len(result) == 5, "Le dictionnaire devrait avoir exactement 5 clés"

    # Vérification des clés attendues
    expected_keys = {"country", "address", "postal_code", "city", "province"}
    assert set(result.keys()) == expected_keys, "Les clés ne correspondent pas aux attributs attendus"


def test_load_object_to_json_empty():
    # Test avec un objet vide
    empty_shipping = Shipping_information()
    result = empty_shipping.load_object_to_json()

    # Vérification que toutes les valeurs sont None
    assert all(value is None for value in result.values()), \
        "Toutes les valeurs devraient être None pour un objet vide"

    # Vérification que toutes les clés existent
    expected_keys = {"country", "address", "postal_code", "city", "province"}
    assert set(result.keys()) == expected_keys, \
        "Toutes les clés devraient être présentes même pour un objet vide"


def test_load_object_to_json_partial():
    # Test avec seulement certaines informations remplies
    partial_shipping = Shipping_information(
        country="Canada",
        city="Montreal",
        province="QC"
    )

    result = partial_shipping.load_object_to_json()

    # Vérification des valeurs remplies
    assert result["country"] == "Canada"
    assert result["city"] == "Montreal"
    assert result["province"] == "QC"

    # Vérification des valeurs non remplies
    assert result["address"] is None
    assert result["postal_code"] is None


def test_load_object_to_json_types():
    # Test avec différents types de données
    shipping = Shipping_information(
        country="Canada",
        address="123",  # Numérique sous forme de string
        postal_code="12345",
        city="Ville-Test",  # Avec trait d'union
        province="QC"
    )

    result = shipping.load_object_to_json()

    # Vérification des types
    assert isinstance(result["country"], (str, type(None)))
    assert isinstance(result["address"], (str, type(None)))
    assert isinstance(result["postal_code"], (str, type(None)))
    assert isinstance(result["city"], (str, type(None)))
    assert isinstance(result["province"], (str, type(None)))


def test_load_object_to_json_special_characters():
    # Test avec des caractères spéciaux
    shipping = Shipping_information(
        country="États-Unis",
        address="123 Première Avenue, App. #4",
        postal_code="H2X 1Y6",
        city="Saint-Jérôme",
        province="QC"
    )

    result = shipping.load_object_to_json()

    # Vérification que les caractères spéciaux sont préservés
    assert result["country"] == "États-Unis"
    assert result["address"] == "123 Première Avenue, App. #4"
    assert result["city"] == "Saint-Jérôme"


def test_from_dict_and_load_object_to_json():
    # Test de l'intégration entre from_dict et load_object_to_json
    initial_data = {
        "country": "Canada",
        "address": "456 Main St",
        "postal_code": "A1B 2C3",
        "city": "Toronto",
        "province": "ON"
    }

    # Création d'un objet via from_dict
    shipping = Shipping_information.from_dict(initial_data)

    # Conversion en JSON
    result = shipping.load_object_to_json()

    # Vérification que les données sont identiques
    assert result == initial_data, \
        "Les données après from_dict et load_object_to_json devraient être identiques"
