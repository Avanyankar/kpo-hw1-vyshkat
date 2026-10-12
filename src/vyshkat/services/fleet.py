"""Парк: всё, что стоит на балансе."""

from vyshkat.domain.inventory import InventoryItem


class Fleet:
    def __init__(self) -> None:
        self._items: dict[str, InventoryItem] = {}

    def add(self, item: InventoryItem) -> None:
        if item.number in self._items:
            raise ValueError(f"инвентарный номер {item.number} уже занят")
        self._items[item.number] = item

    def items(self) -> tuple[InventoryItem, ...]:
        """Записи в порядке постановки на баланс."""
        return tuple(self._items.values())
