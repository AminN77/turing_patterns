"""Interactive Gray-Scott reaction-diffusion playground."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pygame

from presets import PRESETS
from renderer import COLORMAP_ORDER, FieldRenderer
from simulation import GrayScott
from ui import PANEL_WIDTH, Sidebar


SIM_SIZE = 256
CANVAS_SIZE = 768
WINDOW_SIZE = (CANVAS_SIZE + PANEL_WIDTH, CANVAS_SIZE)
FPS_TARGET = 30
BRUSH_RADIUS = 7


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Reaction Diffusion")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    simulation = GrayScott()
    renderer = FieldRenderer(SIM_SIZE, CANVAS_SIZE)
    sidebar = Sidebar(CANVAS_SIZE, PANEL_WIDTH, CANVAS_SIZE)

    active_preset_index = 0
    preset = PRESETS[active_preset_index]
    colormap_index = COLORMAP_ORDER.index(preset.colormap)
    feed = preset.feed
    kill = preset.kill
    steps_per_frame = 10
    paused = False
    painting = False
    manual_speed = False
    auto_timer = 0.0

    simulation.reset(preset.seed_mode)
    sidebar.set_preset_values(preset, steps_per_frame)

    running = True
    while running:
        dt_ms = clock.tick(FPS_TARGET)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    simulation.reset(PRESETS[active_preset_index].seed_mode)
                elif event.key == pygame.K_c:
                    colormap_index = (colormap_index + 1) % len(COLORMAP_ORDER)
                elif event.key == pygame.K_s:
                    save_screenshot(screen)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    steps_per_frame = min(80, steps_per_frame + 1)
                    sidebar.sliders["speed"].value = steps_per_frame
                    manual_speed = True
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    steps_per_frame = max(1, steps_per_frame - 1)
                    sidebar.sliders["speed"].value = steps_per_frame
                    manual_speed = True
                elif pygame.K_1 <= event.key <= pygame.K_8:
                    active_preset_index = event.key - pygame.K_1
                    preset = PRESETS[active_preset_index]
                    feed, kill = preset.feed, preset.kill
                    colormap_index = COLORMAP_ORDER.index(preset.colormap)
                    simulation.reset(preset.seed_mode)
                    sidebar.set_preset_values(preset, steps_per_frame)

            action = sidebar.handle_event(event)
            if action:
                if action.startswith("preset:"):
                    active_preset_index = int(action.split(":", 1)[1])
                    preset = PRESETS[active_preset_index]
                    feed, kill = preset.feed, preset.kill
                    colormap_index = COLORMAP_ORDER.index(preset.colormap)
                    simulation.reset(preset.seed_mode)
                    sidebar.set_preset_values(preset, steps_per_frame)
                elif action == "reset":
                    simulation.reset(PRESETS[active_preset_index].seed_mode)
                elif action == "pause":
                    paused = not paused
                elif action == "save":
                    save_screenshot(screen)
                elif action.startswith("slider:"):
                    feed = sidebar.sliders["feed"].value
                    kill = sidebar.sliders["kill"].value
                    steps_per_frame = int(sidebar.sliders["speed"].value)
                    manual_speed = action == "slider:speed" or manual_speed

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.pos[0] < CANVAS_SIZE:
                painting = True
                paint_at_mouse(simulation, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                painting = False
            elif event.type == pygame.MOUSEMOTION and painting:
                paint_at_mouse(simulation, event.pos)

        if not paused:
            simulation.step(feed, kill, steps_per_frame)

        if not manual_speed:
            auto_timer += dt_ms
            if auto_timer >= 1000:
                fps = clock.get_fps()
                if fps > 36 and steps_per_frame < 40:
                    steps_per_frame += 1
                    sidebar.sliders["speed"].value = steps_per_frame
                elif fps < 24 and steps_per_frame > 1:
                    steps_per_frame -= 1
                    sidebar.sliders["speed"].value = steps_per_frame
                auto_timer = 0.0

        frame = renderer.render(simulation.b, COLORMAP_ORDER[colormap_index])
        screen.blit(frame, (0, 0))
        sidebar.draw(
            screen,
            active_preset_index,
            COLORMAP_ORDER[colormap_index],
            paused,
            clock.get_fps(),
            simulation.step_count,
        )
        pygame.display.flip()

    pygame.quit()


def paint_at_mouse(simulation: GrayScott, pos: tuple[int, int]) -> None:
    x, y = pos
    if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
        simulation.paint(x // 3, y // 3, BRUSH_RADIUS)


def save_screenshot(screen: pygame.Surface) -> None:
    screenshots = Path("screenshots")
    screenshots.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    canvas = screen.subsurface(pygame.Rect(0, 0, CANVAS_SIZE, CANVAS_SIZE)).copy()
    pygame.image.save(canvas, screenshots / f"reaction_diffusion_{timestamp}.png")


if __name__ == "__main__":
    main()
