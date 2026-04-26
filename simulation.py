"""Gray-Scott reaction-diffusion simulation math."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SimConfig:
    width: int = 256
    height: int = 256
    diffusion_a: float = 1.0
    diffusion_b: float = 0.5
    dt: float = 1.0


class GrayScott:
    """Vectorized Gray-Scott simulation on a toroidal float32 grid."""

    def __init__(self, config: SimConfig | None = None) -> None:
        self.config = config or SimConfig()
        shape = (self.config.height, self.config.width)
        self.a = np.ones(shape, dtype=np.float32)
        self.b = np.zeros(shape, dtype=np.float32)
        self.step_count = 0
        self._rng = np.random.default_rng()

    def reset(self, seed_mode: str = "center") -> None:
        self.a.fill(1.0)
        self.b.fill(0.0)
        self.step_count = 0

        if seed_mode == "scatter":
            self.seed_scatter()
        elif seed_mode == "mouse":
            self.seed_center()
        else:
            self.seed_center()

    def step(self, feed: float, kill: float, iterations: int = 1) -> None:
        """Advance the fields using wrap-around boundaries."""
        da = self.config.diffusion_a
        db = self.config.diffusion_b
        dt = self.config.dt

        for _ in range(iterations):
            lap_a = self._laplacian(self.a)
            lap_b = self._laplacian(self.b)
            reaction = self.a * self.b * self.b

            self.a += (da * lap_a - reaction + feed * (1.0 - self.a)) * dt
            self.b += (db * lap_b + reaction - (kill + feed) * self.b) * dt
            np.clip(self.a, 0.0, 1.0, out=self.a)
            np.clip(self.b, 0.0, 1.0, out=self.b)
            self.step_count += 1

    def seed_center(self) -> None:
        size = 28
        cx = self.config.width // 2
        cy = self.config.height // 2
        self._seed_rect(cx - size // 2, cy - size // 2, size, size, noisy=True)

    def seed_scatter(self) -> None:
        for _ in range(int(self._rng.integers(8, 13))):
            size = int(self._rng.integers(10, 24))
            x = int(self._rng.integers(0, self.config.width))
            y = int(self._rng.integers(0, self.config.height))
            self.paint(x, y, size, strength=1.0)

    def paint(self, x: int, y: int, radius: int = 8, strength: float = 0.95) -> None:
        """Paint B chemical into a circular brush with toroidal wrapping."""
        xs = (np.arange(x - radius, x + radius + 1) % self.config.width).astype(np.intp)
        ys = (np.arange(y - radius, y + radius + 1) % self.config.height).astype(np.intp)
        yy, xx = np.ix_(np.arange(-radius, radius + 1), np.arange(-radius, radius + 1))
        mask = (xx * xx + yy * yy) <= radius * radius

        area_a = self.a[np.ix_(ys, xs)].copy()
        area_b = self.b[np.ix_(ys, xs)].copy()
        area_a[mask] = np.minimum(area_a[mask], 0.35)
        area_b[mask] = np.maximum(area_b[mask], strength)
        self.a[np.ix_(ys, xs)] = area_a
        self.b[np.ix_(ys, xs)] = area_b

    def _seed_rect(self, x: int, y: int, width: int, height: int, noisy: bool) -> None:
        xs = np.arange(x, x + width) % self.config.width
        ys = np.arange(y, y + height) % self.config.height
        noise = self._rng.random((height, width), dtype=np.float32) if noisy else 0.0
        self.a[np.ix_(ys, xs)] = 0.45 + 0.1 * noise
        self.b[np.ix_(ys, xs)] = 0.75 + 0.2 * noise

    @staticmethod
    def _laplacian(field: np.ndarray) -> np.ndarray:
        return (
            -1.0 * field
            + 0.2 * np.roll(field, 1, axis=0)
            + 0.2 * np.roll(field, -1, axis=0)
            + 0.2 * np.roll(field, 1, axis=1)
            + 0.2 * np.roll(field, -1, axis=1)
            + 0.05 * np.roll(np.roll(field, 1, axis=0), 1, axis=1)
            + 0.05 * np.roll(np.roll(field, 1, axis=0), -1, axis=1)
            + 0.05 * np.roll(np.roll(field, -1, axis=0), 1, axis=1)
            + 0.05 * np.roll(np.roll(field, -1, axis=0), -1, axis=1)
        )
