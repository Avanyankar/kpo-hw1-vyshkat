"""Приёмка на баланс: транспорт через техосмотр, вещи без него."""

from dataclasses import dataclass

from vyshkat.domain.inventory import Asset, InventoryItem
from vyshkat.domain.things import Thing
from vyshkat.domain.vehicles import Vehicle
from vyshkat.services.fleet import Fleet
from vyshkat.services.numbering import InventoryNumberGenerator
from vyshkat.services.service_center import ServiceCenter


@dataclass(frozen=True)
class Accepted:
    item: InventoryItem


@dataclass(frozen=True)
class Rejected:
    reason: str


type AcceptanceResult = Accepted | Rejected


class AcceptanceService:
    def __init__(
        self,
        service_center: ServiceCenter,
        numbers: InventoryNumberGenerator,
        fleet: Fleet,
    ) -> None:
        self._service_center = service_center
        self._numbers = numbers
        self._fleet = fleet

    def accept_vehicle(self, vehicle: Vehicle) -> AcceptanceResult:
        verdict = self._service_center.inspect(vehicle)
        if not verdict.accepted:
            # Номер не выдаётся: отклонённый транспорт на баланс не попадает.
            return Rejected(verdict.reason)
        return Accepted(self._register(vehicle))

    def add_thing(self, thing: Thing) -> Accepted:
        return Accepted(self._register(thing))

    def _register(self, asset: Asset) -> InventoryItem:
        item = InventoryItem(self._numbers.next_number(), asset)
        self._fleet.add(item)
        return item
