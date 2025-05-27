Error422OrderNeedProduct = {
                "errors": {
                    "product": {
                        "code": "missing-fields",
                        "name": "La création d'une commande nécessite un produit"
                    }
                }
            }, 422
Error422OrderDoesNotExist = {
                "errors": {
                    "product": {
                        "code": "missing-fields",
                        "name": "Le produit n'existe pas"
                    }
                }
            }, 422

Error422ProductOutOfInventory = {
                "errors": {
                    "product": {
                        "code": "out-of-inventory",
                        "name": "Le produit demandé n'est pas en inventaire"
                    }
                }
            }, 422