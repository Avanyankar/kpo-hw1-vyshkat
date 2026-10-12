"""Выполнение команд: вызывает сервисы и превращает результат в текст для пользователя."""

from collections.abc import Callable, Iterable, Mapping

from vyshkat.cli.catalog import THING_KINDS, VEHICLE_KINDS, Kind, create
from vyshkat.cli.errors import CommandError
from vyshkat.cli.parser import Command
from vyshkat.domain.protocols import Inventoried
from vyshkat.services.acceptance import AcceptanceService, Accepted, Rejected
from vyshkat.services.reports import FleetReports

HELP = """\
Команды:
  accept <вид> "<название>" simplicity=N condition=N [energy=X]
                         принять технику, перед приёмкой — техосмотр
  add <вид> "<название>" [energy=X]
                         поставить вещь на баланс, без осмотра
  report                 число единиц и суточный расход энергии
  newbies                техника, которую можно выдавать новичкам
  inventory              номера, виды и наименования всего на балансе
  kinds                  виды техники и вещей и их параметры
  help                   эта справка
  exit                   выход

Название с пробелами — в кавычках. Знак «=» в названии не поддерживается.
Дробные числа — через точку: energy=0.4"""


class ConsoleApp:
    def __init__(self, acceptance: AcceptanceService, reports: FleetReports) -> None:
        self._acceptance = acceptance
        self._reports = reports
        self._handlers: Mapping[str, Callable[[Command], str]] = {
            "accept": self._accept,
            "add": self._add,
            "report": self._without_args(self._report),
            "newbies": self._without_args(self._newbies),
            "inventory": self._without_args(self._inventory),
            "kinds": self._without_args(self._kinds),
            "help": self._without_args(lambda: HELP),
        }

    def execute(self, command: Command) -> str:
        handler = self._handlers.get(command.name)
        if handler is None:
            raise CommandError(f"неизвестная команда «{command.name}», список команд: help")
        return handler(command)

    def _accept(self, command: Command) -> str:
        _reject_wrong_catalog(command, THING_KINDS, "это вещь, её ставят на баланс командой add")
        vehicle = create(VEHICLE_KINDS, command.args, command.params)
        match self._acceptance.accept_vehicle(vehicle):
            case Accepted(item):
                return f"Принят: {_describe(item)}"
            case Rejected(reason):
                return f"Отказ: {vehicle.kind} «{vehicle.name}» — {reason}"

    def _add(self, command: Command) -> str:
        _reject_wrong_catalog(command, VEHICLE_KINDS, "это техника, её принимают командой accept")
        thing = create(THING_KINDS, command.args, command.params)
        return f"Поставлен на баланс: {_describe(self._acceptance.add_thing(thing).item)}"

    def _report(self) -> str:
        counts = self._reports.unit_counts()
        lines = [f"На балансе: {counts.total} (техника: {counts.vehicles}, вещи: {counts.things})"]
        lines += [f"  {kind}: {count}" for kind, count in counts.by_kind.items()]
        lines.append(f"Суточный расход энергии: {self._reports.total_daily_energy_kwh():.2f} кВт·ч")
        return "\n".join(lines)

    def _newbies(self) -> str:
        return _table(self._reports.newbie_vehicles()) or "Подходящей для новичков техники нет"

    def _inventory(self) -> str:
        return _table(self._reports.inventory()) or "На балансе ничего нет"

    def _kinds(self) -> str:
        lines = ["Техника (accept, с техосмотром):"]
        lines += [f"  {name:<10} {kind.usage}" for name, kind in VEHICLE_KINDS.items()]
        lines.append("Вещи (add, без осмотра):")
        lines += [f"  {name:<10} {kind.usage}".rstrip() for name, kind in THING_KINDS.items()]
        return "\n".join(lines)

    @staticmethod
    def _without_args(handler: Callable[[], str]) -> Callable[[Command], str]:
        def run(command: Command) -> str:
            if command.args or command.params:
                raise CommandError(f"команда {command.name} не принимает аргументов")
            return handler()

        return run


def _reject_wrong_catalog[T](command: Command, other: Mapping[str, Kind[T]], hint: str) -> None:
    if command.args and command.args[0] in other:
        raise CommandError(f"«{command.args[0]}» — {hint}")


def _describe(entry: Inventoried) -> str:
    return f"{entry.number} {entry.kind} «{entry.name}»"


def _table(entries: Iterable[Inventoried]) -> str:
    rows = [(entry.number, entry.kind, entry.name) for entry in entries]
    if not rows:
        return ""
    kind_width = max(len(kind) for _, kind, _ in rows)
    return "\n".join(f"{number}  {kind:<{kind_width}}  {name}" for number, kind, name in rows)
