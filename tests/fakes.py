"""Тестовые двойники, общие для нескольких наборов тестов."""

from vyshkat.domain.vehicles import Vehicle
from vyshkat.services.service_center import Verdict


class FakeServiceCenter:
    """Выносит заранее заданный вердикт и запоминает, кого осматривал."""

    def __init__(self, verdict: Verdict) -> None:
        self.verdict = verdict
        self.inspected: list[Vehicle] = []

    def inspect(self, vehicle: Vehicle) -> Verdict:
        self.inspected.append(vehicle)
        return self.verdict
