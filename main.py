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
# Historically, Ptolemy assumed UNIFORM CIRCULAR motion (no eccentricity),
# not the true Keplerian ellipse. We reproduce that simplification here:
# deferent = Mars' orbit approximated as a perfect circle (radius = MARS["a"],
# period = MARS["period"]), epicycle = Earth's orbit approximated as a perfect
# circle (radius = EARTH["a"], period = EARTH["period"]). Because real orbits
# are elliptical (Mars e ≈ 0.093, much larger than Earth's e ≈ 0.017), this
# circular approximation genuinely diverges from the true heliocentric
# (Keplerian) position — the divergence is the actual historical limitation
# that eventually pointed Kepler toward elliptical orbits.
def ptolemaic_positions(day):
    theta_d = np.radians((MARS["M0"] + 360.0 / MARS["period"] * day) % 360.0)
    cx, cy = MARS["a"] * np.cos(theta_d), MARS["a"] * np.sin(theta_d)

    theta_e = np.radians((EARTH["M0"] + 360.0 / EARTH["period"] * day) % 360.0)
    ex, ey = EARTH["a"] * np.cos(theta_e), EARTH["a"] * np.sin(theta_e)

    mx, my = cx - ex, cy - ey
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

    # Here the deferent and epicycle really are perfect circles (Ptolemy's
    # assumption), so the drawn circles exactly match the point's path.
    deferent_r = MARS["a"]
    epicycle_r = EARTH["a"]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(deferent_r * np.cos(theta), deferent_r * np.sin(theta), "b--", alpha=0.4, label="Deferent (~Mars orbit)")
    ax.plot(cx + epicycle_r * np.cos(theta), cy + epicycle_r * np.sin(theta), "r--", alpha=0.3, label="Epicycle (~Earth orbit)")
    ax.plot(0, 0, "o", color="blue", markersize=14, label="Earth (fixed center)")
    ax.plot(cx, cy, "x", color="gray", markersize=8, label="Epicycle center")
    ax.plot(mx, my, "ro", markersize=10, label="Mars")
    ax.plot([0, mx * 1.3], [0, my * 1.3], "g-", linewidth=1, alpha=0.6, label="Earth→Mars line of sight")

    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-2.6, 2.6)
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


def angular_diff(a, b):
    """Shortest signed angular difference a-b, wrapped to [-180, 180]."""
    return (a - b + 180) % 360 - 180


def draw_error_over_time(current_day, n_days=780, n_points=400):
    days = np.linspace(0, n_days, n_points)
    errors = []
    for d in days:
        ex, ey = planet_xy(EARTH, d)
        mx, my = planet_xy(MARS, d)
        lon_true = apparent_longitude(ex, ey, mx, my)
        _, _, pmx, pmy = ptolemaic_positions(d)
        lon_ptol = apparent_longitude(0, 0, pmx, pmy)
        errors.append(angular_diff(lon_ptol, lon_true))
    errors = np.array(errors)

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.plot(days, errors, "m-", label="Ptolemaic (circular) error vs true position")
    ax.axvline(current_day, color="green", linestyle="--", alpha=0.6, label="Current day")
    ax.set_xlabel("Elapsed days")
    ax.set_ylabel("Error (deg)")
    ax.set_title("Geocentric circular model's apparent-longitude error over one synodic cycle")
    ax.legend(loc="upper right", fontsize=8)
    return fig, errors


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

st.subheader("Error of the Geocentric (Circular) Model Over Time")
fig_err, err_array = draw_error_over_time(day)
st.pyplot(fig_err)
current_error = angular_diff(lon_ptol, lon_cop)

st.markdown(f"""
- **Heliocentric model** (true, elliptical/Keplerian orbits): Mars' direction as seen from Earth (ecliptic longitude) = **{lon_cop:.1f}°**
- **Geocentric model** (Ptolemy's assumption: perfect circles, uniform motion, no eccentricity): predicted direction = **{lon_ptol:.1f}°**
- **Error at this moment**: **{current_error:+.2f}°**
- This error exists *because* Ptolemy's model ignores orbital eccentricity. Mars'
  real eccentricity (e ≈ 0.093) is over five times Earth's (e ≈ 0.017), so treating
  Mars' orbit as a perfect circle introduces a real, measurable error — this is not
  a rounding artifact, it is the actual structural limitation of the geocentric model.
- The error chart above shows this discrepancy is not constant: it grows and shrinks
  over the course of the {780}-day synodic cycle, peaking when Mars is near
  perihelion/aphelion in its real elliptical orbit. This kind of persistent,
  systematic mismatch between predicted and observed planetary position is exactly
  what led Kepler (using Tycho Brahe's precise Mars observations) to abandon
  circular orbits in favor of ellipses.
- **Caveat for the report**: the historical Ptolemaic system also used devices like
  the *equant* to partially compensate for non-uniform motion, so real Ptolemaic
  predictions were somewhat better than this simplified circular version. This
  simulation isolates the eccentricity-approximation error specifically, as a
  clear, single-cause illustration of why circular geocentric models ultimately fail —
  it should be described as a simplified model, not a literal reconstruction of
  Ptolemy's full equant-based system.
""")
