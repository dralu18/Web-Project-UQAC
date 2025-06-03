import pytest
from session_Part.Models.Product import Product


@pytest.fixture
def sample_product():
    return Product(
        id=1,
        name="Test Product",
        weight=100,  # poids de base pour les tests
        price=1000,
        in_stock=True
    )


def test_calculate_weight_light_package(sample_product):
    # Test pour un colis léger (poids total <= 500g)
    quantities = [1, 2, 3, 4, 5]  # 100g * 5 = 500g
    for quantity in quantities:
        assert sample_product.calculate_weight(quantity) == 500, \
            f"Pour un poids de {sample_product.weight * quantity}g (quantity={quantity}), " \
            f"les frais de port devraient être de 500"


def test_calculate_weight_medium_package(sample_product):
    # Test pour un colis moyen (500g < poids total <= 2000g)
    sample_product.weight = 250  # 250g par unité
    quantities = [3, 4, 5, 6, 7, 8]  # 750g à 2000g
    for quantity in quantities:
        assert sample_product.calculate_weight(quantity) == 1000, \
            f"Pour un poids de {sample_product.weight * quantity}g (quantity={quantity}), " \
            f"les frais de port devraient être de 1000"


def test_calculate_weight_heavy_package(sample_product):
    # Test pour un colis lourd (poids total > 2000g)
    sample_product.weight = 500  # 500g par unité
    quantities = [5, 6, 7, 8, 9, 10]  # 2500g à 5000g
    for quantity in quantities:
        assert sample_product.calculate_weight(quantity) == 2500, \
            f"Pour un poids de {sample_product.weight * quantity}g (quantity={quantity}), " \
            f"les frais de port devraient être de 2500"


def test_calculate_weight_edge_cases(sample_product):
    # Test des cas limites

    # Cas limite à 500g exactement
    sample_product.weight = 500
    assert sample_product.calculate_weight(1) == 500, "Pour 500g exactement, les frais devraient être de 500"

    # Cas limite à 2000g exactement
    sample_product.weight = 1000
    assert sample_product.calculate_weight(2) == 1000, "Pour 2000g exactement, les frais devraient être de 1000"

    # Juste au-dessus de 500g
    sample_product.weight = 501
    assert sample_product.calculate_weight(1) == 1000, "Pour 501g, les frais devraient être de 1000"

    # Juste au-dessus de 2000g
    sample_product.weight = 2001
    assert sample_product.calculate_weight(1) == 2500, "Pour 2001g, les frais devraient être de 2500"


def test_calculate_weight_invalid_quantity(sample_product):
    # Test avec des quantités invalides
    with pytest.raises(TypeError):
        sample_product.calculate_weight("1")  # Test avec une chaîne

    with pytest.raises(TypeError):
        sample_product.calculate_weight(None)  # Test avec None

    with pytest.raises(TypeError):
        sample_product.calculate_weight(1.5)  # Test avec un float


def test_calculate_weight_zero_or_negative(sample_product):
    # Test avec quantité zéro ou négative
    assert sample_product.calculate_weight(0) == 500, "Pour une quantité de 0, les frais devraient être de 500"
    assert sample_product.calculate_weight(-1) == 500, "Pour une quantité négative, les frais devraient être de 500"