"""Техосмотр: решает, принимать ли транспорт в парк."""

from dataclasses import dataclass
from typing import Protocol

from vyshkat.domain.validation import SCALE_MAX, require_scale
from vyshkat.domain.vehicles import Vehicle


@dataclass(frozen=True)
class Verdict:
    accepted: bool
    reason: str


class ServiceCenter(Protocol):
    """Подставляется через DI; в тестах заменяется фейком."""

    def inspect(self, vehicle: Vehicle) -> Verdict: ...


class ConditionServiceCenter:
    """Принимает транспорт, если его техсостояние не ниже порога."""

    def __init__(self, min_condition: int = 5) -> None:
        require_scale("min_condition", "порог состояния", min_condition)
        self._min_condition = min_condition

    def inspect(self, vehicle: Vehicle) -> Verdict:
        condition = f"состояние {vehicle.condition}/{SCALE_MAX}"
        if vehicle.condition >= self._min_condition:
            return Verdict(True, f"{condition}, порог {self._min_condition}")
        return Verdict(False, f"{condition} ниже порога {self._min_condition}")
