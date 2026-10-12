from vyshkat.services.numbering import InventoryNumberGenerator


def test_numbers_go_in_one_series() -> None:
    numbers = InventoryNumberGenerator()

    assert [numbers.next_number() for _ in range(3)] == ["INV-0001", "INV-0002", "INV-0003"]
