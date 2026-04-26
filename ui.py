"""Minimal Pygame sidebar controls."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from presets import PRESETS, Preset


PANEL_WIDTH = 300
BG = (13, 15, 21)
CARD = (24, 27, 36)
CARD_ACTIVE = (54, 68, 92)
TEXT = (226, 232, 240)
MUTED = (128, 139, 154)
ACCENT = (102, 217, 239)
LINE = (45, 50, 63)


@dataclass
class Slider:
    label: str
    minimum: float
    maximum: float
    value: float
    rect: pygame.Rect
    precision: int = 4
    dragging: bool = False

    def set_from_x(self, x: int) -> None:
        ratio = (x - self.rect.left) / max(self.rect.width, 1)
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.minimum + ratio * (self.maximum - self.minimum)

    def knob_x(self) -> int:
        ratio = (self.value - self.minimum) / (self.maximum - self.minimum)
        return int(self.rect.left + ratio * self.rect.width)


class Sidebar:
    def __init__(self, x: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(x, 0, width, height)
        self.height = height
        self.font_title = pygame.font.SysFont("menlo", 23, bold=True)
        self.font = pygame.font.SysFont("menlo", 15)
        self.font_small = pygame.font.SysFont("menlo", 12)
        self.font_button = pygame.font.SysFont("menlo", 13, bold=True)
        self.preset_buttons: list[tuple[pygame.Rect, int]] = []
        self.action_buttons: dict[str, pygame.Rect] = {}
        self.sliders: dict[str, Slider] = {}
        self._layout()

    def _layout(self) -> None:
        left = self.rect.left + 20
        button_w = 122
        button_h = 34
        gap = 10
        y = 68

        for index in range(len(PRESETS)):
            row = index // 2
            col = index % 2
            rect = pygame.Rect(left + col * (button_w + gap), y + row * 42, button_w, button_h)
            self.preset_buttons.append((rect, index))

        slider_y = 275
        self.sliders = {
            "feed": Slider("Feed (f)", 0.0100, 0.0900, PRESETS[0].feed, pygame.Rect(left + 94, slider_y, 150, 18)),
            "kill": Slider("Kill (k)", 0.0450, 0.0750, PRESETS[0].kill, pygame.Rect(left + 94, slider_y + 42, 150, 18)),
            "speed": Slider("Speed", 1, 80, 10, pygame.Rect(left + 94, slider_y + 84, 150, 18), precision=0),
        }

        y = 472
        for name in ("reset", "pause", "save"):
            self.action_buttons[name] = pygame.Rect(left, y, 76, 34)
            left += 84

    def set_preset_values(self, preset: Preset, speed: int) -> None:
        self.sliders["feed"].value = preset.feed
        self.sliders["kill"].value = preset.kill
        self.sliders["speed"].value = speed

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for rect, index in self.preset_buttons:
                if rect.collidepoint(pos):
                    return f"preset:{index}"
            for name, rect in self.action_buttons.items():
                if rect.collidepoint(pos):
                    return name
            for name, slider in self.sliders.items():
                hit_rect = slider.rect.inflate(12, 22)
                if hit_rect.collidepoint(pos):
                    slider.dragging = True
                    slider.set_from_x(pos[0])
                    return f"slider:{name}"

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for slider in self.sliders.values():
                slider.dragging = False

        if event.type == pygame.MOUSEMOTION:
            for name, slider in self.sliders.items():
                if slider.dragging:
                    slider.set_from_x(event.pos[0])
                    return f"slider:{name}"

        return None

    def draw(
        self,
        surface: pygame.Surface,
        active_index: int,
        colormap: str,
        paused: bool,
        fps: float,
        step_count: int,
    ) -> None:
        pygame.draw.rect(surface, BG, self.rect)
        self._text(surface, "REACTION", self.font_title, TEXT, self.rect.left + 20, 20)
        self._text(surface, "DIFFUSION", self.font_title, ACCENT, self.rect.left + 146, 20)

        for rect, index in self.preset_buttons:
            active = index == active_index
            color = CARD_ACTIVE if active else CARD
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, ACCENT if active else LINE, rect, 1, border_radius=8)
            self._center_text(surface, PRESETS[index].name, self.font_button, TEXT, rect)

        self._rule(surface, 247)
        for slider in self.sliders.values():
            self._draw_slider(surface, slider)

        self._rule(surface, 414)
        self._text(surface, f"Colormap: {colormap.upper()}", self.font, TEXT, self.rect.left + 20, 434)
        self._keycap(surface, "C", self.rect.right - 56, 430)

        self._rule(surface, 456)
        self._draw_actions(surface, paused)

        self._rule(surface, 530)
        preset = PRESETS[active_index]
        self._text(surface, preset.name, self.font, ACCENT, self.rect.left + 20, 552)
        for line_index, line in enumerate(self._wrap(preset.description, 31)):
            self._text(surface, line, self.font_small, MUTED, self.rect.left + 20, 578 + line_index * 18)

        self._text(surface, f"fps: {fps:02.0f}  step: {step_count}", self.font_small, MUTED, self.rect.left + 20, self.height - 36)

    def _draw_slider(self, surface: pygame.Surface, slider: Slider) -> None:
        y = slider.rect.centery
        self._text(surface, slider.label, self.font, TEXT, self.rect.left + 20, y - 9)
        pygame.draw.line(surface, LINE, (slider.rect.left, y), (slider.rect.right, y), 5)
        pygame.draw.line(surface, ACCENT, (slider.rect.left, y), (slider.knob_x(), y), 5)
        pygame.draw.circle(surface, TEXT, (slider.knob_x(), y), 8)

        value = f"{slider.value:.{slider.precision}f}" if slider.precision else f"{int(slider.value)}"
        self._text(surface, value, self.font_small, MUTED, slider.rect.left, y + 13)

    def _draw_actions(self, surface: pygame.Surface, paused: bool) -> None:
        labels = {"reset": "RESET", "pause": "RESUME" if paused else "PAUSE", "save": "SAVE"}
        for name, rect in self.action_buttons.items():
            pygame.draw.rect(surface, CARD, rect, border_radius=8)
            pygame.draw.rect(surface, ACCENT if name == "pause" and paused else LINE, rect, 1, border_radius=8)
            self._center_text(surface, labels[name], self.font_button, TEXT, rect)

    def _rule(self, surface: pygame.Surface, y: int) -> None:
        pygame.draw.line(surface, LINE, (self.rect.left + 20, y), (self.rect.right - 20, y), 1)

    def _keycap(self, surface: pygame.Surface, text: str, x: int, y: int) -> None:
        rect = pygame.Rect(x, y, 30, 24)
        pygame.draw.rect(surface, CARD, rect, border_radius=5)
        pygame.draw.rect(surface, LINE, rect, 1, border_radius=5)
        self._center_text(surface, text, self.font_button, TEXT, rect)

    def _text(self, surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], x: int, y: int) -> None:
        surface.blit(font.render(text, True, color), (x, y))

    def _center_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], rect: pygame.Rect) -> None:
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=rect.center))

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > width and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines
