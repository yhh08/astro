"""
main.py
지구과학Ⅱ: 케플러 법칙 + 좌표계 변환 + 천동설/지동설 역행운동 비교
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("화성의 역행운동: 천동설 vs 지동설")

# ── 궤도요소 (근사값) ──────────────────────────────
EARTH = dict(a=1.0, e=0.0167, period=365.256, M0=100.46)
MARS  = dict(a=1.524, e=0.0934, period=686.98, M0=19.35)
OBLIQUITY = 23.4393  # 황도경사각(deg)


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


def ecliptic_to_equatorial(x, y, z=0):
    eps = np.radians(OBLIQUITY)
    y_eq = y * np.cos(eps) - z * np.sin(eps)
    z_eq = y * np.sin(eps) + z * np.cos(eps)
    ra = np.degrees(np.arctan2(y_eq, x)) % 360
    dec = np.degrees(np.arcsin(z_eq / np.sqrt(x**2 + y_eq**2 + z_eq**2)))
    return ra, dec


def equatorial_to_horizontal(ra, dec, lst_deg, lat_deg):
    H = np.radians(lst_deg - ra)
    lat, dec = np.radians(lat_deg), np.radians(dec)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(H))
    cos_az = (np.sin(dec) - np.sin(lat) * np.sin(alt)) / (np.cos(lat) * np.cos(alt))
    az = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
    az = 360 - az if np.sin(H) > 0 else az
    return np.degrees(alt), az


def copernican_longitude(t_days):
    ex, ey = planet_xy(EARTH, t_days)
    mx, my = planet_xy(MARS, t_days)
    return np.degrees(np.arctan2(my - ey, mx - ex)) % 360


def ptolemaic_longitude(t_days, deferent_r=1.0, epicycle_r=0.4,
                         deferent_period=780, epicycle_period=687):
    theta_d = np.radians(360 * t_days / deferent_period)
    cx, cy = deferent_r * np.cos(theta_d), deferent_r * np.sin(theta_d)
    theta_e = np.radians(360 * t_days / epicycle_period)
    mx = cx + epicycle_r * np.cos(theta_e)
    my = cy + epicycle_r * np.sin(theta_e)
    return np.degrees(np.arctan2(my, mx)) % 360


# ── (A) 역행운동 비교 그래프 ─────────────────────
st.header("1. 역행운동 비교")
t = np.arange(0, 780, 5)
lon_cop = np.array([copernican_longitude(d) for d in t])
lon_ptol = np.array([ptolemaic_longitude(d) for d in t])

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(t, lon_cop, label="Copernicus/Kepler model")
ax.plot(t, lon_ptol, "--", label="Ptolemy epicycle model")
ax.set_xlabel("Days")
ax.set_ylabel("Mars apparent longitude (deg)")
ax.set_title("Mars Retrograde Motion: Two Models")
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)

# ── (B) 좌표계 변환 예시 ──────────────────────────
st.header("2. 좌표계 변환 (황도 → 적도 → 지평)")
day = st.slider("경과일 (day)", 0, 780, 100)
lat = st.slider("관측자 위도 (deg)", -90, 90, 37)
lst = st.slider("지방항성시 LST (deg)", 0, 360, 150)

ex, ey = planet_xy(EARTH, day)
mx, my = planet_xy(MARS, day)
ra, dec = ecliptic_to_equatorial(mx - ex, my - ey)
alt, az = equatorial_to_horizontal(ra, dec, lst_deg=lst, lat_deg=lat)

st.write(f"**적경(RA)**: {ra:.2f}°")
st.write(f"**적위(Dec)**: {dec:.2f}°")
st.write(f"**고도(Alt)**: {alt:.2f}°")
st.write(f"**방위각(Az)**: {az:.2f}°")
