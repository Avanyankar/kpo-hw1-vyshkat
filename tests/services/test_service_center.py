import pytest

from vyshkat.domain.vehicles import Bicycle
from vyshkat.services.service_center import ConditionServiceCenter


def bicycle(condition: int) -> Bicycle:
    return Bicycle("Stels", 9, condition)


@pytest.mark.parametrize("condition", [5, 10])
def test_condition_at_or_above_threshold_is_accepted(condition: int) -> None:
    verdict = ConditionServiceCenter().inspect(bicycle(condition))

    assert verdict.accepted


@pytest.mark.parametrize("condition", [1, 4])
def test_condition_below_threshold_is_rejected(condition: int) -> None:
    verdict = ConditionServiceCenter().inspect(bicycle(condition))

    assert not verdict.accepted
    assert verdict.reason == f"состояние {condition}/10 ниже порога 5"


def test_threshold_is_configurable() -> None:
    strict = ConditionServiceCenter(min_condition=8)

    assert not strict.inspect(bicycle(7)).accepted
    assert strict.inspect(bicycle(8)).accepted


@pytest.mark.parametrize("min_condition", [0, 11])
def test_threshold_out_of_scale_is_rejected(min_condition: int) -> None:
    with pytest.raises(ValueError, match="порог состояния"):
        ConditionServiceCenter(min_condition)
