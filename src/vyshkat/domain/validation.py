"""Проверки инвариантов, общие для доменных классов."""

import math

from vyshkat.domain.errors import DomainError

SCALE_MIN = 1
SCALE_MAX = 10


def require_name(name: str) -> None:
    if not name.strip():
        raise DomainError("наименование не может быть пустым")


def require_scale(field: str, value: int) -> None:
    if not SCALE_MIN <= value <= SCALE_MAX:
        raise DomainError(f"{field}: ожидается от {SCALE_MIN} до {SCALE_MAX}, получено {value}")


def require_positive(field: str, value: float) -> None:
    # isfinite отсекает nan и бесконечность
    if not math.isfinite(value) or value <= 0:
        raise DomainError(f"{field}: ожидается конечное число больше нуля, получено {value}")
