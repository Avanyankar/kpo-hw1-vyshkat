import pytest
from fakes import FakeServiceCenter

from vyshkat.cli.app import ConsoleApp
from vyshkat.cli.errors import CommandError
from vyshkat.cli.parser import parse_line
from vyshkat.container import build_container
from vyshkat.domain.errors import DomainError
from vyshkat.services.service_center import ServiceCenter, Verdict

NINEBOT = 'accept scooter "Ninebot Max" simplicity=7 condition=8 energy=0.4'
ELTRECO = 'accept ebike "Eltreco" simplicity=4 condition=9 energy=0.9'
HELMET = 'add helmet "Шлем M"'
CABINET = 'add cabinet "Шкаф на Покровке" energy=3.5'


def make_app(service_center: ServiceCenter | None = None) -> ConsoleApp:
    container = build_container()
    if service_center is not None:
        container.register(ServiceCenter, instance=service_center)
    app: ConsoleApp = container.resolve(ConsoleApp)
    return app


def execute(app: ConsoleApp, *lines: str) -> str:
    """Выполняет строки по очереди и возвращает ответ на последнюю."""
    answer = ""
    for line in lines:
        command = parse_line(line)
        assert command is not None
        answer = app.execute(command)
    return answer


def test_accepted_vehicle_gets_a_number() -> None:
    assert execute(make_app(), NINEBOT) == "Принят: INV-0001 Электросамокат «Ninebot Max»"


def test_rejected_vehicle_shows_the_reason() -> None:
    answer = execute(make_app(), 'accept bicycle "Stels" simplicity=9 condition=3')

    assert answer == "Отказ: Велосипед «Stels» — состояние 3/10 ниже порога 5"


def test_accept_uses_service_center_from_container() -> None:
    app = make_app(FakeServiceCenter(Verdict(False, "плановый ремонт")))

    answer = execute(app, NINEBOT)

    assert answer == "Отказ: Электросамокат «Ninebot Max» — плановый ремонт"


def test_thing_is_put_on_balance() -> None:
    assert execute(make_app(), HELMET) == "Поставлен на баланс: INV-0001 Шлем «Шлем M»"


@pytest.mark.parametrize(
    ("line", "hint"),
    [
        ('accept helmet "Шлем"', "«helmet» — это вещь, её ставят на баланс командой add"),
        ('add scooter "Kugoo" energy=1', "«scooter» — это техника, её принимают командой accept"),
    ],
)
def test_wrong_command_for_kind_gives_a_hint(line: str, hint: str) -> None:
    with pytest.raises(CommandError, match=hint):
        execute(make_app(), line)


def test_domain_errors_reach_the_caller() -> None:
    with pytest.raises(DomainError, match="наименование"):
        execute(make_app(), 'accept bicycle "  " simplicity=5 condition=5')


def test_unknown_command() -> None:
    with pytest.raises(CommandError, match="неизвестная команда «sell»"):
        execute(make_app(), "sell")


@pytest.mark.parametrize("line", ["report all", "inventory sort=name", "help me"])
def test_reports_take_no_arguments(line: str) -> None:
    with pytest.raises(CommandError, match="не принимает аргументов"):
        execute(make_app(), line)


def test_empty_fleet_reports() -> None:
    app = make_app()

    assert execute(app, "report") == (
        "На балансе: 0 (техника: 0, вещи: 0)\nСуточный расход энергии: 0.00 кВт·ч"
    )
    assert execute(app, "newbies") == "Подходящей для новичков техники нет"
    assert execute(app, "inventory") == "На балансе ничего нет"


def test_report_counts_kinds_and_energy() -> None:
    answer = execute(make_app(), NINEBOT, ELTRECO, HELMET, CABINET, "report")

    assert answer == (
        "На балансе: 4 (техника: 2, вещи: 2)\n"
        "  Электросамокат: 1\n"
        "  Электровелосипед: 1\n"
        "  Шлем: 1\n"
        "  Зарядный шкаф: 1\n"
        "Суточный расход энергии: 4.80 кВт·ч"
    )


def test_newbies_lists_only_simple_vehicles() -> None:
    answer = execute(make_app(), NINEBOT, ELTRECO, HELMET, "newbies")

    assert answer == "INV-0001  Электросамокат  Ninebot Max"


def test_inventory_shows_number_kind_and_name() -> None:
    answer = execute(make_app(), NINEBOT, HELMET, CABINET, "inventory")

    assert answer == (
        "INV-0001  Электросамокат  Ninebot Max\n"
        "INV-0002  Шлем            Шлем M\n"
        "INV-0003  Зарядный шкаф   Шкаф на Покровке"
    )


def test_help_mentions_every_command() -> None:
    answer = execute(make_app(), "help")

    for command in ["accept", "add", "report", "newbies", "inventory", "kinds", "help", "exit"]:
        assert command in answer


def test_kinds_lists_every_kind_with_its_params() -> None:
    answer = execute(make_app(), "kinds")

    for kind in ["scooter", "ebike", "bicycle", "helmet", "dock", "cabinet"]:
        assert kind in answer
    assert "bicycle    simplicity=1..10 condition=1..10\n" in answer
