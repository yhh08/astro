"""
main.py
지구과학Ⅱ: 케플러 법칙 + 좌표계 변환 + 천동설/지동설 역행운동 비교 (Streamlit 앱)
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("화성의 역행운동: 천동설 vs 지동설")

# ── 궤도요소 (근사값) ──────────────────────────────
EARTH = dict(a=1.0, e=0.0167, period=365.256, M0=100.46)
MARS  = dict(a=1.524, e=0.0934, period=686.98, M0=19.35)
OBLIQUITY = 23.4393  # 황도경사각(deg)


# ── 1. 케플러 방정식 & 궤도 위치 계산 ──────────────
def solve_kepler(M, e):
    M = np.radians(M)
    E = M
    for _ in range(50):
        E -= (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E


def planet_xy(elements, t_days):
    """공전 기준시각(t_days)에서의 태양중심 황도좌표 (x, y)"""
    n = 360.0 / elements["period"]
    M = (elements["M0"] + n * t_days) % 360.0
    E = solve_kepler(M, elements["e"])
    a, e = elements["a"], elements["e"]
    x = a * (np.cos(E) - e)
    y = a * np.sqrt(1 - e**2) * np.sin(E)
    return x, y


# ── 2. 좌표계 변환: 황도 → 적도 → 지평 ─────────────
def ecliptic_to_equatorial(x, y, z=0):
    eps = np.radians(OBLIQUITY)
    y_eq = y * np.cos(eps) - z * np.sin(eps)
    z_eq = y * np.sin(eps) + z * np.cos(eps)
    ra = np.degrees(np.arctan2(y_eq, x)) % 360
    dec = np.degrees(np.arcsin(z_eq / np.sqrt(x**2 + y_eq**2 + z_eq**2)))
    return ra, dec


def equatorial_to_horizontal(ra, dec, lst_deg, lat_deg):
    """LST(지방항성시, deg)와 관측자 위도(deg)로 고도/방위각 계산"""
    H = np.radians(lst_deg - ra)
    lat_r, dec_r = np.radians(lat_deg), np.radians(dec)
    alt = np.arcsin(np.sin(dec_r) * np.sin(lat_r) + np.cos(dec_r) * np.cos(lat_r) * np.cos(H))
    cos_az = (np.sin(dec_r) - np.sin(lat_r) * np.sin(alt)) / (np.cos(lat_r) * np.cos(alt))
    az = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
    az = 360 - az if np.sin(H) > 0 else az
    return np.degrees(alt), az


# ── 3. 천동설(주전원) vs 지동설(케플러) 겉보기 황경 ─
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

day = st.slider("경과일 (day)", 0, 780, 100)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(t, lon_cop, label="Copernicus/Kepler model")
ax.plot(t, lon_ptol, "--", label="Ptolemy epicycle model")

current_lon = copernican_longitude(day)
ax.plot(day, current_lon, "ro", markersize=10, label="현재 위치 (슬라이더)")

ax.set_xlabel("Days")
ax.set_ylabel("Mars apparent longitude (deg)")
ax.set_title("Mars Retrograde Motion: Two Models")
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)

# ── (B) 좌표계 변환 예시 ──────────────────────────
st.header("2. 좌표계 변환 (황도 → 적도 → 지평)")

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

if alt < 0:
    st.warning("현재 화성은 지평선 아래에 있어 관측할 수 없습니다.")
else:
    st.success(f"화성은 고도 {alt:.1f}°, 방위각 {az:.1f}° 방향에서 보입니다.")
