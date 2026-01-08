#%%

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams['font.sans-serif'] = ['Trebuchet MS']

# Parameters
gm = 40e-3    # 40 mS
ro = 100e3    # 100 kOhm
CL = 10e-12   # 10 pF

# Symbolic Values Calculation
# DC Gain: A0 = gm * ro
A0 = gm * ro
A0_db = 20 * np.log10(A0)
# Pole Frequency (rad/s): w_p = 1 / (ro * CL)
w_p = 1 / (ro * CL)
# Unity Gain Frequency (approx): w_u = gm / CL
w_u = gm / CL

# Frequency Range (rad/s)
w = np.logspace(np.log10(w_p) - 2, np.log10(w_u) + 1.5, 1000)
s = 1j * w

# Transfer Function
# H(s) = -gm*ro / (1 + s*CL*ro)
H = -gm * ro / (1 + s * CL * ro)

# Magnitude (dB) and Phase (deg)
mag_db = 20 * np.log10(np.abs(H))
phase_deg = np.angle(H, deg=True)

# Unwrap phase to handle the 180 -> 90 transition cleanly
# (numpy.angle might wrap to -180, we want continuous positive representation here)
phase_deg = np.unwrap(np.deg2rad(phase_deg)) * 180 / np.pi
# Shift to positive [90, 180] range if it defaulted to negative
if np.mean(phase_deg) < 0:
    phase_deg += 360

# Plotting
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax_mag, ax_phase) = plt.subplots(1, 2, figsize=(4.5, 2.5),dpi=600)

# 1. Magnitude Plot
ax_mag.semilogx(w, mag_db, color='royalblue', linewidth=2)
ax_mag.set_title('Magnitude Response')
ax_mag.set_ylabel('Magnitude (dB)')
ax_mag.set_xlabel('$\omega$ (rad/s)')

# Symbolic Ticks (Magnitude)
ax_mag.set_yticks([0, A0_db])
ax_mag.set_yticklabels([r'$0 \mathrm{dB}$', r'$g_m r_o$'])
ax_mag.set_xticks([w_p])
ax_mag.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_mag.grid(True)

# 2. Phase Plot
ax_phase.semilogx(w, phase_deg, color='darkorange', linewidth=2)
ax_phase.set_title('Phase Response')
ax_phase.set_ylabel('Phase (degrees)')
ax_phase.set_xlabel('$\omega$ (rad/s)')

# Symbolic Ticks (Phase X-axis only)
ax_phase.set_xticks([w_p])
ax_phase.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
# Standard Ticks (Phase Y-axis)
ax_phase.set_yticks([90, 135, 180])
ax_phase.grid(True)

plt.tight_layout()
plt.savefig('figures/celoadcapav.svg')

#%%
# ---------------------------------------------------------
# Cell: Output Impedance (ZO)
# ---------------------------------------------------------

# Definition: ZO = ro || (1/sCL)
# ZO = ro / (1 + s*CL*ro)
ZO = ro / (1 + s * CL * ro)

# Magnitude (dB) and Phase (deg) for Impedance
# Note: 20*log10(Ohms) is standard for impedance plots
zo_mag_db = 20 * np.log10(np.abs(ZO))
zo_phase_deg = np.angle(ZO, deg=True)

# Plotting
fig, (ax_mag, ax_phase) = plt.subplots(1, 2, figsize=(4.5, 2.5), dpi=600)

# 1. Magnitude Plot
ax_mag.semilogx(w, zo_mag_db, color='forestgreen', linewidth=2)
ax_mag.set_title(r'Output Impedance ($Z_{out}$)')
ax_mag.set_ylabel(r'$|Z_{out}|$ (dB$\Omega$)')
ax_mag.set_xlabel(r'$\omega$ (rad/s)')

# Symbolic Ticks (Magnitude)
# DC Impedance is ro
ro_db = 20 * np.log10(ro)
ax_mag.set_yticks([ro_db])
ax_mag.set_yticklabels([r'$r_o$'])
# Pole location is same as TF
ax_mag.set_xticks([w_p])
ax_mag.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_mag.grid(True)

