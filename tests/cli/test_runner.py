import io

import pytest

from vyshkat.cli.app import ConsoleApp
from vyshkat.cli.parser import Command
from vyshkat.cli.runner import run
from vyshkat.container import build_container


def make_app() -> ConsoleApp:
    app: ConsoleApp = build_container().resolve(ConsoleApp)
    return app


def run_lines(*lines: str, echo: bool = False, app: ConsoleApp | None = None) -> str:
    out = io.StringIO()
    run(app or make_app(), lines, out, echo=echo)
    return out.getvalue()


def test_echo_marks_commands_and_keeps_comments_as_is() -> None:
    output = run_lines("# раздел", "", 'add helmet "Шлем M"', echo=True)

    assert output.splitlines() == [
        "# раздел",
        "",
        '> add helmet "Шлем M"',
        "Поставлен на баланс: INV-0001 Шлем «Шлем M»",
    ]


def test_without_echo_only_answers_are_printed() -> None:
    assert run_lines('add helmet "Шлем M"') == "Поставлен на баланс: INV-0001 Шлем «Шлем M»\n"


def test_errors_are_reported_and_processing_continues() -> None:
    output = run_lines(
        "sell",
        'accept bicycle "Stels" simplicity=15 condition=5',
        'add helmet "Шлем M',
        'add helmet "Шлем M"',
    )

    assert output.splitlines() == [
        "Ошибка: неизвестная команда «sell», список команд: help",
        "Ошибка: simplicity=15 — простота: ожидается от 1 до 10, получено 15",
        "Ошибка: не закрыта кавычка",
        "Поставлен на баланс: INV-0001 Шлем «Шлем M»",
    ]


def test_exit_stops_processing() -> None:
    assert run_lines("exit", 'add helmet "Шлем M"') == ""


def test_unexpected_errors_are_not_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    # Голый ValueError — признак бага.
    app = make_app()

    def broken(command: Command) -> str:
        raise ValueError("баг")

    monkeypatch.setattr(app, "execute", broken)

    with pytest.raises(ValueError, match="баг"):
        run_lines("report", app=app)
