"""Вещи на балансе: не транспорт, техосмотр не проходят."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from vyshkat.domain.validation import require_name, require_positive


@dataclass(frozen=True)
class Thing(ABC):
    """Вещь без инвентарного номера: номер выдаётся только при постановке на баланс."""

    name: str

    @property
    @abstractmethod
    def kind(self) -> str:
        """Вид вещи для вывода пользователю."""

    def __post_init__(self) -> None:
        require_name(self.name)


@dataclass(frozen=True)
class Helmet(Thing):
    kind: ClassVar[str] = "Шлем"


@dataclass(frozen=True)
class DockStation(Thing):
    daily_energy_kwh: float
    kind: ClassVar[str] = "Док-станция"

    def __post_init__(self) -> None:
        super().__post_init__()
        require_positive("daily_energy_kwh", "суточный расход", self.daily_energy_kwh)


@dataclass(frozen=True)
class ChargingCabinet(Thing):
    daily_energy_kwh: float
    kind: ClassVar[str] = "Зарядный шкаф"

    def __post_init__(self) -> None:
        super().__post_init__()
        require_positive("daily_energy_kwh", "суточный расход", self.daily_energy_kwh)
