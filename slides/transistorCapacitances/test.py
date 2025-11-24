
#%%

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- Configuration & Parameters ---
# Define system parameters to mimic the generic bandpass shape
f_L = 100.0      # Lower cutoff frequency (Hz)
f_H = 100_000.0  # Upper cutoff frequency (Hz)
A_mid_dB = 40.0  # Midband gain in dB

# Derived angular frequencies
w_L = 2 * np.pi * f_L
w_H = 2 * np.pi * f_H
A_mid = 10**(A_mid_dB / 20.0)

# --- System Modeling ---
# Create a Transfer Function: H(s) = A_mid * (s / (s + w_L)) * (w_H / (s + w_H))
# This represents a high-pass stage and a low-pass stage in series.

# Numerator: A_mid * w_H * s  -> [A_mid * w_H, 0]
num = [A_mid * w_H, 0]

# Denominator: (s + w_L) * (s + w_H) = s^2 + s(w_L + w_H) + w_L*w_H
den = [1, w_L + w_H, w_L * w_H]

# Create the system
sys = signal.TransferFunction(num, den)

# Generate frequency range for plotting (logarithmic)
# Go slightly beyond f_L/10 and f_H*10 for visual margins
f = np.logspace(np.log10(f_L/50), np.log10(f_H*50), 100)
w = 2 * np.pi * f

# Calculate Bode plot
w, mag, phase = signal.bode(sys, w)

# --- Plotting Setup ---
# Use a color similar to the reference image (cyan/light blue)
line_color = '#00AEEF' 
text_color = '#008AC0'
gray_color = '#555555'

fig, ax = plt.subplots(figsize=(5, 2.5),dpi=600)

# Plot the magnitude response
ax.semilogx(f, mag, color=line_color, linewidth=2.5)

# --- Visual Styling & Axes ---

# Hide top and right spines
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)

# Move left and bottom spines to zero/edges
# ax.spines['left'].set_position(('outward', 10))
# ax.spines['bottom'].set_position(('outward', 10))

# Add arrows to the ends of the axes
# (Matplotlib doesn't have built-in axis arrows, so we draw them)
# ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
# ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

# Set labels
ax.set_xlabel(r'$f$ (Hz)' + '\n(log scale)', fontsize=12, loc='right')
ax.set_ylabel(r'$\left| \frac{V_o}{V_{sig}} \right|$ (dB)', fontsize=12, loc='top', rotation=0)

# Limit y-axis to look like the sketch (start from a bit below max)
y_min = 0
y_max = A_mid_dB + 10
ax.set_ylim(y_min, y_max)
ax.set_xlim(f[0], f[-1])

# --- Annotations & Markers ---

# 1. Dashed Lines for f_L and f_H
# Vertical lines
ax.vlines(x=f_L, ymin=0, ymax=A_mid_dB, colors=gray_color, linestyles='--', linewidth=1.5)
ax.vlines(x=f_H, ymin=0, ymax=A_mid_dB, colors=gray_color, linestyles='--', linewidth=1.5) # -3dB point approx

# Horizontal line at A_mid - 3dB
ax.hlines(y=A_mid_dB - 3, xmin=f_L/5, xmax=f_H*5, colors=gray_color, linestyles='--', linewidth=1.5)

# 2. X-Axis Ticks Labels (f_L, f_H)
ax.set_xticks([f_L, f_H])
ax.set_xticklabels([r'$f_L$', r'$f_H$'], fontsize=14)
# Remove standard log ticks for cleaner look matching the sketch
ax.minorticks_off()
ax.get_xaxis().set_major_formatter(plt.NullFormatter()) # Clear default numbers
# Re-add our custom text labels manually to ensure style
ax.text(f_L, -2, r'$f_L$', ha='center', va='top', fontsize=14)
ax.text(f_H, -2, r'$f_H$', ha='center', va='top', fontsize=14)

# 3. Band Labels (Low, Mid, High)
y_band_label = A_mid_dB + 5 # Height for the band arrows
# Helper to draw double arrows
def draw_dimension_arrow(x_start, x_end, y, text):
    ax.annotate(
        text='', xy=(x_start, y), xytext=(x_end, y),
        arrowprops=dict(arrowstyle='<->', color=gray_color, lw=1.5)
    )

# Low Frequency Band Arrow
# From left edge to f_L
draw_dimension_arrow(f[0], f_L, y_band_label, "")
ax.text(np.sqrt(f[0]*f_L), y_band_label, "Low-frequency\nband", 
        color=text_color, ha='center', va='center',  backgroundcolor='white', fontsize=4)

# Midband Arrow
draw_dimension_arrow(f_L, f_H, y_band_label, "")
ax.text(np.sqrt(f_L*f_H), y_band_label, "Midband", 
        color=text_color, ha='center', va='center', backgroundcolor='white', fontsize=8)

