import math
from dataclasses import FrozenInstanceError

import pytest

from vyshkat.domain.errors import DomainError
from vyshkat.domain.things import ChargingCabinet, DockStation, Helmet, Thing


def test_thing_is_abstract() -> None:
    with pytest.raises(TypeError):
        Thing("Без вида")  # type: ignore[abstract]


@pytest.mark.parametrize("name", ["", "   "])
def test_blank_name_is_rejected(name: str) -> None:
    with pytest.raises(DomainError, match="наименование"):
        Helmet(name)


@pytest.mark.parametrize("thing_type", [DockStation, ChargingCabinet])
@pytest.mark.parametrize("energy", [0, -1.0, math.nan, math.inf])
def test_invalid_energy_is_rejected(
    thing_type: type[DockStation | ChargingCabinet], energy: float
) -> None:
    with pytest.raises(DomainError, match="суточный расход"):
        thing_type("Оборудование", energy)


def test_thing_is_immutable() -> None:
    helmet = Helmet("Шлем M")

    with pytest.raises(FrozenInstanceError):
        helmet.name = "Шлем L"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("thing", "kind"),
    [
        (Helmet("Шлем M"), "Шлем"),
        (DockStation("Док у корпуса", 1.2), "Док-станция"),
        (ChargingCabinet("Шкаф на Покровке", 3.5), "Зарядный шкаф"),
    ],
)
def test_each_thing_has_its_kind(thing: Thing, kind: str) -> None:
    assert thing.kind == kind
