import pytest

from vyshkat.cli.errors import CommandError
from vyshkat.cli.parser import Command, parse_line


@pytest.mark.parametrize("line", ["", "   ", "# комментарий", "  # с отступом"])
def test_blank_and_comment_lines_give_nothing(line: str) -> None:
    assert parse_line(line) is None


def test_command_without_arguments() -> None:
    assert parse_line("report") == Command("report")


def test_quoted_name_with_spaces_and_params() -> None:
    command = parse_line('accept scooter "Ninebot Max" simplicity=7 energy=0.4')

    assert command == Command(
        "accept",
        ("scooter", "Ninebot Max"),
        {"simplicity": "7", "energy": "0.4"},
    )


def test_trailing_comment_is_ignored() -> None:
    assert parse_line("inventory  # всё на балансе") == Command("inventory")


def test_unclosed_quote_is_reported() -> None:
    with pytest.raises(CommandError, match="не удалось разобрать"):
        parse_line('add helmet "Шлем M')


def test_empty_param_name_is_reported() -> None:
    with pytest.raises(CommandError, match="пустое имя параметра"):
        parse_line('add dock "Док" =5')


def test_equals_sign_makes_a_param_even_in_quotes() -> None:
    # Известное ограничение: shlex снимает кавычки до разбора, «=» в названии не поддерживается.
    assert parse_line('add helmet "Шлем=M"') == Command("add", ("helmet",), {"Шлем": "M"})


def test_repeated_param_is_reported() -> None:
    with pytest.raises(CommandError, match="energy указан дважды"):
        parse_line('add dock "Док" energy=1 energy=2')
