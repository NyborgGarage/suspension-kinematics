"""Plotting of metrics over wheel travel (matplotlib)."""

from __future__ import annotations

import matplotlib.pyplot as plt


def plot_curves(travel, curves: dict[str, list[float]], title: str = ""):
    """Plot each metric against wheel travel. curves: name -> values."""
    fig, axes = plt.subplots(len(curves), 1, sharex=True, figsize=(7, 2.4 * len(curves)))
    if len(curves) == 1:
        axes = [axes]
    for ax, (name, values) in zip(axes, curves.items()):
        ax.plot(travel, values)
        ax.set_ylabel(name)
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("Wheel travel [mm] (bump +)")
    fig.suptitle(title)
    fig.tight_layout()
    return fig
