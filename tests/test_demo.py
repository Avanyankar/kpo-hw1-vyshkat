"""Демо-сценарий — то, что увидит проверяющий; он не должен незаметно сломаться."""

from pathlib import Path

import pytest

from vyshkat.cli.main import main

DEMO = Path(__file__).parents[1] / "scenarios" / "demo.txt"
ERRORS_SECTION = "# --- 5. Ошибки ввода"


def test_demo_runs_to_the_end(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(DEMO)]) == 0

    output = capsys.readouterr().out
    before_errors, errors_section = output.split(ERRORS_SECTION)

    # До раздела ошибок всё принимается штатно: ни одной ошибки ввода.
    assert "Ошибка:" not in before_errors
    assert before_errors.count("Отказ:") == 2
    assert "Принят: INV-0004" in before_errors
    assert "Поставлен на баланс: INV-0008" in before_errors

    # В разделе ошибок каждая некорректная команда даёт сообщение, а парк не меняется.
    assert errors_section.count("Ошибка:") == 11
    assert errors_section.rstrip().endswith("> exit")
    assert "На балансе: 8 (техника: 4, вещи: 4)" in errors_section
