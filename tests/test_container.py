from fakes import FakeServiceCenter

from vyshkat.container import build_container
from vyshkat.domain.things import Helmet
from vyshkat.domain.vehicles import Scooter
from vyshkat.services.acceptance import AcceptanceService, Accepted, Rejected
from vyshkat.services.reports import FleetReports
from vyshkat.services.service_center import ConditionServiceCenter, ServiceCenter, Verdict


def scooter(condition: int) -> Scooter:
    return Scooter("Ninebot", 7, condition, 0.4)


def test_default_service_center_checks_condition() -> None:
    container = build_container()

    service_center: ServiceCenter = container.resolve(ServiceCenter)
    acceptance = container.resolve(AcceptanceService)

    assert isinstance(service_center, ConditionServiceCenter)
    assert isinstance(acceptance.accept_vehicle(scooter(condition=2)), Rejected)


def test_service_center_is_replaced_through_container() -> None:
    container = build_container()
    fake = FakeServiceCenter(Verdict(False, "фейк отклоняет всё"))
    container.register(ServiceCenter, instance=fake)

    result = container.resolve(AcceptanceService).accept_vehicle(scooter(condition=10))

    assert result == Rejected("фейк отклоняет всё")
    assert len(fake.inspected) == 1


def test_acceptance_and_reports_share_one_fleet() -> None:
    container = build_container()
    acceptance = container.resolve(AcceptanceService)

    vehicle_result = acceptance.accept_vehicle(scooter(condition=9))
    acceptance.add_thing(Helmet("Шлем M"))

    assert isinstance(vehicle_result, Accepted)
    assert container.resolve(FleetReports).unit_counts().total == 2


def test_numbers_continue_across_resolved_services() -> None:
    container = build_container()

    first = container.resolve(AcceptanceService).add_thing(Helmet("Шлем M"))
    second = container.resolve(AcceptanceService).add_thing(Helmet("Шлем L"))

    assert (first.item.number, second.item.number) == ("INV-0001", "INV-0002")
