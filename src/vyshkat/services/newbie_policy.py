"""Правило выдачи техники новичкам."""

from vyshkat.domain.validation import require_scale
from vyshkat.domain.vehicles import Vehicle


class NewbiePolicy:
    """Подходит транспорт с простотой не ниже порога.

    Интерфейса нет: реализация одна. Правило меняется здесь, отчёты не трогаются.
    """

    def __init__(self, min_simplicity: int = 6) -> None:
        require_scale("порог простоты", min_simplicity)
        self._min_simplicity = min_simplicity

    def is_suitable(self, vehicle: Vehicle) -> bool:
        return vehicle.simplicity >= self._min_simplicity
