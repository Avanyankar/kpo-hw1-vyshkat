import math
from collections.abc import Callable
from dataclasses import FrozenInstanceError

import pytest

from vyshkat.domain.errors import DomainError
from vyshkat.domain.vehicles import Bicycle, EBike, Scooter, Vehicle

type VehicleFactory = Callable[[str, int, int], Vehicle]

# Общие для всего транспорта правила проверяем на каждом виде.
FACTORIES: dict[str, VehicleFactory] = {
    "scooter": lambda name, simplicity, condition: Scooter(name, simplicity, condition, 0.4),
    "ebike": lambda name, simplicity, condition: EBike(name, simplicity, condition, 0.9),
    "bicycle": lambda name, simplicity, condition: Bicycle(name, simplicity, condition),
}
each_kind = pytest.mark.parametrize("make", FACTORIES.values(), ids=FACTORIES.keys())


def test_vehicle_is_abstract() -> None:
    with pytest.raises(TypeError):
        Vehicle("Без вида", 5, 5)  # type: ignore[abstract]


@each_kind
@pytest.mark.parametrize("value", [1, 10])
def test_scale_bounds_are_accepted(make: VehicleFactory, value: int) -> None:
    vehicle = make("Транспорт", value, value)

    assert (vehicle.simplicity, vehicle.condition) == (value, value)


@each_kind
@pytest.mark.parametrize("simplicity", [0, 11])
def test_simplicity_out_of_scale_is_rejected(make: VehicleFactory, simplicity: int) -> None:
    with pytest.raises(DomainError, match="простота"):
        make("Транспорт", simplicity, 5)


@each_kind
@pytest.mark.parametrize("condition", [0, 11])
def test_condition_out_of_scale_is_rejected(make: VehicleFactory, condition: int) -> None:
    with pytest.raises(DomainError, match="состояние"):
        make("Транспорт", 5, condition)


@each_kind
@pytest.mark.parametrize("name", ["", "   "])
def test_blank_name_is_rejected(make: VehicleFactory, name: str) -> None:
    with pytest.raises(DomainError, match="наименование"):
        make(name, 5, 5)


@pytest.mark.parametrize("vehicle_type", [Scooter, EBike])
@pytest.mark.parametrize("energy", [0, -0.5, math.nan, math.inf])
def test_invalid_energy_is_rejected(vehicle_type: type[Scooter | EBike], energy: float) -> None:
    with pytest.raises(DomainError, match="суточный расход"):
        vehicle_type("Электро", 5, 5, energy)


def test_vehicle_is_immutable() -> None:
    scooter = Scooter("Ninebot", 7, 8, 0.4)

    with pytest.raises(FrozenInstanceError):
        scooter.condition = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    ("vehicle", "kind"),
    [
        (Scooter("Ninebot", 7, 8, 0.4), "Электросамокат"),
        (EBike("Eltreco", 5, 9, 0.9), "Электровелосипед"),
        (Bicycle("Stels", 9, 6), "Велосипед"),
    ],
)
def test_each_vehicle_has_its_kind(vehicle: Vehicle, kind: str) -> None:
    assert vehicle.kind == kind
