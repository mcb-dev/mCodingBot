from __future__ import annotations

from decimal import Decimal

from apgorm import Converter


class NumericConverter(Converter[Decimal, int]):
    def from_stored(self, value: Decimal) -> int:
        return int(value)

    def to_stored(self, value: int) -> Decimal:
        return Decimal(value)
