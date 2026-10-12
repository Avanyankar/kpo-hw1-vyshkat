import pytest

from vyshkat.cli.catalog import THING_KINDS, VEHICLE_KINDS, create
from vyshkat.cli.errors import CommandError
from vyshkat.domain.errors import DomainError
from vyshkat.domain.things import ChargingCabinet, DockStation, Helmet
from vyshkat.domain.vehicles import Bicycle, EBike, Scooter

VEHICLE_PARAMS = {"simplicity": "7", "condition": "8"}


def test_creates_every_vehicle_kind() -> None:
    electric = {**VEHICLE_PARAMS, "energy": "0.4"}

    assert create(VEHICLE_KINDS, ("scooter", "Ninebot"), electric) == Scooter("Ninebot", 7, 8, 0.4)
    assert create(VEHICLE_KINDS, ("ebike", "Eltreco"), electric) == EBike("Eltreco", 7, 8, 0.4)
    assert create(VEHICLE_KINDS, ("bicycle", "Stels"), VEHICLE_PARAMS) == Bicycle("Stels", 7, 8)


def test_creates_every_thing_kind() -> None:
    energy = {"energy": "1.5"}

    assert create(THING_KINDS, ("helmet", "Шлем M"), {}) == Helmet("Шлем M")
    assert create(THING_KINDS, ("dock", "Док"), energy) == DockStation("Док", 1.5)
    assert create(THING_KINDS, ("cabinet", "Шкаф"), energy) == ChargingCabinet("Шкаф", 1.5)


def test_vehicle_kinds_and_thing_kinds_do_not_overlap() -> None:
    # Каждый вид принимается ровно одной командой: accept или add.
    assert VEHICLE_KINDS.keys().isdisjoint(THING_KINDS.keys())


def test_unknown_kind_lists_available_ones() -> None:
    with pytest.raises(CommandError, match="неизвестный вид «helmet», доступны: scooter"):
        create(VEHICLE_KINDS, ("helmet", "Шлем M"), {})


@pytest.mark.parametrize("args", [(), ("helmet",), ("helmet", "Шлем", "лишнее")])
def test_kind_and_one_name_are_required(args: tuple[str, ...]) -> None:
    with pytest.raises(CommandError, match="ожидается"):
        create(THING_KINDS, args, {})


def test_missing_param_is_reported() -> None:
    with pytest.raises(CommandError, match="не указан параметр energy"):
        create(VEHICLE_KINDS, ("scooter", "Ninebot"), VEHICLE_PARAMS)


def test_extra_param_is_reported() -> None:
    params = {**VEHICLE_PARAMS, "simplicty": "7"}

    with pytest.raises(CommandError, match="неизвестные параметры: simplicty"):
        create(VEHICLE_KINDS, ("bicycle", "Stels"), params)


@pytest.mark.parametrize("value", ["семь", "7.5"])
def test_non_integer_scale_is_reported(value: str) -> None:
    params = {**VEHICLE_PARAMS, "simplicity": value}

    with pytest.raises(CommandError, match="simplicity: ожидается целое число"):
        create(VEHICLE_KINDS, ("bicycle", "Stels"), params)


@pytest.mark.parametrize(
    ("value", "message"),
    [("0,4", "ожидается число через точку"), ("nan", "ожидается конечное число")],
)
def test_bad_energy_is_reported(value: str, message: str) -> None:
    with pytest.raises(CommandError, match=message):
        create(THING_KINDS, ("dock", "Док"), {"energy": value})


def test_domain_rules_still_apply() -> None:
    params = {**VEHICLE_PARAMS, "simplicity": "15"}

    with pytest.raises(DomainError, match="простота"):
        create(VEHICLE_KINDS, ("bicycle", "Stels"), params)
