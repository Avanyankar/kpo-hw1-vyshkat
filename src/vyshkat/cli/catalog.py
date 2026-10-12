"""Каталог видов: имя в команде -> фабрика объекта."""

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from vyshkat.cli.errors import CommandError
from vyshkat.domain.errors import DomainError
from vyshkat.domain.things import ChargingCabinet, DockStation, Helmet, Thing
from vyshkat.domain.vehicles import Bicycle, EBike, Scooter, Vehicle

# Атрибут доменного объекта -> ключ параметра в команде.
PARAM_FOR_ATTRIBUTE: Mapping[str, str] = MappingProxyType(
    {"simplicity": "simplicity", "condition": "condition", "daily_energy_kwh": "energy"}
)


class Params:
    """Параметры `ключ=значение` с приведением типов и проверкой лишних ключей."""

    def __init__(self, raw: Mapping[str, str]) -> None:
        self._raw = raw
        self._used: set[str] = set()

    def get_int(self, key: str) -> int:
        raw = self._take(key)
        try:
            return int(raw)
        except ValueError:
            raise CommandError(f"{key}: ожидается целое число, получено «{raw}»") from None

    def get_float(self, key: str) -> float:
        raw = self._take(key)
        try:
            value = float(raw)
        except ValueError:
            raise CommandError(f"{key}: ожидается число через точку, получено «{raw}»") from None
        if not math.isfinite(value):
            raise CommandError(f"{key}: ожидается конечное число, получено «{raw}»")
        return value

    def ensure_all_used(self) -> None:
        extra = sorted(self._raw.keys() - self._used)
        if extra:
            raise CommandError(f"неизвестные параметры: {', '.join(extra)}")

    def _take(self, key: str) -> str:
        if key not in self._raw:
            raise CommandError(f"не указан параметр {key}")
        self._used.add(key)
        return self._raw[key]


@dataclass(frozen=True)
class Kind[T]:
    build: Callable[[str, Params], T]
    usage: str  # параметры для подсказки пользователю


VEHICLE_KINDS: Mapping[str, Kind[Vehicle]] = MappingProxyType(
    {
        "scooter": Kind(
            lambda name, p: Scooter(
                name, p.get_int("simplicity"), p.get_int("condition"), p.get_float("energy")
            ),
            "simplicity=1..10 condition=1..10 energy=кВт·ч",
        ),
        "ebike": Kind(
            lambda name, p: EBike(
                name, p.get_int("simplicity"), p.get_int("condition"), p.get_float("energy")
            ),
            "simplicity=1..10 condition=1..10 energy=кВт·ч",
        ),
        "bicycle": Kind(
            lambda name, p: Bicycle(name, p.get_int("simplicity"), p.get_int("condition")),
            "simplicity=1..10 condition=1..10",
        ),
    }
)

THING_KINDS: Mapping[str, Kind[Thing]] = MappingProxyType(
    {
        "helmet": Kind(lambda name, p: Helmet(name), ""),
        "dock": Kind(lambda name, p: DockStation(name, p.get_float("energy")), "energy=кВт·ч"),
        "cabinet": Kind(
            lambda name, p: ChargingCabinet(name, p.get_float("energy")), "energy=кВт·ч"
        ),
    }
)


def create[T](kinds: Mapping[str, Kind[T]], args: tuple[str, ...], params: Mapping[str, str]) -> T:
    """Создаёт объект по `<вид> "<название>"` и параметрам команды."""
    if not args:
        raise CommandError(f"не указан вид, доступны: {', '.join(kinds)}")
    kind_name, *rest = args
    kind = kinds.get(kind_name)
    if kind is None:
        raise CommandError(f"неизвестный вид «{kind_name}», доступны: {', '.join(kinds)}")
    if not rest:
        raise CommandError(f'не указано название: {kind_name} "<название>"')
    name, *extra = rest
    if extra:
        raise CommandError(
            f"лишние слова: {' '.join(extra)}. "
            "Название с пробелами пишется в кавычках, параметры — как ключ=значение"
        )

    checked = Params(params)
    try:
        created = kind.build(name, checked)
    except DomainError as error:
        # Домен называет атрибут по-своему; показываем его так, как его ввёл пользователь.
        param = PARAM_FOR_ATTRIBUTE.get(error.attribute or "")
        if param is None or param not in params:
            raise
        raise CommandError(f"{param}={params[param]} — {error}") from error
    checked.ensure_all_used()
    return created
