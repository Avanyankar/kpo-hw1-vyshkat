"""Разбор строки ввода: `команда позиционные... ключ=значение...`.

Любой токен со знаком `=` считается параметром, даже в кавычках: shlex снимает кавычки
до разбора. Поэтому `=` в названии не поддерживается.
"""

import shlex
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from vyshkat.cli.errors import CommandError


@dataclass(frozen=True)
class Command:
    name: str
    args: tuple[str, ...] = ()
    params: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))


def parse_line(line: str) -> Command | None:
    """Пустая строка и строка-комментарий (`# ...`) дают None."""
    try:
        tokens = shlex.split(line, comments=True)
    except ValueError as error:  # незакрытая кавычка
        raise CommandError(f"не удалось разобрать строку: {error}") from error
    if not tokens:
        return None

    name, *rest = tokens
    args: list[str] = []
    params: dict[str, str] = {}
    for token in rest:
        key, separator, value = token.partition("=")
        if not separator:
            args.append(token)
        elif not key:
            raise CommandError(f"пустое имя параметра в «{token}»")
        elif key in params:
            raise CommandError(f"параметр {key} указан дважды")
        else:
            params[key] = value
    return Command(name, tuple(args), MappingProxyType(params))
