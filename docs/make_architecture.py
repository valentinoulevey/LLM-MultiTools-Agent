"""Génère docs/architecture.png (schéma d'architecture en couches)."""
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

fig, ax = plt.subplots(figsize=(11, 8))
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis("off")

C_UI = "#4C72B0"
C_AGENT = "#55A868"
C_LLM = "#DD8452"
C_TOOLS = "#C44E52"
C_API = "#8172B3"


def box(x, y, w, h, label, color, fs=10):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.2, edgecolor="#2b2b2b", facecolor=color))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            color="white", fontsize=fs, weight="bold")


def arrow(x1, y1, x2, y2, style="-|>", color="#444444", ls="-"):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=15,
        linewidth=1.6, color=color, linestyle=ls,
        connectionstyle="arc3,rad=0"))


ax.text(5.5, 7.6, "LLM MultiTools Autonomous Travel Agent",
        ha="center", fontsize=16, weight="bold")
ax.text(5.5, 7.2, "Architecture ReAct  •  LangGraph  •  OpenRouter",
        ha="center", fontsize=10, color="#555555")

# Couche 1 : UI
box(3.9, 6.1, 3.2, 0.8, "Interface Streamlit  (chat + sidebar)", C_UI, 10)

# Couche 2 : Agent (boucle ReAct) - cadre
ax.add_patch(FancyBboxPatch((1.4, 3.55), 8.2, 2.1,
             boxstyle="round,pad=0.02,rounding_size=0.06",
             linewidth=1.4, edgecolor=C_AGENT, facecolor="#eaf3ec"))
ax.text(1.65, 5.42, "Agent LangGraph — StateGraph (boucle ReAct)",
        fontsize=9.5, color=C_AGENT, weight="bold")

box(2.0, 4.0, 2.0, 0.95, "reasoning\n(décision)", C_AGENT, 9)
box(4.5, 4.0, 2.0, 0.95, "tools\n(exécuteur)", C_AGENT, 9)
box(7.0, 4.0, 2.0, 0.95, "respond\n(réponse)", C_AGENT, 9)
box(2.0, 2.35, 2.0, 0.8, "LLM OpenRouter", C_LLM, 9)

# Couche 3 : Outils
tools = ["get_weather", "compare_weather", "search_activity",
         "get_transport_route", "estimate_budget", "build_simple_itinerary"]
for i, t in enumerate(tools):
    col = i % 3
    row = i // 3
    box(0.4 + col * 3.5, 1.15 - row * 0.85, 3.2, 0.65, t, C_TOOLS, 8.5)

# Couche 4 : APIs (bandeau)
box(0.4, -1.15, 10.3, 0.6,
    "APIs externes :  Open-Meteo  •  Nominatim (OSM)  •  Overpass (OSM)  •  OSRM",
    C_API, 9.5)
ax.set_ylim(-1.4, 8)

# Flèches
arrow(5.5, 6.1, 5.5, 5.65)                       # UI -> agent
arrow(4.0, 4.47, 4.5, 4.47)                      # reasoning -> tools
arrow(6.5, 4.47, 7.0, 4.47)                      # tools -> respond
arrow(4.5, 4.15, 4.0, 4.15, color="#999999", ls=(0,(4,3)))  # loop back tools->reasoning
ax.text(4.25, 3.78, "boucle", fontsize=7, color="#999999", ha="center")
arrow(3.0, 4.0, 3.0, 3.15, style="<|-|>", color="#DD8452")   # reasoning <-> LLM
arrow(5.5, 4.0, 4.0, 1.35)                       # tools -> outils
arrow(3.5, 0.5, 3.0, -0.55)                      # outils -> APIs

handles = [
    mpatches.Patch(color=C_UI, label="Interface"),
    mpatches.Patch(color=C_AGENT, label="Agent (LangGraph)"),
    mpatches.Patch(color=C_LLM, label="LLM"),
    mpatches.Patch(color=C_TOOLS, label="Outils"),
    mpatches.Patch(color=C_API, label="APIs externes"),
]
ax.legend(handles=handles, loc="upper right", fontsize=8.5, frameon=True)

plt.savefig("docs/architecture.png", dpi=150, bbox_inches="tight")
print("docs/architecture.png généré.")
