"""Инвентарная запись: единственное место, где у актива есть номер."""

from dataclasses import dataclass

from vyshkat.domain.errors import DomainError
from vyshkat.domain.things import Thing
from vyshkat.domain.vehicles import Vehicle

type Asset = Vehicle | Thing


@dataclass(frozen=True)
class InventoryItem:
    """Актив, принятый на баланс. Реализует Inventoried."""

    number: str
    asset: Asset

    def __post_init__(self) -> None:
        if not self.number.strip():
            raise DomainError("инвентарный номер не может быть пустым")

    @property
    def kind(self) -> str:
        return self.asset.kind

    @property
    def name(self) -> str:
        return self.asset.name
