"""Проверки инвариантов, общие для доменных классов."""

SCALE_MIN = 1
SCALE_MAX = 10


def require_name(name: str) -> None:
    if not name.strip():
        raise ValueError("наименование не может быть пустым")


def require_scale(field: str, value: int) -> None:
    if not SCALE_MIN <= value <= SCALE_MAX:
        raise ValueError(f"{field}: ожидается от {SCALE_MIN} до {SCALE_MAX}, получено {value}")


def require_positive(field: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{field}: ожидается число больше нуля, получено {value}")
