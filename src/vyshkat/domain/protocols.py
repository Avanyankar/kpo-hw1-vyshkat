"""Абстракции, которые требует задание: потребитель энергии и инвентаризируемый объект."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class EnergyConsumer(Protocol):
    """Устройство, у которого учитывается суточный расход энергии.

    runtime_checkable нужен отчёту по энергии: он фильтрует активы через isinstance.
    Такая проверка смотрит только на наличие атрибута, сигнатуру она не сверяет.
    """

    @property
    def daily_energy_kwh(self) -> float: ...


class Inventoried(Protocol):
    """Строка инвентарной ведомости: номер, вид и наименование объекта на балансе."""

    @property
    def number(self) -> str: ...

    @property
    def kind(self) -> str: ...

    @property
    def name(self) -> str: ...
