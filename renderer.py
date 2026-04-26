"""Render simulation fields into Pygame surfaces."""

from __future__ import annotations

import numpy as np
import pygame


COLORMAP_ORDER = ("inferno", "ice", "organic", "neon")

_COLOR_STOPS: dict[str, tuple[tuple[float, tuple[int, int, int]], ...]] = {
    "inferno": (
        (0.00, (5, 4, 18)),
        (0.25, (48, 12, 84)),
        (0.50, (156, 47, 82)),
        (0.75, (238, 104, 38)),
        (1.00, (252, 244, 164)),
    ),
    "ice": (
        (0.00, (3, 8, 28)),
        (0.30, (12, 57, 107)),
        (0.60, (46, 154, 204)),
        (0.82, (164, 225, 240)),
        (1.00, (250, 255, 255)),
    ),
    "organic": (
        (0.00, (12, 10, 5)),
        (0.28, (45, 57, 25)),
        (0.55, (96, 126, 54)),
        (0.78, (169, 138, 76)),
        (1.00, (237, 215, 155)),
    ),
    "neon": (
        (0.00, (2, 1, 14)),
        (0.22, (18, 0, 62)),
        (0.48, (201, 22, 168)),
        (0.72, (0, 229, 225)),
        (1.00, (241, 255, 118)),
    ),
}


class FieldRenderer:
    def __init__(self, sim_size: int, display_size: int) -> None:
        self.sim_size = sim_size
        self.display_size = display_size
        self._maps = {name: self._build_lut(stops) for name, stops in _COLOR_STOPS.items()}

    def render(self, field: np.ndarray, colormap: str) -> pygame.Surface:
        """Convert the B field to an upscaled RGB surface."""
        values = np.clip(field * 3.2 - 0.08, 0.0, 1.0)
        values = np.sqrt(values, out=values)
        indices = np.minimum((values * 255).astype(np.uint8), 255)
        rgb = self._maps[colormap][indices]

        small = pygame.surfarray.make_surface(np.swapaxes(rgb, 0, 1))
        return pygame.transform.smoothscale(small, (self.display_size, self.display_size))

    @staticmethod
    def _build_lut(stops: tuple[tuple[float, tuple[int, int, int]], ...]) -> np.ndarray:
        lut = np.zeros((256, 3), dtype=np.uint8)
        for index in range(len(stops) - 1):
            start_pos, start_color = stops[index]
            end_pos, end_color = stops[index + 1]
            start = int(start_pos * 255)
            end = int(end_pos * 255)
            span = max(end - start, 1)
            mix = np.linspace(0.0, 1.0, span + 1, dtype=np.float32)[:, None]
            colors = (1.0 - mix) * np.array(start_color) + mix * np.array(end_color)
            lut[start : end + 1] = colors.astype(np.uint8)
        return lut
