from regatta.models.position import Position
from regatta.models.wind import Heading
from regatta.models.yacht import Yacht


def test_yacht_defaults():
    default = Yacht(Position(0, 0), Heading.SOUTH)
    assert not default.spinnaker
    assert default.puff_count == 2


def test_with_position():
    original = Yacht(Position(1, 2), Heading.SOUTH)
    updated = original.with_position(Position(2, 1))
    assert original.position == Position(1, 2)
    assert updated.position == Position(2, 1)
    assert original is not updated


def test_with_heading():
    original = Yacht(Position(1, 1), Heading.NORTH)
    updated = original.with_heading(Heading.SOUTH)
    assert original.heading == Heading.NORTH
    assert updated.heading == Heading.SOUTH
    assert original is not updated


def test_with_spinnaker():
    original = Yacht(Position(2, 2), Heading.SOUTH_EAST)
    updated = original.with_spinnaker(True)
    assert not original.spinnaker
    assert updated.spinnaker
    assert original is not updated


def test_with_puff_count():
    original = Yacht(Position(3, 3), Heading.EAST)
    updated = original.with_puff_count(0)
    assert original.puff_count == 2
    assert updated.puff_count == 0
    assert original is not updated
