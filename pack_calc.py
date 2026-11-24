"""
EV battery pack calculator + plots
Generates: pack_config.png, discharge_curve.png, crate_time.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Cell parameters (typical 18650 Li-ion, change as needed) ----------
V_NOM = 3.7      # V, nominal
V_MAX = 4.2      # V, fully charged
V_MIN = 3.0      # V, cut-off
CELL_AH = 3.0    # Ah per cell

def pack_specs(s, p, v=V_NOM, ah=CELL_AH):
    """Return (voltage V, capacity Ah, energy Wh) of an sSpP pack."""
    volt = s * v
    cap = p * ah
    return volt, cap, volt * cap

# ---------- Example: 13S4P ----------
S, P = 13, 4
v, c, e = pack_specs(S, P)
print(f"{S}S{P}P pack -> {v:.1f} V nominal, {c:.1f} Ah, {e:.1f} Wh")
print(f"Full charge: {S*V_MAX:.1f} V | Cut-off: {S*V_MIN:.1f} V | Cells: {S*P}")

# ---------- Plot 1: voltage and energy vs series count (P fixed) ----------
s_vals = np.arange(4, 25)
volts = [pack_specs(s, P)[0] for s in s_vals]
energy = [pack_specs(s, P)[2] for s in s_vals]

fig, ax1 = plt.subplots(figsize=(7, 4))
ax1.plot(s_vals, volts, "o-", color="tab:blue")
ax1.set_xlabel("Cells in series (S)")
ax1.set_ylabel("Pack voltage (V)", color="tab:blue")
ax2 = ax1.twinx()
ax2.plot(s_vals, energy, "s--", color="tab:orange")
ax2.set_ylabel("Pack energy (Wh)", color="tab:orange")
ax1.set_title(f"Effect of series count (P = {P}, {CELL_AH} Ah cells)")
ax1.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("pack_config.png", dpi=150)
plt.close(fig)

# ---------- Plot 2: illustrative discharge curve of one cell ----------
# NOTE: simplified model for illustration, NOT measured data.
soc = np.linspace(1, 0, 200)                       # 100% -> 0%
v_cell = (V_MIN
          + (V_NOM - V_MIN) * (1 - np.exp(-6 * soc)) / (1 - np.exp(-6)) * 0.8
          + (V_MAX - V_NOM) * soc**3 * 1.0
          + 0.55 * soc)
v_cell = np.clip(v_cell, V_MIN, V_MAX)
v_cell = V_MIN + (v_cell - v_cell.min()) / (v_cell.max() - v_cell.min()) * (V_MAX - V_MIN)

plt.figure(figsize=(7, 4))
plt.plot((1 - soc) * CELL_AH, v_cell, color="tab:green")
plt.axhline(V_MIN, ls="--", color="red", label=f"Cut-off {V_MIN} V")
plt.axhline(V_MAX, ls="--", color="gray", label=f"Full {V_MAX} V")
plt.xlabel("Discharged capacity (Ah)")
plt.ylabel("Cell voltage (V)")
plt.title("Illustrative Li-ion discharge curve (simplified model)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("discharge_curve.png", dpi=150)
plt.close()

# ---------- Plot 3: C-rate vs discharge time and pack current ----------
c_rates = np.array([0.2, 0.5, 1, 2, 3, 5])
time_min = 60 / c_rates                 # t (min) = 60 / C
current = c_rates * c                   # I = C * capacity of pack

fig, ax1 = plt.subplots(figsize=(7, 4))
ax1.bar(range(len(c_rates)), time_min, color="tab:purple", alpha=0.7)
ax1.set_xticks(range(len(c_rates)))
ax1.set_xticklabels([f"{x}C" for x in c_rates])
ax1.set_ylabel("Ideal discharge time (min)")
ax1.set_xlabel("C-rate")
ax2 = ax1.twinx()
ax2.plot(range(len(c_rates)), current, "ko-")
ax2.set_ylabel(f"Pack current (A) for {S}S{P}P")
ax1.set_title("C-rate: discharge time vs current")
fig.tight_layout()
fig.savefig("crate_time.png", dpi=150)
plt.close(fig)
print("Saved 3 PNGs")
