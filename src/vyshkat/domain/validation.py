"""Проверки инвариантов, общие для доменных классов.

attribute — имя атрибута в коде (уходит в DomainError.attribute), label — его название
для сообщения пользователю.
"""

import math

from vyshkat.domain.errors import DomainError

SCALE_MIN = 1
SCALE_MAX = 10


def require_name(name: str) -> None:
    if not name.strip():
        raise DomainError("наименование не может быть пустым", "name")


def require_scale(attribute: str, label: str, value: int) -> None:
    if not SCALE_MIN <= value <= SCALE_MAX:
        raise DomainError(
            f"{label}: ожидается от {SCALE_MIN} до {SCALE_MAX}, получено {value}", attribute
        )


def require_positive(attribute: str, label: str, value: float) -> None:
    # isfinite отсекает nan и бесконечность
    if not math.isfinite(value) or value <= 0:
        raise DomainError(
            f"{label}: ожидается конечное число больше нуля, получено {value}", attribute
        )
