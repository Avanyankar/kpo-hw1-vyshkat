"""Цикл ввода: строки → команды → ответы. Источник строк не важен: файл, pipe или клавиатура."""

from collections.abc import Iterable
from typing import TextIO

from vyshkat.cli.app import ConsoleApp
from vyshkat.cli.errors import CommandError
from vyshkat.cli.parser import parse_line
from vyshkat.domain.errors import DomainError


def run(app: ConsoleApp, lines: Iterable[str], out: TextIO, *, echo: bool) -> None:
    """echo печатает каждую строку перед ответом: при чтении из файла видно, что выполняется."""
    for line in lines:
        if echo:
            # Команды печатаются с «> », комментарии и пустые строки — как есть.
            is_command = line.strip() and not line.lstrip().startswith("#")
            print(f"> {line}" if is_command else line, file=out)
        try:
            command = parse_line(line)
            if command is None:
                continue
            if command.name == "exit":
                return
            print(app.execute(command), file=out)
        # Только ошибки ввода и нарушения модели; остальное — баги.
        except (CommandError, DomainError) as error:
            print(f"Ошибка: {error}", file=out)
