"""Отчёты по парку."""

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from vyshkat.domain.inventory import InventoryItem
from vyshkat.domain.protocols import EnergyConsumer, Inventoried
from vyshkat.domain.things import Thing
from vyshkat.domain.vehicles import Vehicle
from vyshkat.services.fleet import Fleet
from vyshkat.services.newbie_policy import NewbiePolicy


@dataclass(frozen=True)
class UnitCounts:
    total: int
    vehicles: int
    things: int
    by_kind: Mapping[str, int]  # только чтение; в порядке первого появления вида на балансе


class FleetReports:
    def __init__(self, fleet: Fleet, newbie_policy: NewbiePolicy) -> None:
        self._fleet = fleet
        self._newbie_policy = newbie_policy

    def unit_counts(self) -> UnitCounts:
        assets = [item.asset for item in self._fleet.items()]
        return UnitCounts(
            total=len(assets),
            vehicles=sum(isinstance(asset, Vehicle) for asset in assets),
            things=sum(isinstance(asset, Thing) for asset in assets),
            by_kind=MappingProxyType(dict(Counter(asset.kind for asset in assets))),
        )

    def total_daily_energy_kwh(self) -> float:
        return sum(
            item.asset.daily_energy_kwh
            for item in self._fleet.items()
            if isinstance(item.asset, EnergyConsumer)
        )

    def newbie_vehicles(self) -> tuple[InventoryItem, ...]:
        return tuple(
            item
            for item in self._fleet.items()
            if isinstance(item.asset, Vehicle) and self._newbie_policy.is_suitable(item.asset)
        )

    def inventory(self) -> tuple[Inventoried, ...]:
        """Номер, вид и наименование всей техники и вещей."""
        return self._fleet.items()
