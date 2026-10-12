"""Выдача инвентарных номеров: одна серия на технику и вещи."""


class InventoryNumberGenerator:
    def __init__(self) -> None:
        self._last = 0

    def next_number(self) -> str:
        self._last += 1
        return f"INV-{self._last:04d}"
