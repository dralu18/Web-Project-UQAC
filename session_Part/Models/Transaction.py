from peewee import *
from Models.BaseModel import BaseModel

class Transaction(BaseModel):
    id = CharField(unique=True)
    success = BooleanField()
    amount_charged = IntegerField()

    @classmethod
    def from_dict(cls, transaction_info: dict):
        return cls(
            id = transaction_info.get("id"),
            success=transaction_info.get("success"),
            amount_charged=transaction_info.get("amount_charged")
        )

    def load_object_to_json(self):
        return {
            "id": self.id,
            "success": self.success,
            "amount_charged": self.amount_charged
        }
