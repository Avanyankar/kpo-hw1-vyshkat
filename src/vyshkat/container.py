"""Composition root: единственное место, где абстракции связываются с реализациями."""

import punq

from vyshkat.cli.app import ConsoleApp
from vyshkat.services.acceptance import AcceptanceService
from vyshkat.services.fleet import Fleet
from vyshkat.services.newbie_policy import NewbiePolicy
from vyshkat.services.numbering import InventoryNumberGenerator
from vyshkat.services.reports import FleetReports
from vyshkat.services.service_center import ConditionServiceCenter, ServiceCenter


def build_container() -> punq.Container:
    container = punq.Container()

    # Состояние учёта: по одному экземпляру на приложение, иначе приёмка и отчёты
    # работали бы с разными парками и разными сериями номеров.
    container.register(Fleet, scope=punq.Scope.singleton)
    container.register(InventoryNumberGenerator, scope=punq.Scope.singleton)

    container.register(ServiceCenter, ConditionServiceCenter)
    container.register(NewbiePolicy)
    container.register(AcceptanceService)
    container.register(FleetReports)
    container.register(ConsoleApp)

    return container
