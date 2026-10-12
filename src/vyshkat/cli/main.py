"""Точка входа: `vyshkat` (интерактивно) или `vyshkat <файл со сценарием>`."""

import io
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

from vyshkat.cli.app import ConsoleApp
from vyshkat.cli.runner import run
from vyshkat.container import build_container

USAGE = "Использование: vyshkat [файл со сценарием]"


def main(argv: Sequence[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    _use_utf8()
    if len(args) > 1:
        print(USAGE, file=sys.stderr)
        return 2

    app = build_container().resolve(ConsoleApp)
    if args:
        path = Path(args[0])
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as error:
            print(f"Не удалось прочитать {path}: {error}", file=sys.stderr)
            return 1
        run(app, lines, sys.stdout, echo=True)
    elif not sys.stdin.isatty():
        run(app, (line.rstrip("\n") for line in sys.stdin), sys.stdout, echo=True)
    else:
        print("ВышКат: учёт парка. Справка: help, выход: exit")
        try:
            run(app, _prompt(), sys.stdout, echo=False)
        except KeyboardInterrupt:
            print()
    return 0


def _use_utf8() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")


def _prompt() -> Iterator[str]:
    while True:
        try:
            yield input("> ")
        except EOFError:
            print()
            return
