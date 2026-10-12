import pytest

from vyshkat.domain.inventory import InventoryItem
from vyshkat.domain.protocols import Inventoried
from vyshkat.domain.things import Helmet
from vyshkat.domain.vehicles import Scooter


def test_item_takes_kind_and_name_from_its_asset() -> None:
    item = InventoryItem("INV-0001", Scooter("Ninebot", 7, 8, 0.4))

    assert (item.kind, item.name) == ("Электросамокат", "Ninebot")


@pytest.mark.parametrize("number", ["", "   "])
def test_blank_number_is_rejected(number: str) -> None:
    with pytest.raises(ValueError, match="инвентарный номер"):
        InventoryItem(number, Helmet("Шлем M"))


def test_item_satisfies_inventoried() -> None:
    # Присваивание проверяет mypy: если InventoryItem перестанет подходить
    # под протокол Inventoried, упадёт make typecheck.
    item: Inventoried = InventoryItem("INV-0002", Helmet("Шлем M"))

    assert (item.number, item.kind, item.name) == ("INV-0002", "Шлем", "Шлем M")