# High Frequency Band Arrow
draw_dimension_arrow(f_H, f[-1], y_band_label, "")
ax.text(np.sqrt(f_H*f[-1]), y_band_label, "High-frequency\nband", 
        color=text_color, ha='center', va='center', backgroundcolor='white',fontsize=4)

# 4. Explanatory Text (The blue bullet points)

# # Low band explanation
# ax.annotate(
#     "• Gain falls off\ndue to the effects\nof coupling and\nbypass\ncapacitors",
#     xy=(f_L/2, A_mid_dB/2), xycoords='data',
#     xytext=(-20, 0), textcoords='offset points',
#     color=text_color, ha='right', va='center', fontsize=10
# )

# # Midband explanation
# ax.annotate(
#     "• All capacitances can be neglected",
#     xy=(np.sqrt(f_L*f_H), A_mid_dB), xycoords='data',
#     xytext=(0, 15), textcoords='offset points',
#     color=text_color, ha='center', va='bottom', fontsize=10
# )

# # High band explanation
# ax.annotate(
#     "• Gain falls off\ndue to the internal\ncapacitive effects\nof the BJT or the\nMOSFET",
#     xy=(f_H*2, A_mid_dB*0.8), xycoords='data',
#     xytext=(20, 0), textcoords='offset points',
#     color=text_color, ha='left', va='center', fontsize=10
# )

# 5. 3dB Drop Indication
# Small vertical arrows between Peak and -3dB line
mid_freq_log = np.sqrt(f_L * f_H) # Geometric mean for center on log scale
# Shift slightly right of center to match image
arrow_x = mid_freq_log * 5 

# Arrow down from Peak
# ax.annotate('', xy=(arrow_x, A_mid_dB - 3), xytext=(arrow_x, A_mid_dB),
            # arrowprops=dict(arrowstyle='->', color='black', lw=1))
# Arrow up from -3dB line
# ax.annotate('', xy=(arrow_x, A_mid_dB), xytext=(arrow_x, A_mid_dB - 3),
            # arrowprops=dict(arrowstyle='->', color='black', lw=1))
# Text "3 dB"
ax.text(arrow_x, A_mid_dB-3, "3 dB", ha='center', va='center', backgroundcolor='white', fontsize=5)

# 6. Gain Label (20 log |Am|)
# Arrow from 0 to A_mid
label_x = np.sqrt(f_L * f_H)
ax.annotate(
    '', xy=(label_x, A_mid_dB), xytext=(label_x, 0),
    arrowprops=dict(arrowstyle='<->', color='black', lw=1)
)
ax.text(label_x, A_mid_dB/2, r'$20 \log |A_M|$ (dB)', 
        ha='center', va='center', fontsize=12, color=text_color, backgroundcolor='white')

plt.tight_layout()

plt.savefig("figures/midband.svg")
plt.show()


#%%

import numpy as np

import matplotlib.pyplot as plt



Cje0 = 10e-15  # Base-Emitter Junction Capacitance at zero bias (F)



V_bi = 0.7  # Built-in potential (V)

V_be = np.linspace(-1, 1, 100)  # Base-Emitter voltage (V)

C_je = Cje0 / np.sqrt(1 - V_be / V_bi)  # Base-Emitter Junction Capacitance (F)



plt.figure(figsize=(3,2), dpi=600)

plt.grid()

plt.plot(V_be, C_je * 1e15)  # Convert to pF for plotting

plt.xlabel('$V_{BE}$ (V)')

plt.ylabel('$C_{je}$ (pF)')

plt.xlim([-1, 1])

# Line for V_be = 0.7 V

plt.axvline(x=0.7, color='gray', linestyle='--')

# Label V_be at the x axis of 0.7 V

plt.text(0.7, plt.ylim()[0] - 5, '$V_{j,BE}$', verticalalignment='top', color='gray', horizontalalignment='center')



# Label C_je0

plt.plot(0, Cje0 * 1e15, 'o', color='black')  # Point at V_be = 0 V

plt.text(0, Cje0 * 1e15 + 5, '$C_{je0}$', horizontalalignment='center', color='black', verticalalignment='bottom')

plt.savefig("figures/cje.svg", transparent=True)

#%%

import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. Define Transistor Parameters (Typical RF BJT/MOSFET values)
# ==========================================
gm = 50e-3    # Transconductance (50 mS)
ro = 10e3     # Output Resistance (10 kOhm)
rpi = 2.5e3   # Input Resistance (Beta_dc / gm, assuming Beta_dc=125)
Cpi = 2.0e-12 # Input Capacitance (Cgs or Cpi) (2 pF)
Cmu = 0.5e-12 # Feedback Capacitance (Cgd or Cmu) (0.5 pF)

