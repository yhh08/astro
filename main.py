"""
main.py
Earth Science II: Geocentric vs Heliocentric Model - Visual Comparison of Mars' Apparent Position
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Where is Mars: Geocentric vs Heliocentric Model")

# ── Orbital elements (approximate) ──────────────────────────────
EARTH = dict(a=1.0, e=0.0167, period=365.256, M0=100.46)
MARS  = dict(a=1.524, e=0.0934, period=686.98, M0=19.35)


# ── Kepler's Equation & Orbital Position Calculation (Heliocentric Model) ────
def solve_kepler(M, e):
    M = np.radians(M)
    E = M
    for _ in range(50):
        E -= (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E


def planet_xy(elements, t_days):
    n = 360.0 / elements["period"]
    M = (elements["M0"] + n * t_days) % 360.0
    E = solve_kepler(M, elements["e"])
    a, e = elements["a"], elements["e"]
    x = a * (np.cos(E) - e)
    y = a * np.sqrt(1 - e**2) * np.sin(E)
    return x, y


def orbit_ring(elements, n=200):
    """Full orbital ellipse path (one revolution)"""
    xs, ys = [], []
    for M in np.linspace(0, 360, n):
        E = solve_kepler(M, elements["e"])
        a, e = elements["a"], elements["e"]
        xs.append(a * (np.cos(E) - e))
        ys.append(a * np.sqrt(1 - e**2) * np.sin(E))
    return np.array(xs), np.array(ys)


def apparent_longitude(ex, ey, mx, my):
    return np.degrees(np.arctan2(my - ey, mx - ex)) % 360


# ── Geocentric (Deferent-Epicycle) Model ─────────────────────
def ptolemaic_positions(day, deferent_r=1.0, epicycle_r=0.4,
                         deferent_period=780, epicycle_period=687):
    theta_d = np.radians(360 * day / deferent_period)
    cx, cy = deferent_r * np.cos(theta_d), deferent_r * np.sin(theta_d)
    theta_e = np.radians(360 * day / epicycle_period)
    mx = cx + epicycle_r * np.cos(theta_e)
    my = cy + epicycle_r * np.sin(theta_e)
    return cx, cy, mx, my


# ── Figure 1: Heliocentric (Copernican) Solar System Plan View ──────
def draw_copernican(day):
    ex, ey = planet_xy(EARTH, day)
    mx, my = planet_xy(MARS, day)
    e_ring_x, e_ring_y = orbit_ring(EARTH)
    m_ring_x, m_ring_y = orbit_ring(MARS)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(e_ring_x, e_ring_y, "b--", alpha=0.4, label="Earth's Orbit")
    ax.plot(m_ring_x, m_ring_y, "r--", alpha=0.4, label="Mars' Orbit")
    ax.plot(0, 0, "o", color="gold", markersize=20, label="Sun")
    ax.plot(ex, ey, "bo", markersize=10, label="Earth")
    ax.plot(mx, my, "ro", markersize=10, label="Mars")

    dx, dy = mx - ex, my - ey
    ax.plot([ex, ex + dx * 3], [ey, ey + dy * 3], "g-", linewidth=1, alpha=0.6, label="Earth→Mars line of sight")

    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect("equal")
    ax.set_title("Heliocentric (Copernican): Sun-Centered")
    ax.legend(loc="upper right", fontsize=7)
    return fig, apparent_longitude(ex, ey, mx, my)


# ── Figure 2: Geocentric (Ptolemaic) Earth-Centered View ──────
def draw_ptolemaic(day):
    cx, cy, mx, my = ptolemaic_positions(day)
    theta = np.linspace(0, 2 * np.pi, 200)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(np.cos(theta), np.sin(theta), "b--", alpha=0.4, label="Deferent")
    ax.plot(cx + 0.4 * np.cos(theta), cy + 0.4 * np.sin(theta), "r--", alpha=0.3, label="Epicycle")
    ax.plot(0, 0, "o", color="blue", markersize=14, label="Earth (fixed center)")
    ax.plot(cx, cy, "x", color="gray", markersize=8, label="Epicycle center")
    ax.plot(mx, my, "ro", markersize=10, label="Mars")
    ax.plot([0, mx * 2.5], [0, my * 2.5], "g-", linewidth=1, alpha=0.6, label="Earth→Mars line of sight")

    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect("equal")
    ax.set_title("Geocentric (Ptolemaic): Earth-Centered")
    ax.legend(loc="upper right", fontsize=7)
    return fig, apparent_longitude(0, 0, mx, my)


# ── Figure 3: Direction of Mars as Seen in the Sky (Compass) ─────
def draw_sky_compass(lon_cop, lon_ptol):
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_ylim(0, 1)
    ax.set_yticklabels([])

    ax.plot([np.radians(lon_cop)], [0.8], "bo", markersize=16, label="Heliocentric predicted direction")
    ax.plot([np.radians(lon_ptol)], [0.8], "r^", markersize=16, label="Geocentric predicted direction")
    ax.set_title("Mars' Actual Direction in the Sky (Ecliptic Longitude)", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=8)
    return fig


# ── Layout ────────────────────────────────────
day = st.slider("Elapsed days (Mars synodic period ≈ 780 days)", 0, 780, 100)

col1, col2 = st.columns(2)
fig_cop, lon_cop = draw_copernican(day)
fig_ptol, lon_ptol = draw_ptolemaic(day)

with col1:
    st.pyplot(fig_cop)
with col2:
    st.pyplot(fig_ptol)

st.subheader("Comparison of Mars' Actual Sky Position")
fig_sky = draw_sky_compass(lon_cop, lon_ptol)
st.pyplot(fig_sky)

st.markdown(f"""
- **Heliocentric model**: Calculated using the real orbital positions of Earth and Mars around the Sun, the direction of Mars as seen from Earth (ecliptic longitude) = **{lon_cop:.1f}°**
- **Geocentric model**: Calculated assuming Mars moves along a deferent-epicycle system, the direction of Mars (ecliptic longitude) = **{lon_ptol:.1f}°**
- Moving the slider to around day 285–360 shows the interval where, in the heliocentric model,
  Earth overtakes Mars in its orbit, causing Mars to appear to move briefly backward (retrograde) in the sky.
""")
