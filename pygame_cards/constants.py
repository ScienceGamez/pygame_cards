"""Constants for helping with dimensions and things."""

# Size of differnt objects in pixels
CARD_SIZE: tuple[int, int] = (110, 180)  # (width, height)

CARDSET_SIZE: tuple[int, int] = (900, 240)

BOARD_SIZE: tuple[int, int] = (720, 560)
# The radius of the circled borders of the cards
CARD_BORDER_RADIUS_RATIO: float = 0.05


# Common screen resolutions
SCREEN_RESOLUTIONS: dict[str, tuple[int, int]] = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "2K": (2048, 1080),
    "1440p": (2560, 1440),
    "2160p": (3840, 2160),
    "4K": (4096, 2160),
}

# Ratio from card width of spacing between columns
COLUMN_SPACING: float = 0.15
