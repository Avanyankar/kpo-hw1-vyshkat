import pytest

from vyshkat.domain.inventory import Asset
from vyshkat.domain.protocols import EnergyConsumer
from vyshkat.domain.things import ChargingCabinet, DockStation, Helmet
from vyshkat.domain.vehicles import Bicycle, EBike, Scooter

POWERED: list[Asset] = [
    Scooter("Ninebot", 7, 8, 0.4),
    EBike("Eltreco", 5, 9, 0.9),
    DockStation("Док у корпуса", 1.2),
    ChargingCabinet("Шкаф на Покровке", 3.5),
]
UNPOWERED: list[Asset] = [Bicycle("Stels", 9, 6), Helmet("Шлем M")]


def asset_id(asset: Asset) -> str:
    return type(asset).__name__


@pytest.mark.parametrize("asset", POWERED, ids=asset_id)
def test_powered_assets_are_energy_consumers(asset: Asset) -> None:
    assert isinstance(asset, EnergyConsumer)


@pytest.mark.parametrize("asset", UNPOWERED, ids=asset_id)
def test_unpowered_assets_are_not_energy_consumers(asset: Asset) -> None:
    assert not isinstance(asset, EnergyConsumer)
