"""Прокатный транспорт. Новый вид = новый наследник Vehicle."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from vyshkat.domain.validation import require_name, require_positive, require_scale


@dataclass(frozen=True)
class Vehicle(ABC):
    """Транспорт без инвентарного номера: номер выдаётся только при приёмке."""

    name: str
    simplicity: int  # простота для новичка, 1–10
    condition: int  # техническое состояние, 1–10

    @property
    @abstractmethod
    def kind(self) -> str:
        """Вид транспорта для вывода пользователю."""

    def __post_init__(self) -> None:
        require_name(self.name)
        require_scale("простота", self.simplicity)
        require_scale("состояние", self.condition)


@dataclass(frozen=True)
class Scooter(Vehicle):
    """Электросамокат."""

    daily_energy_kwh: float
    kind: ClassVar[str] = "Электросамокат"

    def __post_init__(self) -> None:
        super().__post_init__()
        require_positive("суточный расход", self.daily_energy_kwh)


@dataclass(frozen=True)
class EBike(Vehicle):
    """Электровелосипед."""

    daily_energy_kwh: float
    kind: ClassVar[str] = "Электровелосипед"

    def __post_init__(self) -> None:
        super().__post_init__()
        require_positive("суточный расход", self.daily_energy_kwh)


@dataclass(frozen=True)
class Bicycle(Vehicle):
    """Обычный велосипед: энергию не потребляет, поэтому не EnergyConsumer."""

    kind: ClassVar[str] = "Велосипед"
