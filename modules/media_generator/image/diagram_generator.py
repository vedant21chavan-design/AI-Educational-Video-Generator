"""
Lightweight, fully local diagram generator for Physics/Astronomy scenes.

Stable Diffusion (used for Biology/Chemistry/Earth Science scenes) does not
handle abstract physics concepts well and cannot render legible text, so
Physics scenes are instead illustrated with simple, matplotlib-drawn
schematic diagrams. These are less "photographic" but they are actually
readable, on-topic, and can include real labels - something Stable
Diffusion can never do.

This is a small, template-based system: a handful of common diagram
archetypes (motion/force, orbit/gravity, wave, energy levels) plus a
generic "concept card" fallback for anything that doesn't match a template.
It is not meant to draw an accurate diagram for every possible physics
topic - it is meant to always produce something clean, legible, and
on-topic instead of Stable Diffusion's garbled or irrelevant guesses.

Each template is deterministically randomized (seeded from the scene's own
title/narration/visual_prompt) so that several scenes matching the same
template - which is common within one video - don't render the identical
picture over and over. Same scene text always regenerates the same
diagram, but different scenes look visibly different from each other.
"""

import hashlib
import os
import random

import matplotlib
matplotlib.use("Agg")  # headless rendering, no GUI backend needed
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


FIGURE_SIZE_PX = 512
DPI = 100
FIGSIZE = (FIGURE_SIZE_PX / DPI, FIGURE_SIZE_PX / DPI)

BACKGROUND_COLOR = "#FFFFFF"
TEXT_COLOR = "#1E1B4B"

# A few accent/secondary color pairs to rotate through so scenes sharing a
# template don't also share identical colors.
COLOR_PALETTES = [
    ("#4F46E5", "#F97316"),  # indigo / orange (site's UI accent)
    ("#0EA5E9", "#DB2777"),  # sky blue / pink
    ("#059669", "#D97706"),  # green / amber
    ("#7C3AED", "#DC2626"),  # violet / red
]


TEMPLATES = {
    "force_motion": [
        "force", "newton", "acceleration", "motion", "friction", "momentum",
        "velocity", "mass", "push", "pull", "collision",
    ],
    "orbit_gravity": [
        "orbit", "planet", "gravity", "black hole", "star", "galaxy",
        "solar system", "moon", "satellite", "sun", "space", "universe",
        "cosmic", "gravitational",
    ],
    "wave": [
        "wave", "frequency", "wavelength", "sound", "light", "amplitude",
        "oscillation", "vibration", "electromagnetic",
    ],
    "energy_levels": [
        "energy", "electron", "photon", "quantum", "level", "atom",
        "excited", "emission",
    ],
}


def _pick_template(*texts):
    combined = " ".join(t.lower() for t in texts if t)
    best_template = None
    best_score = 0
    for template_name, keywords in TEMPLATES.items():
        score = sum(1 for keyword in keywords if keyword in combined)
        if score > best_score:
            best_score = score
            best_template = template_name
    return best_template


def _seed_from_text(*texts):
    """Deterministic seed derived from the scene's own text, so the same
    scene always regenerates the same diagram, but different scenes (even
    ones sharing a template) get different random choices."""
    combined = "|".join(t or "" for t in texts)
    digest = hashlib.sha256(combined.encode("utf-8")).hexdigest()
    return int(digest, 16) % (2 ** 32)


def _new_figure():
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    return fig, ax


def _draw_force_motion(ax, title, rng):
    accent, secondary = rng.choice(COLOR_PALETTES)
    flip = rng.choice([True, False])
    box_x = rng.uniform(3.0, 4.2)
    box_w = rng.uniform(1.8, 2.6)

    ground_x1, ground_x2 = (9, 1) if flip else (1, 9)
    ax.plot([1, 9], [2, 2], color=TEXT_COLOR, linewidth=2)

    box = patches.FancyBboxPatch(
        (box_x, 2), box_w, 1.6,
        boxstyle="round,pad=0.05",
        linewidth=2, edgecolor=TEXT_COLOR, facecolor=accent, alpha=0.85,
    )
    ax.add_patch(box)

    arrow_dx = -1.8 if flip else 1.8
    arrow_start_x = box_x if flip else box_x + box_w
    ax.annotate(
        "", xy=(arrow_start_x + arrow_dx, 2.8), xytext=(arrow_start_x, 2.8),
        arrowprops=dict(arrowstyle="->", color=secondary, linewidth=3),
    )
    ax.text(arrow_start_x + arrow_dx / 2, 3.3, "Force (F)", color=secondary,
            fontsize=13, ha="center", weight="bold")

    motion_x1, motion_x2 = (ground_x2 - 2.5, ground_x2) if flip else (ground_x1 + 2.5, ground_x1 + 5.5)
    ax.annotate(
        "", xy=(motion_x2, 1.2), xytext=(motion_x1, 1.2),
        arrowprops=dict(arrowstyle="->", color=TEXT_COLOR, linewidth=2),
    )
    ax.text((motion_x1 + motion_x2) / 2, 0.7, "Motion", color=TEXT_COLOR,
            fontsize=11, ha="center")
    ax.text(5, 8.7, title, color=TEXT_COLOR, fontsize=14,
            ha="center", weight="bold")


