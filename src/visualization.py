"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Visualization & Plotly Graphic Studio
Custom dark-mode high-contrast responsive charts for enterprise analytics
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional

DARK_THEME = {
    "paper_bgcolor": "rgba(14, 17, 23, 0.0)",
    "plot_bgcolor": "rgba(14, 17, 23, 0.0)",
    "font_color": "#E0E6ED",
    "font_family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
    "grid_color": "rgba(255, 255, 255, 0.08)",
    "accent_cyan": "#00F2FE",
    "accent_blue": "#4FACFE",
    "accent_purple": "#7F00FF",
    "accent_emerald": "#00E676",
    "accent_amber": "#FFB300",
    "accent_coral": "#FF5252"
}

def apply_chart_styling(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    """Applies premium glassmorphism dark theme styling to any Plotly chart."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.96,
            "x": 0.02,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 16, "color": DARK_THEME["font_color"], "family": DARK_THEME["font_family"]}
        },
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        plot_bgcolor=DARK_THEME["plot_bgcolor"],
        font={"color": DARK_THEME["font_color"], "family": DARK_THEME["font_family"]},
        margin=dict(l=40, r=30, t=60, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor="#1E232F",
            font_size=12,
            font_family=DARK_THEME["font_family"]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=11, color="#A0AEC0")
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=DARK_THEME["grid_color"],
        linecolor="rgba(255, 255, 255, 0.15)",
        tickfont=dict(color="#A0AEC0")
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=DARK_THEME["grid_color"],
        linecolor="rgba(255, 255, 255, 0.15)",
        tickfont=dict(color="#A0AEC0")
    )
    return fig

def plot_time_series_trend(df: pd.DataFrame, x_col: str, y_cols: List[str], title: str, colors: List[str] = None) -> go.Figure:
    fig = go.Figure()
    if colors is None:
        colors = ["#00F2FE", "#00E676", "#FFB300", "#FF5252", "#E040FB"]
        
    for i, col in enumerate(y_cols):
        c = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            mode="lines+markers",
            name=col.replace("_", " "),
            line=dict(color=c, width=3, shape="spline"),
            marker=dict(size=5, color=c),
            hovertemplate="<b>%{x}</b><br>" + col.replace("_", " ") + ": %{y:,.0f}<extra></extra>"
        ))
    return apply_chart_styling(fig, title=title)

def plot_stacked_segment_area(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    segments = [
        ("Two_Wheeler", "2-Wheelers (2W)", "#00F2FE"),
        ("Three_Wheeler", "3-Wheelers (3W)", "#4FACFE"),
        ("Four_Wheeler", "4-Wheelers / Cars (4W)", "#00E676"),
        ("Bus", "Buses & CVs", "#FFB300")
    ]
    for col, label, color in segments:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df[col],
                mode="lines",
                name=label,
                stackgroup="one",
                line=dict(width=1, color=color),
                hovertemplate="<b>%{x|%b %Y}</b><br>" + label + ": %{y:,.0f} units<extra></extra>"
            ))
    return apply_chart_styling(fig, title="Indian EV Market Evolution by Vehicle Segment (2018 - 2025)", height=450)

def plot_state_bubble_map(df_states: pd.DataFrame) -> go.Figure:
    """Geographical bubble map representation of India with coordinates."""
    fig = go.Figure()
    
    # Add coordinate scatter bubbles
    fig.add_trace(go.Scattergeo(
        lon=df_states["Longitude"],
        lat=df_states["Latitude"],
        text=df_states["State"],
        customdata=np.stack((
            df_states["Total_EV_Registrations"],
            df_states["Public_Charging_Stations"],
            df_states["EV_Penetration_Pct"],
            df_states["EVs_Per_Public_Charger"]
        ), axis=-1),
        hovertemplate=(
            "<b>%{text}</b><br><br>"
            "Total EV Registrations: %{customdata[0]:,}<br>"
            "Operational Public Chargers: %{customdata[1]:,}<br>"
            "EV Penetration: %{customdata[2]}%<br>"
            "EVs per Charger: %{customdata[3]}<extra></extra>"
        ),
        mode="markers+text",
        textposition="top center",
        marker=dict(
            size=np.sqrt(df_states["Total_EV_Registrations"]) / 18,
            sizemin=6,
            color=df_states["Total_EV_Registrations"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(
                title=dict(text="EV Registrations", font=dict(color="#E0E6ED")),
                tickfont=dict(color="#A0AEC0"),
                thickness=14,
                len=0.7
            ),
            line=dict(width=1.5, color="#00F2FE"),
            opacity=0.88
        )
    ))
    
    fig.update_layout(
        geo=dict(
            scope="asia",
            center=dict(lat=22.0, lon=82.0),
            projection_scale=3.8,
            showland=True,
            landcolor="#141923",
            showocean=True,
            oceancolor="#0A0D14",
            showlakes=True,
            lakecolor="#0A0D14",
            showcountries=True,
            countrycolor="#2A3245",
            bgcolor="rgba(0,0,0,0)"
        ),
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        margin=dict(l=0, r=0, t=40, b=0),
        height=540,
        title=dict(text="<b>Geographical EV Density & Charging Distribution Across India</b>", font=dict(color="#E0E6ED"))
    )
    return fig

def plot_state_ranking_bar(df_states: pd.DataFrame, top_n: int = 10, metric: str = "Total_EV_Registrations", title: str = "") -> go.Figure:
    df_sorted = df_states.sort_values(metric, ascending=True).tail(top_n)
    fig = go.Figure(go.Bar(
        x=df_sorted[metric],
        y=df_sorted["State"],
        orientation="h",
        marker=dict(
            color=df_sorted[metric],
            colorscale="Tealgrn",
            line=dict(color="rgba(255,255,255,0.2)", width=1)
        ),
        text=df_sorted[metric].apply(lambda v: f"{v:,.0f}"),
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>" + metric.replace("_", " ") + ": %{x:,.0f}<extra></extra>"
    ))
    return apply_chart_styling(fig, title=title or f"Top {top_n} States by {metric.replace('_', ' ')}", height=420)

def plot_oem_market_share_donut(df_oem: pd.DataFrame, segment: str, year: int) -> go.Figure:
    subset = df_oem[(df_oem["Segment"] == segment) & (df_oem["Year"] == year)]
    if subset.empty:
        subset = df_oem[df_oem["Segment"] == segment]
        
    fig = go.Figure(go.Pie(
        labels=subset["OEM"],
        values=subset["Market_Share_Pct"],
        hole=0.55,
        textinfo="label+percent",
        marker=dict(
            colors=["#00F2FE", "#4FACFE", "#00E676", "#FFB300", "#FF5252", "#9C27B0", "#E040FB", "#795548"],
            line=dict(color="#0E1117", width=2)
        ),
        hovertemplate="<b>%{label}</b><br>Market Share: %{value}%<br>Sales: %{customdata:,} units<extra></extra>",
        customdata=subset["Sales_Units"]
    ))
    fig.update_layout(
        annotations=[dict(text=f"{segment[:3]}<br>{year}", x=0.5, y=0.5, font_size=18, font_color="#00F2FE", showarrow=False)]
    )
    return apply_chart_styling(fig, title=f"{segment.replace('_', ' ')} OEM Market Share Breakdown ({year})", height=420)

def plot_actual_vs_predicted(dates, y_true, y_pred, model_name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=y_true,
        mode="lines+markers",
        name="Actual Registrations (VAHAN)",
        line=dict(color="#00E676", width=3),
        marker=dict(size=7, color="#00E676")
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=y_pred,
        mode="lines+markers",
        name=f"Predicted ({model_name})",
        line=dict(color="#00F2FE", width=3, dash="dot"),
        marker=dict(size=7, color="#00F2FE")
    ))
    return apply_chart_styling(fig, title=f"Model Performance: Actual vs Predicted Registration Volume ({model_name})", height=420)

def plot_future_forecast_fan(df_historical: pd.DataFrame, df_forecast: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    
    # Historical line
    fig.add_trace(go.Scatter(
        x=df_historical["Date"],
        y=df_historical["Total_EV_Sales"],
        mode="lines",
        name="Historical (VAHAN Recorded)",
        line=dict(color="#A0AEC0", width=2.5)
    ))
    
    # Bull case upper bound
    fig.add_trace(go.Scatter(
        x=df_forecast["Date"],
        y=df_forecast["Forecast_Bull_Case"],
        mode="lines",
        name="Bull Case (+15% Push)",
        line=dict(color="rgba(0, 242, 254, 0.4)", width=1),
        showlegend=False
    ))
    
    # Shaded band
    fig.add_trace(go.Scatter(
        x=df_forecast["Date"],
        y=df_forecast["Forecast_Bear_Case"],
        mode="lines",
        name="Confidence Corridor (Bear - Bull)",
        fill="tonexty",
        fillcolor="rgba(0, 242, 254, 0.12)",
        line=dict(color="rgba(0, 242, 254, 0.4)", width=1)
    ))
    
    # Base forecast line
    fig.add_trace(go.Scatter(
        x=df_forecast["Date"],
        y=df_forecast["Forecast_Base_Case"],
        mode="lines+markers",
        name="ML Base Projection",
        line=dict(color="#00F2FE", width=3.5, shape="spline"),
        marker=dict(size=6, color="#00F2FE")
    ))
    
    return apply_chart_styling(fig, title="Long-Horizon Predictive Trajectory & Scenario Projections (2025 - 2027)", height=450)

def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=[c.replace("_", " ") for c in corr_df.columns],
        y=[c.replace("_", " ") for c in corr_df.index],
        colorscale="RdBu_r",
        zmin=-1,
        zmax=1,
        text=corr_df.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 12, "color": "#FFFFFF"},
        colorbar=dict(title=dict(text="Pearson r", font=dict(color="#E0E6ED")), tickfont=dict(color="#A0AEC0"))
    ))
    return apply_chart_styling(fig, title="Cross-Variable Statistical Pearson Correlation Matrix", height=450)

