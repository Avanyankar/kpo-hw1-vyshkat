from fakes import FakeServiceCenter

from vyshkat.domain.inventory import InventoryItem
from vyshkat.domain.things import Helmet
from vyshkat.domain.vehicles import Scooter
from vyshkat.services.acceptance import AcceptanceService, Accepted, Rejected
from vyshkat.services.fleet import Fleet
from vyshkat.services.numbering import InventoryNumberGenerator
from vyshkat.services.service_center import Verdict

APPROVE = Verdict(True, "годен")
DECLINE = Verdict(False, "тормоза неисправны")


def make_service(verdict: Verdict) -> tuple[AcceptanceService, FakeServiceCenter, Fleet]:
    service_center = FakeServiceCenter(verdict)
    fleet = Fleet()
    service = AcceptanceService(service_center, InventoryNumberGenerator(), fleet)
    return service, service_center, fleet


def scooter() -> Scooter:
    return Scooter("Ninebot", 7, 8, 0.4)


def test_vehicle_goes_through_inspection() -> None:
    service, service_center, _ = make_service(APPROVE)
    vehicle = scooter()

    service.accept_vehicle(vehicle)

    assert service_center.inspected == [vehicle]


def test_approved_vehicle_gets_number_and_joins_fleet() -> None:
    service, _, fleet = make_service(APPROVE)
    vehicle = scooter()

    result = service.accept_vehicle(vehicle)

    expected = InventoryItem("INV-0001", vehicle)
    assert result == Accepted(expected)
    assert fleet.items() == (expected,)


def test_declined_vehicle_stays_off_balance_with_reason() -> None:
    service, _, fleet = make_service(DECLINE)

    result = service.accept_vehicle(scooter())

    assert result == Rejected("тормоза неисправны")
    assert fleet.items() == ()


def test_declined_vehicle_does_not_burn_a_number() -> None:
    service, service_center, _ = make_service(DECLINE)
    service.accept_vehicle(scooter())

    service_center.verdict = APPROVE
    result = service.accept_vehicle(scooter())

    assert isinstance(result, Accepted)
    assert result.item.number == "INV-0001"


def test_thing_is_added_without_inspection() -> None:
    service, service_center, fleet = make_service(DECLINE)
    helmet = Helmet("Шлем M")

    result = service.add_thing(helmet)

    assert service_center.inspected == []
    assert result == Accepted(InventoryItem("INV-0001", helmet))
    assert fleet.items() == (result.item,)


def test_vehicles_and_things_share_one_number_series() -> None:
    service, _, fleet = make_service(APPROVE)

    service.accept_vehicle(scooter())
    service.add_thing(Helmet("Шлем M"))

    assert [item.number for item in fleet.items()] == ["INV-0001", "INV-0002"]