# Intrinsic DC Voltage Gain (The "Ceiling")
Av_intrinsic_dc = gm * ro
Av_intrinsic_db = 20 * np.log10(Av_intrinsic_dc)

# Theoretical fT calculation (for comparison)
ft_theoretical = gm / (2 * np.pi * (Cpi + Cmu))

# ==========================================
# 2. Frequency Sweep Setup
# ==========================================
# From 100 kHz to 100 GHz
f = np.logspace(5, 11, 500) 
omega = 2 * np.pi * f
s = 1j * omega

# ==========================================
# 3. Define Gain Equations based on Hybrid-Pi
# ==========================================

# --- A) Short-Circuit Current Gain (io / ii) ---
# Output is shorted (vo = 0). Cmu appears in parallel with Cpi.
# Zin_sc = rpi || (1 / s(Cpi + Cmu))
C_total_in = Cpi + Cmu
Zin_sc = rpi / (1 + s * rpi * C_total_in)
# io approx gm * vpi (ignoring feedforward Cmu current for simplicity at fT)
# vpi = ii * Zin_sc
# Current Gain = io / ii = gm * Zin_sc
Ai_sc = (gm - s*Cmu)/(1/rpi + s*(Cmu + Cpi))
Ai_sc_db = 20 * np.log10(np.abs(Ai_sc))


# --- B) Open-Circuit Voltage Gain (vo / vi) ---
# Assuming ideal voltage source drive (Rs=0) and open output (RL=inf).
# The bandwidth is limited by the output time constant (ro * Cmu).
# Derived transfer function for open circuit Hybrid-Pi:
# Av(s) = -gm*ro * (1 - s(Cmu/gm)) / (1 + s*ro*Cmu)
Numerator = -gm * ro * (1 - s * (Cmu / gm))
Denominator = (1 + s * ro * Cmu)
Av_oc = Numerator / Denominator
Av_oc_db = 20 * np.log10(np.abs(Av_oc))


# ==========================================
# 4. Plotting
# ==========================================
plt.figure(figsize=(8, 4.5))

# Plot 1: Intrinsic DC Gain Ceiling
plt.axhline(y=Av_intrinsic_db, color='grey', linestyle='--', linewidth=2, label=f'Intrinsic DC Voltage Gain ($g_m r_o$) = {Av_intrinsic_db:.1f} dB')

# Plot 2: Open-Circuit Voltage Gain
plt.semilogx(f, Av_oc_db, color='red', linewidth=2.5, label='Open-Circuit Voltage Gain ($v_o/v_i$)')

# Plot 3: Short-Circuit Current Gain (The fT curve)
plt.semilogx(f, Ai_sc_db, color='blue', linewidth=2.5, label='Short-Circuit Current Gain ($i_o/i_i$)')

# Unity Gain Line (0 dB)
plt.axhline(y=0, color='black', linestyle='-')
plt.text(1e5, 1, 'Unity Gain (0 dB)', verticalalignment='bottom')

# Annotate fT
idx_ft = np.argmin(np.abs(Ai_sc_db - 0)) # Find index closest to 0 dB
f_ft_measured = f[idx_ft]
plt.plot(f_ft_measured, 0, 'bo', markersize=10)
plt.annotate(f'$f_T$ Definition\n({f_ft_measured/1e9:.1f} GHz)', 
             xy=(f_ft_measured, 0), xytext=(f_ft_measured*0.1, -20),
             arrowprops=dict(facecolor='blue', shrink=0.05), color='blue', fontsize=12, ha='center')

# Annotate Voltage Gain Bandwidth
# Find -3dB point from DC for voltage gain
idx_3db_v = np.argmin(np.abs(Av_oc_db - (Av_intrinsic_db - 3)))
f_3db_v = f[idx_3db_v]
plt.plot(f_3db_v, Av_intrinsic_db - 3, 'ro', markersize=8)
plt.annotate(f'Voltage Gain\nBandwidth\n({f_3db_v/1e6:.1f} MHz)', 
             xy=(f_3db_v, Av_intrinsic_db - 3), xytext=(f_3db_v*0.05, Av_intrinsic_db - 30),
             arrowprops=dict(facecolor='red', shrink=0.05), color='red', fontsize=10, ha='center')


# Formatting
plt.title("Transistor ", fontsize=14)
plt.xlabel("Frequency (Hz)", fontsize=12)
plt.ylabel("Gain Magnitude (dB)", fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.6)
plt.legend(fontsize=11, loc='lower left')
plt.xlim(1e5, 1e11)
plt.ylim(-40, 70)

plt.legend(fontsize='small')

# plt.tight_layout()

plt.savefig('figures/ft.svg')
plt.show()