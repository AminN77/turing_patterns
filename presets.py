"""Named Gray-Scott presets tuned for visually distinct behavior."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    name: str
    feed: float
    kill: float
    colormap: str
    seed_mode: str
    description: str


PRESETS: tuple[Preset, ...] = (
    Preset(
        "Coral",
        0.0545,
        0.0620,
        "inferno",
        "center",
        "Spot-like patterns with stable circular domains.",
    ),
    Preset(
        "Zebra",
        0.0350,
        0.0600,
        "ice",
        "scatter",
        "Striped waves that stretch into animal-skin bands.",
    ),
    Preset(
        "Maze",
        0.0290,
        0.0570,
        "neon",
        "scatter",
        "Branching corridors that lock into labyrinths.",
    ),
    Preset(
        "Mitosis",
        0.0367,
        0.0649,
        "organic",
        "center",
        "Cells split, compete, and leave living membranes.",
    ),
    Preset(
        "Worms",
        0.0780,
        0.0610,
        "organic",
        "scatter",
        "Fast crawling strands with biological motion.",
    ),
    Preset(
        "Fingerprint",
        0.0200,
        0.0500,
        "ice",
        "center",
        "Fine ridges curl into fingerprint-like whorls.",
    ),
    Preset(
        "Holes",
        0.0390,
        0.0580,
        "inferno",
        "scatter",
        "Perforated sheets with pulsing dark voids.",
    ),
    Preset(
        "Unstable",
        0.0260,
        0.0510,
        "neon",
        "scatter",
        "Volatile fronts that keep breaking and reforming.",
    ),
)


PRESET_BY_NAME = {preset.name: preset for preset in PRESETS}
