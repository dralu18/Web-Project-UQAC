import pytest
from session_Part.Models.CreditCard import CreditCard


def test_load_object_to_json():
    # Arrangement
    carte = CreditCard(
        name="John Doe",
        first_digits=4532,
        last_digits=1234,
        expiration_year=2025,
        expiration_month=12
    )

    # Action
    resultat = carte.load_object_to_json()

    # Assertions
    assert isinstance(resultat, dict), "Le résultat devrait être un dictionnaire"
    assert resultat["name"] == "John Doe"
    assert resultat["first_digits"] == 4532
    assert resultat["last_digits"] == 1234
    assert resultat["expiration_year"] == 2025
    assert resultat["expiration_month"] == 12
    assert len(resultat) == 5, "Le dictionnaire devrait avoir exactement 5 clés"

    # Vérification des clés attendues
    cles_attendues = {
        "name",
        "first_digits",
        "last_digits",
        "expiration_year",
        "expiration_month"
    }
    assert set(resultat.keys()) == cles_attendues, "Les clés ne correspondent pas aux attributs attendus"


def test_load_object_to_json_types():
    # Arrangement
    carte = CreditCard(
        name="Jane Doe",
        first_digits=4111,
        last_digits=5678,
        expiration_year=2026,
        expiration_month=1
    )

    # Action
    resultat = carte.load_object_to_json()

    # Assertions des types
    assert isinstance(resultat["name"], str), "Le nom devrait être une chaîne de caractères"
    assert isinstance(resultat["first_digits"], int), "first_digits devrait être un entier"
    assert isinstance(resultat["last_digits"], int), "last_digits devrait être un entier"
    assert isinstance(resultat["expiration_year"], int), "expiration_year devrait être un entier"
    assert isinstance(resultat["expiration_month"], int), "expiration_month devrait être un entier"
