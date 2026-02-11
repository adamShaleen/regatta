from dataclasses import dataclass

from regatta.models.position import Position
from regatta.models.wind import Heading


@dataclass(frozen=True)
class Yacht:
    position: Position
    heading: Heading
    spinnaker: bool = False
    puff_count: int = 2

    def with_position(self, new_position: Position) -> "Yacht":
        return Yacht(new_position, self.heading, self.spinnaker, self.puff_count)

    def with_heading(self, new_heading: Heading) -> "Yacht":
        return Yacht(self.position, new_heading, self.spinnaker, self.puff_count)

    def with_spinnaker(self, new_spinnaker_position: bool) -> "Yacht":
        return Yacht(
            self.position, self.heading, new_spinnaker_position, self.puff_count
        )

    def with_puff_count(self, new_puff_count: int) -> "Yacht":
        return Yacht(self.position, self.heading, self.spinnaker, new_puff_count)
