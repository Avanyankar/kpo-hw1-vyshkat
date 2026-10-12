import pytest

from vyshkat.domain.vehicles import Bicycle
from vyshkat.services.newbie_policy import NewbiePolicy


def bicycle(simplicity: int) -> Bicycle:
    return Bicycle("Stels", simplicity, 8)


@pytest.mark.parametrize("simplicity", [6, 10])
def test_simple_enough_vehicle_is_suitable(simplicity: int) -> None:
    assert NewbiePolicy().is_suitable(bicycle(simplicity))


@pytest.mark.parametrize("simplicity", [1, 5])
def test_complex_vehicle_is_not_suitable(simplicity: int) -> None:
    assert not NewbiePolicy().is_suitable(bicycle(simplicity))


def test_threshold_is_configurable() -> None:
    strict = NewbiePolicy(min_simplicity=9)

    assert not strict.is_suitable(bicycle(8))
    assert strict.is_suitable(bicycle(9))


@pytest.mark.parametrize("min_simplicity", [0, 11])
def test_threshold_out_of_scale_is_rejected(min_simplicity: int) -> None:
    with pytest.raises(ValueError, match="порог простоты"):
        NewbiePolicy(min_simplicity)
