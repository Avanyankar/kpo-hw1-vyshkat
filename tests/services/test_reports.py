import pytest

from vyshkat.domain.inventory import Asset, InventoryItem
from vyshkat.domain.things import ChargingCabinet, Helmet
from vyshkat.domain.vehicles import Bicycle, EBike, Scooter
from vyshkat.services.fleet import Fleet
from vyshkat.services.newbie_policy import NewbiePolicy
from vyshkat.services.reports import FleetReports, UnitCounts

EASY_SCOOTER = Scooter("Ninebot", 7, 8, 0.4)
HARD_EBIKE = EBike("Eltreco", 4, 9, 0.9)
EASY_BICYCLE = Bicycle("Stels", 9, 6)
HELMET = Helmet("Шлем M")
CABINET = ChargingCabinet("Шкаф на Покровке", 3.5)


def fleet_of(*assets: Asset) -> Fleet:
    fleet = Fleet()
    for index, asset in enumerate(assets, start=1):
        fleet.add(InventoryItem(f"INV-{index:04d}", asset))
    return fleet


def reports_for(fleet: Fleet, policy: NewbiePolicy | None = None) -> FleetReports:
    return FleetReports(fleet, policy or NewbiePolicy())


def test_empty_fleet_reports_nothing() -> None:
    reports = reports_for(Fleet())

    assert reports.unit_counts() == UnitCounts(total=0, vehicles=0, things=0, by_kind={})
    assert reports.total_daily_energy_kwh() == 0
    assert reports.newbie_vehicles() == ()
    assert reports.inventory() == ()


def test_unit_counts_split_by_category_and_kind() -> None:
    reports = reports_for(fleet_of(EASY_SCOOTER, HELMET, Scooter("Kugoo", 6, 7, 0.5), HELMET))

    assert reports.unit_counts() == UnitCounts(
        total=4,
        vehicles=2,
        things=2,
        by_kind={"Электросамокат": 2, "Шлем": 2},
    )


def test_unit_counts_by_kind_is_read_only() -> None:
    counts = reports_for(fleet_of(HELMET)).unit_counts()

    with pytest.raises(TypeError):
        counts.by_kind["Шлем"] = 100  # type: ignore[index]


def test_energy_sums_only_energy_consumers() -> None:
    reports = reports_for(fleet_of(EASY_SCOOTER, HARD_EBIKE, EASY_BICYCLE, HELMET, CABINET))

    assert reports.total_daily_energy_kwh() == pytest.approx(0.4 + 0.9 + 3.5)


def test_newbie_vehicles_follow_policy_and_skip_things() -> None:
    fleet = fleet_of(EASY_SCOOTER, HARD_EBIKE, EASY_BICYCLE, HELMET)

    newbie = reports_for(fleet).newbie_vehicles()

    assert [item.asset for item in newbie] == [EASY_SCOOTER, EASY_BICYCLE]


def test_newbie_vehicles_use_injected_policy() -> None:
    fleet = fleet_of(EASY_SCOOTER, EASY_BICYCLE)

    newbie = reports_for(fleet, NewbiePolicy(min_simplicity=8)).newbie_vehicles()

    assert [item.asset for item in newbie] == [EASY_BICYCLE]


def test_inventory_lists_number_kind_and_name_of_everything() -> None:
    reports = reports_for(fleet_of(EASY_SCOOTER, HELMET, CABINET))

    listing = [(entry.number, entry.kind, entry.name) for entry in reports.inventory()]

    assert listing == [
        ("INV-0001", "Электросамокат", "Ninebot"),
        ("INV-0002", "Шлем", "Шлем M"),
        ("INV-0003", "Зарядный шкаф", "Шкаф на Покровке"),
    ]