def _draw_orbit_gravity(ax, title, rng):
    accent, secondary = rng.choice(COLOR_PALETTES)
    center = (5, 5)
    center_radius = rng.uniform(0.7, 1.1)
    ax.add_patch(patches.Circle(center, center_radius, facecolor=TEXT_COLOR, edgecolor="none"))

    ring_count = rng.choice([1, 2, 3])
    base_radius = rng.uniform(1.8, 2.4)
    radii = [base_radius + i * rng.uniform(0.8, 1.2) for i in range(ring_count)]
    for radius in radii:
        ax.add_patch(patches.Circle(
            center, radius, facecolor="none",
            edgecolor=accent, linewidth=1.5, linestyle="--",
        ))

    orbiting_body_count = rng.choice([1, 1, 2])  # usually 1, sometimes 2
    body_colors = [secondary, accent]
    for i in range(orbiting_body_count):
        orbit_radius = rng.choice(radii)
        orbit_angle = np.radians(rng.uniform(0, 360))
        orbit_point = (
            center[0] + orbit_radius * np.cos(orbit_angle),
            center[1] + orbit_radius * np.sin(orbit_angle),
        )
        body_size = rng.uniform(0.25, 0.42)
        ax.add_patch(patches.Circle(
            orbit_point, body_size, facecolor=body_colors[i % 2], edgecolor="none",
        ))

    ax.text(5, 8.9, title, color=TEXT_COLOR, fontsize=14, ha="center", weight="bold")


def _draw_wave(ax, title, rng):
    accent, secondary = rng.choice(COLOR_PALETTES)
    frequency = rng.uniform(1.2, 2.3)
    amplitude = rng.uniform(1.3, 2.1)

    x = np.linspace(0.5, 9.5, 400)
    y = 5 + amplitude * np.sin((x - 0.5) * frequency)
    ax.plot(x, y, color=accent, linewidth=3)
    ax.plot([0.5, 9.5], [5, 5], color=TEXT_COLOR, linewidth=1, linestyle=":")

    marker_end = rng.uniform(3.5, 5.0)
    ax.annotate(
        "", xy=(marker_end, 2.6), xytext=(0.5, 2.6),
        arrowprops=dict(arrowstyle="<->", color=secondary, linewidth=2),
    )
    ax.text((0.5 + marker_end) / 2, 2.1, "Wavelength", color=secondary,
            fontsize=11, ha="center")
    ax.text(5, 8.9, title, color=TEXT_COLOR, fontsize=14, ha="center", weight="bold")


def _draw_energy_levels(ax, title, rng):
    accent, secondary = rng.choice(COLOR_PALETTES)
    level_count = rng.choice([3, 4])
    levels_y = np.linspace(2.2, 7.2, level_count)
    labels = ["Ground state"] + [f"Excited state {i}" for i in range(1, level_count)]

    for y, label in zip(levels_y, labels):
        ax.plot([2, 8], [y, y], color=TEXT_COLOR, linewidth=2.5)
        ax.text(8.3, y, label, color=TEXT_COLOR, fontsize=9, va="center")

    transition_start = rng.randrange(0, level_count - 1)
    ax.annotate(
        "", xy=(4, levels_y[transition_start + 1]), xytext=(4, levels_y[transition_start]),
        arrowprops=dict(arrowstyle="->", color=secondary, linewidth=2.5),
    )
    ax.text(3.5, (levels_y[transition_start] + levels_y[transition_start + 1]) / 2,
            "Photon", color=secondary, fontsize=11, ha="right")
    ax.text(5, 9.2, title, color=TEXT_COLOR, fontsize=13, ha="center", weight="bold")


def _draw_concept_card(ax, title, rng):
    accent, secondary = rng.choice(COLOR_PALETTES)
    # Generic, clean fallback: the scene's own title, large and centered,
    # on an accent-colored card, with a small decorative accent shape so
    # repeats of this fallback still look distinct from each other.
    card = patches.FancyBboxPatch(
        (0.6, 3), 8.8, 4,
        boxstyle="round,pad=0.1",
        linewidth=0, facecolor=accent, alpha=0.12,
    )
    ax.add_patch(card)

    if rng.choice([True, False]):
        ax.add_patch(patches.Circle((1.6, 7.6), 0.35, facecolor=secondary, alpha=0.7))
    else:
        ax.add_patch(patches.RegularPolygon((1.6, 7.6), 4, radius=0.4, facecolor=secondary, alpha=0.7))

    ax.text(
        5, 5, title, color=TEXT_COLOR, fontsize=16, ha="center", va="center",
        weight="bold", wrap=True,
    )


_DRAW_FUNCTIONS = {
    "force_motion": _draw_force_motion,
    "orbit_gravity": _draw_orbit_gravity,
    "wave": _draw_wave,
    "energy_levels": _draw_energy_levels,
}


def generate_diagram(title, narration, visual_prompt, output_path):
    """
    Render a schematic diagram PNG for a Physics/Astronomy scene, in place
    of asking Stable Diffusion for a photographic image it can't produce
    well. Picks the best-matching template by keyword overlap across the
    scene's title/narration/visual_prompt, falling back to a plain,
    legible title card if nothing matches. Diagram parameters (colors,
    angles, counts) are seeded from the scene's own text, so repeated
    scenes of the same template don't render an identical picture.

    Returns the output path (matching generate_image's interface).
    """
    template_name = _pick_template(title, narration, visual_prompt)
    draw_function = _DRAW_FUNCTIONS.get(template_name, _draw_concept_card)
    rng = random.Random(_seed_from_text(title, narration, visual_prompt))

    fig, ax = _new_figure()
    draw_function(ax, title or "", rng)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fig.savefig(output_path, facecolor=fig.get_facecolor())
    plt.close(fig)

    return output_path


if __name__ == "__main__":
    generate_diagram(
        title="Newton's Third Law",
        narration="For every action there is an equal and opposite reaction.",
        visual_prompt="Two balls colliding, force applied",
        output_path="modules/media_generator/output/test_diagram.png",
    )
