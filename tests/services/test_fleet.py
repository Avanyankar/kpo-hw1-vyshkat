import pytest

from vyshkat.domain.inventory import InventoryItem
from vyshkat.domain.things import Helmet
from vyshkat.domain.vehicles import Bicycle
from vyshkat.services.fleet import Fleet


def test_new_fleet_is_empty() -> None:
    assert Fleet().items() == ()


def test_items_keep_registration_order() -> None:
    fleet = Fleet()
    first = InventoryItem("INV-0002", Bicycle("Stels", 9, 6))
    second = InventoryItem("INV-0001", Helmet("Шлем M"))

    fleet.add(first)
    fleet.add(second)

    assert fleet.items() == (first, second)


def test_duplicate_number_is_rejected() -> None:
    fleet = Fleet()
    fleet.add(InventoryItem("INV-0001", Helmet("Шлем M")))

    with pytest.raises(ValueError, match="INV-0001 уже занят"):
        fleet.add(InventoryItem("INV-0001", Helmet("Шлем L")))

    assert len(fleet.items()) == 1
