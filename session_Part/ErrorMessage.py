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

Error422OneOrMoreMissingField = {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires"
                }
            }
        }, 422

Error422CanNotGiveCardAndShippingInfoOrEmail = {
                "errors": {
                    "order": {
                        "code": "missing-fields",
                        "name": "On ne peut pas fournir credit_card avec shipping_information et/ou email"
                    }
                }
            }, 422

Error422OrderAlreadyBuy = {
                "errors": {
                    "order": {
                        "code": "already-paid",
                        "name": "La commande a déjà été payée."
                    }
                }
            }, 422

Error422NeedShippingInfoBeforCreditCard = {
                "errors": {
                    "order": {
                        "code": "missing-fields",
                        "name": "Les informations du client sont nécessaires avant d'appliquer une carte de crédit"
                    }
                }
            }, 422

Error422NonCompliantFields = {
                "errors": {
                    "order": {
                        "code": "missing-fields",
                        "name": "Champs non conform"
                    }
                }
            }, 422

Error422InvalidEmailformat = {
              "error": "Invalid email format",
              "field": "email"
            }, 422

Error422Invalidprovincevalue = {
                "error": "Invalid province value",
                "field": "province",
                "allowed_values": ["QC", "ON", "AB", "BC", "NS"]
            }, 422