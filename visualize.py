"""
Visualization utilities for transaction analysis.

This module provides standardized visualization functions for transaction data analysis,
reducing code duplication and ensuring consistent chart styling across the application.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any

# Default configuration
DEFAULT_COLOR_SCALE = "earth"
DEFAULT_TEMPLATE = "seaborn"
DEFAULT_HEIGHT = 500
MIN_BAR_HEIGHT = 40
LARGEST = 10


def create_horizontal_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_scale: str = DEFAULT_COLOR_SCALE,
    template: str = DEFAULT_TEMPLATE,
    text_template: str = "%{x:,.0f}/=",
    height: Optional[int] = None,
    hover_data: str = "count",
) -> go.Figure:
    """
    Create a standardized horizontal bar chart for transaction analysis.

    Args:
        data: DataFrame containing the data to plot
        x_col: Column name for x-axis values (amounts)
        y_col: Column name for y-axis values (entities)
        title: Chart title
        color_scale: Plotly color scale
        template: Plotly template
        text_template: Template for text labels on bars
        height: Chart height (auto-calculated if None)
        n_largest: Number of top entities to display

    Returns:
        Plotly figure object
    """
    if data.empty:
        return None  # type: ignore

    # Calculate dynamic height based on sorted data if not specified
    if height is None:
        height = max(DEFAULT_HEIGHT, MIN_BAR_HEIGHT)

    fig = px.bar(
        data.nlargest(LARGEST, x_col).sort_values(by=x_col, ascending=True),
        y=y_col,
        x=x_col,
        orientation="h",
        title=title,
        # color=x_col,
        color_continuous_scale=color_scale,
        template=template,
        hover_data="count",
    )

    fig.update_layout(
        height=height if height else DEFAULT_HEIGHT,
        showlegend=False,
        xaxis_title="",
        xaxis=dict(showticklabels=False),
        yaxis_title="",
        dragmode=False,
    )

    fig.update_traces(
        texttemplate=text_template,
        textposition="auto",
        hovertemplate=" %{customdata} transaction(s)",
    )

    return fig


def create_pie_chart(
    data: pd.DataFrame,
    values_col: str,
    names_col: str,
    title: str,
    template: str = DEFAULT_TEMPLATE,
    color_sequence: list = None,  # type: ignore
) -> go.Figure:
    """
    Create a standardized pie chart for transaction analysis.

    Args:
        data: DataFrame containing the data to plot
        values_col: Column name for pie slice values
        names_col: Column name for pie slice names
        title: Chart title
        template: Plotly template
        color_sequence: Color sequence for pie slices

    Returns:
        Plotly figure object
    """
    if data.empty:
        return None  # type: ignore

    if color_sequence is None:
        color_sequence = px.colors.qualitative.Set3

    fig = px.pie(
        data,
        values=values_col,
        names=names_col,
        title=title,
        color_discrete_sequence=color_sequence,
        template=template,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")

    return fig
