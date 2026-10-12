"""Ошибки доменной модели."""


class DomainError(ValueError):
    """Нарушен инвариант модели: такой объект не может существовать.

    attribute — имя нарушенного атрибута (`simplicity`, `daily_energy_kwh`, ...).
    По нему интерфейс может назвать поле так, как его ввёл пользователь.
    """

    def __init__(self, message: str, attribute: str | None = None) -> None:
        super().__init__(message)
        self.attribute = attribute
