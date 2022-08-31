from enum import Enum
from pygame import Surface


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class AutoUpperName(AutoName):
    """Same as autoname, but enforcing upper case."""

    def _generate_next_value_(name, start, count, last_values):
        return str(name).upper()


def position_for_centering(
    surface_on: Surface, surface_under: Surface
) -> tuple[int, int]:
    """Calculate the position for surface on to be on the center of surface_under.

    Then you could just blit the surface using::

        center_pos = position_for_centering(surface_on, surface_under)
        surface_under.blit(surface_on, center_pos)
    """
    size_on = surface_on.get_size()
    size_under = surface_under.get_size()

    return (size_under[0] - size_on[0]) // 2, (size_under[1] - size_on[1]) // 2
