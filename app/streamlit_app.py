"""Interface Streamlit de l'agent de voyage multi-outils."""
from __future__ import annotations

import os
import sys
import uuid

# Permet de lancer l'app depuis la racine du dépôt (imports absolus).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402

from agent.graph import build_agent  # noqa: E402
from llm.model import DEFAULT_MODEL  # noqa: E402
from memory.checkpointer import get_checkpointer  # noqa: E402

load_dotenv()

st.set_page_config(page_title="City Trip Assistant", page_icon="🧭", layout="centered")

APIS = [
    "Open-Meteo (météo + géocodage)",
    "Nominatim / OpenStreetMap (fallback géocodage)",
    "Overpass / OpenStreetMap (activités)",
    "OSRM (itinéraires)",
]


@st.cache_resource(show_spinner=False)
def load_agent():
    """Compile l'agent une seule fois (mis en cache par Streamlit)."""
    return build_agent(checkpointer=get_checkpointer())


def reset_conversation() -> None:
    """Réinitialise l'historique et le fil de mémoire."""
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())


# --- Initialisation de l'état ---------------------------------------------
if "messages" not in st.session_state:
    reset_conversation()

# --- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.title("🧭 City Trip Assistant")
    st.caption("Agent LLM multi-outils (ReAct • LangGraph)")

    st.subheader("⚙️ Modèle")
    st.code(os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL), language=None)

    st.subheader("🔌 APIs actives")
    for api in APIS:
        st.markdown(f"- {api}")

    st.subheader("📖 À propos")
    st.markdown(
        "Assistant de voyage urbain capable de raisonner, choisir des outils, "
        "appeler des APIs temps réel (météo, activités, transport, budget) et "
        "composer un itinéraire personnalisé."
    )

    st.divider()
    if st.button("🔄 Réinitialiser la conversation", use_container_width=True):
        reset_conversation()
        st.rerun()

# --- En-tête ---------------------------------------------------------------
st.title("Assistant de voyage 🗺️")
st.caption(
    "Exemples : « Quel temps fera-t-il demain à Paris ? » · "
    "« Organise-moi une sortie à Montmartre pour 4 personnes avec 40€/personne »"
)

# --- Vérification de la clé API -------------------------------------------
if not os.getenv("OPENROUTER_API_KEY"):
    st.warning(
        "⚠️ `OPENROUTER_API_KEY` manquante. Copiez `.env.example` vers `.env` "
        "et renseignez votre clé pour activer l'agent."
    )

# --- Historique ------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tools"):
            st.caption("🛠️ Outils utilisés : " + ", ".join(msg["tools"]))

# --- Saisie utilisateur ----------------------------------------------------
if prompt := st.chat_input("Posez votre question de voyage…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Raisonnement en cours…"):
            try:
                agent = load_agent()
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = agent.invoke(
                    {"messages": [HumanMessage(content=prompt)], "tools_used": []},
                    config=config,
                )
                answer = result.get("final_answer") or result["messages"][-1].content
                tools_used = result.get("tools_used", [])
            except Exception as exc:  # noqa: BLE001
                answer = f"❌ Une erreur est survenue : {exc}"
                tools_used = []

        st.markdown(answer)
        if tools_used:
            st.caption("🛠️ Outils utilisés : " + ", ".join(tools_used))

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "tools": tools_used}
    )