# 2. Phase Plot
ax_phase.semilogx(w, zo_phase_deg, color='crimson', linewidth=2)
ax_phase.set_title('Phase')
ax_phase.set_ylabel('Phase (degrees)')
ax_phase.set_xlabel(r'$\omega$ (rad/s)')

# Symbolic Ticks (Phase)
ax_phase.set_xticks([w_p])
ax_phase.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_phase.set_yticks([0, -45, -90])
ax_phase.grid(True)

plt.tight_layout()
plt.savefig('figures/zout_response.svg')

#%%
# ---------------------------------------------------------
# Cell: Transconductance (GM)
# ---------------------------------------------------------

# Definition: For a simple CS stage, Gm is constant gm (ignoring transit time)
GM = np.full_like(s, gm, dtype=complex)

# Magnitude (dB) and Phase (deg)
# 20*log10(Siemens)
gm_mag_db = 20 * np.log10(np.abs(GM))
gm_phase_deg = np.angle(GM, deg=True)

# Plotting
fig, (ax_mag, ax_phase) = plt.subplots(1, 2, figsize=(4.5, 2.5), dpi=600)

# 1. Magnitude Plot
ax_mag.semilogx(w, gm_mag_db, color='purple', linewidth=2)
ax_mag.set_title(r'Transconductance ($G_m$)')
ax_mag.set_ylabel(r'$|G_m|$ (dBS)')
ax_mag.set_xlabel(r'$\omega$ (rad/s)')

# Symbolic Ticks (Magnitude)
gm_db_val = 20 * np.log10(gm)
ax_mag.set_yticks([gm_db_val])
ax_mag.set_yticklabels([r'$g_m$'])
# Remove X ticks as it's constant, or keep reference
ax_mag.set_xticks([w_p])
ax_mag.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_mag.grid(True)

# 2. Phase Plot
ax_phase.semilogx(w, gm_phase_deg, color='brown', linewidth=2)
ax_phase.set_title('Phase')
ax_phase.set_ylabel('Phase (degrees)')
ax_phase.set_xlabel(r'$\omega$ (rad/s)')
ax_phase.set_ylim(-10, 10) # Zoom in as it's 0

ax_phase.set_xticks([w_p])
ax_phase.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_phase.set_yticks([0])
ax_phase.grid(True)

plt.tight_layout()
plt.savefig('figures/gm_response.svg')

#%%
# ---------------------------------------------------------
# Cell: Input Impedance (ZI)
# ---------------------------------------------------------

# Additional parasitic parameters for Miller Effect calc
rpi = 4e3

ZI=rpi*s/s

# Magnitude (dB) and Phase (deg)
zi_mag_db = 20 * np.log10(np.abs(ZI))
zi_phase_deg = np.angle(ZI, deg=True)

# Plotting
fig, (ax_mag, ax_phase) = plt.subplots(1, 2, figsize=(4.5, 2.5), dpi=600)

# 1. Magnitude Plot
ax_mag.semilogx(w, zi_mag_db, color='teal', linewidth=2)
ax_mag.set_title(r'Input Impedance ($Z_{in}$)')
ax_mag.set_ylabel(r'$|Z_{in}|$ (dB$\Omega$)')
ax_mag.set_xlabel(r'$\omega$ (rad/s)')

# Symbolic Ticks (Magnitude)
# At the pole frequency, the gain drops, reducing Miller capacitance.
# We can mark the approximate low-freq impedance point if desired, 
# but a purely capacitive slope is cleaner without complex labels.
ax_mag.set_xticks([w_p])
ax_mag.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_mag.grid(True)

# 2. Phase Plot
ax_phase.semilogx(w, zi_phase_deg, color='goldenrod', linewidth=2)
ax_phase.set_title('Phase')
ax_phase.set_ylabel('Phase (degrees)')
ax_phase.set_xlabel(r'$\omega$ (rad/s)')

# The phase will shift from -90 (pure cap) due to the resistive component 
# of the Miller effect near the pole.
ax_phase.set_xticks([w_p])
ax_phase.set_xticklabels([r'$\frac{1}{r_o C_L}$'])
ax_phase.set_yticks([-90])
ax_phase.grid(True)

plt.tight_layout()
plt.savefig('figures/zin_response.svg')