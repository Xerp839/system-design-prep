from typing import Dict, Optional

from domain.receipt import Receipt


class ReceiptRepository:
    def __init__(self):
        self._receipts: Dict[str, Receipt] = {}

    def save(self, receipt: Receipt) -> Receipt:
        self._receipts[receipt.id] = receipt
        return receipt

    def find_by_id(self, receipt_id: str) -> Optional[Receipt]:
        return self._receipts.get(receipt_id)
