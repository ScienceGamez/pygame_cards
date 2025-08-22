"""Some effects for cards."""

from enum import auto
from math import sqrt
import pygame

from pygame_cards.utils import AutoName


class Decay(AutoName):
    """Different decays for halos."""

    LINEAR = auto()
    QUADRATIC = auto()
    NONE = auto()


def outer_border(
    surface: pygame.Surface,
    width: int = 3,
    radius: int = 20,
    color: pygame.Color = pygame.Color((105, 105, 105, 255)),
    inplace: bool = False,
) -> pygame.Surface:
    """Generate a border for the surface.

    :arg surface: The surface that will have the border.
    :arg radius: The radius of the angles.
    :arg width: The width of the border.
    :arg color: The color of the border.
    :arg inplace: Whether to operate directly on the given surface or
        returning a new surface containing only the border.

    """
    size = surface.get_size()
    s = pygame.Surface(size, pygame.SRCALPHA) if not inplace else surface

    pygame.draw.rect(
        s,
        color,
        pygame.Rect(0, 0, *size),
        width=width,
        border_radius=radius,
    )

    return s


def outer_halo(
    inner_surface: pygame.Surface,
    radius: int = 20,
    inner_color: pygame.Color = pygame.Color((255, 255, 255, 255)),
    outer_color: pygame.Color = pygame.Color((255, 255, 255, 0)),
    decay: Decay = Decay.QUADRATIC,
    fill_inside: bool = True,
) -> pygame.Surface:
    """Create a halo around the card.

    :arg radius: The radius of the halo in pixels.
    :arg fill_inside: If false, it is transparent where the card is.
        Else, fill with the inner_color.

    :return: The halo surface.

    """
    inner_size = inner_surface.get_size()
    inner_size = (int(inner_size[0]), int(inner_size[1]))
    radius = int(radius)
    surf = pygame.Surface(
        (inner_size[0] + 2 * radius, inner_size[1] + 2 * int(radius)),
        pygame.SRCALPHA,
    )
    if fill_inside:
        surf.fill(inner_color, pygame.Rect(radius, radius, *inner_size))
    # A line with the pixel values for the halo, the value will be between 0 and radius
    # When x = 0, decay = 0, and x= radius, decay = 1
    match decay:
        case Decay.LINEAR:
            decay_func = lambda x: min(max(x / radius, 0), 1)
        case Decay.QUADRATIC:
            # a*x**2 + c
            a = 1.0 / radius**2
            decay_func = lambda x: 1 - a * (min(x, radius) - radius) ** 2
        case Decay.NONE:
            decay_func = lambda x: 1
        case _:
            raise NotImplementedError(f"{decay = } not implemented.")

    halo_colors = [
        inner_color.lerp(outer_color, decay_func(i)) for i in range(int(radius))
    ]
    # A line surface to put the halo on
    line_surf = pygame.Surface((int(radius), 1), pygame.SRCALPHA)
    for i, c in enumerate(halo_colors):
        line_surf.set_at((i, 0), c)

    blit_right = [
        (line_surf, (inner_size[0] + radius, i))
        for i in range(radius, inner_size[1] + radius)
    ]
    surf.blits(blit_right)

    line_surf = pygame.transform.rotate(line_surf, 90)
    blit_top = [(line_surf, (i, 0)) for i in range(radius, inner_size[0] + radius)]
    surf.blits(blit_top)

    line_surf = pygame.transform.rotate(line_surf, 90)
    blit_left = [(line_surf, (0, i)) for i in range(radius, inner_size[1] + radius)]
    surf.blits(blit_left)

    line_surf = pygame.transform.rotate(line_surf, 90)
    blit_bot = [
        (line_surf, (i, radius + inner_size[1]))
        for i in range(radius, inner_size[0] + radius)
    ]
    surf.blits(blit_bot)

    # Now do the same for the edge but it is 2D
    coords = sum([[(i, j) for i in range(radius)] for j in range(radius)], start=[])
    rads = [sqrt(i**2 + j**2) for i, j in coords]
    angle_surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
    for coord, r in zip(coords, rads):
        angle_surf.set_at(coord, inner_color.lerp(outer_color, decay_func(r)))
    surf.blit(angle_surf, (inner_size[0] + radius, inner_size[1] + radius))
    angle_surf = pygame.transform.rotate(angle_surf, 90)
    surf.blit(angle_surf, (inner_size[0] + radius, 0))
    angle_surf = pygame.transform.rotate(angle_surf, 90)
    surf.blit(angle_surf, (0, 0))
    angle_surf = pygame.transform.rotate(angle_surf, 90)
    surf.blit(angle_surf, (0, inner_size[1] + radius))

    return surf
