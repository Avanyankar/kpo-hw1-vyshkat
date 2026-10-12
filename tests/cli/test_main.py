import io
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from vyshkat.cli.main import main

SCENARIO = 'add helmet "Шлем M"\nreport\n'


class FakeTerminal(io.StringIO):
    def isatty(self) -> bool:
        return True


def write_scenario(tmp_path: Path, text: str = SCENARIO) -> Path:
    path = tmp_path / "scenario.txt"
    path.write_text(text, encoding="utf-8")
    return path


def test_runs_scenario_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(write_scenario(tmp_path))]) == 0

    output = capsys.readouterr().out
    assert '> add helmet "Шлем M"\nПоставлен на баланс: INV-0001 Шлем «Шлем M»' in output
    assert "На балансе: 1 (техника: 0, вещи: 1)" in output


def test_redirected_stdin_is_read_like_a_file(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(SCENARIO))

    assert main([]) == 0
    assert "> report" in capsys.readouterr().out


def test_interactive_session_until_end_of_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    answers: Iterator[str] = iter(['add helmet "Шлем M"'])

    def fake_input(prompt: str) -> str:
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr(sys, "stdin", FakeTerminal())
    monkeypatch.setattr("builtins.input", fake_input)

    assert main([]) == 0
    output = capsys.readouterr().out
    assert output.startswith("ВышКат: учёт парка. Справка: help, выход: exit\n")
    assert "Поставлен на баланс: INV-0001 Шлем «Шлем M»" in output


def test_ctrl_c_ends_session_quietly(monkeypatch: pytest.MonkeyPatch) -> None:
    def interrupted(prompt: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(sys, "stdin", FakeTerminal())
    monkeypatch.setattr("builtins.input", interrupted)

    assert main([]) == 0


def test_too_many_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["a.txt", "b.txt"]) == 2
    assert "Использование" in capsys.readouterr().err


def test_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(tmp_path / "нет.txt")]) == 1
    assert "Не удалось прочитать" in capsys.readouterr().err


def test_file_not_in_utf8(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "cp1251.txt"
    path.write_bytes('add helmet "Шлем"'.encode("cp1251"))

    assert main([str(path)]) == 1
    assert "Не удалось прочитать" in capsys.readouterr().err


def test_cyrillic_output_survives_a_pipe(tmp_path: Path) -> None:
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    result = subprocess.run(
        [sys.executable, "-m", "vyshkat", str(write_scenario(tmp_path))],
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert "Поставлен на баланс: INV-0001 Шлем «Шлем M»" in result.stdout.decode("utf-8")
