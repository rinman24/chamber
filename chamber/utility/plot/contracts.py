"""Data contracts for plot utility."""

from dataclasses import dataclass
from datetime import datetime

from typing import List


# ----------------------------------------------------------------------------
# Plot utility DTOs


@dataclass(frozen=True)
class Observations:
    """Observations to plot on a single axis."""

    values: List  # List of observation values
    sigma: List  # Error bars not plotted if sum == 0
    label: str = ''  # Should be an empty string for abscissae


@dataclass(frozen=True)
class Plot:
    """Two dimensional plot."""

    abscissae: List[Observations]  # Independent observations
    ordinates: List[Observations]  # Dependent observations
    title: str  # Title for the plot
    x_label: str
    y_label: str
    axis: int  # Location of the plot


@dataclass(frozen=True)
class Layout:
    """Layout of a figure."""

    plots: List[Plot]  # List of plots to display
    style: str = ''  # valid pyplot.style
