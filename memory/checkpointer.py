"""Gestion de la mémoire conversationnelle via LangGraph.

On utilise ``MemorySaver`` (mémoire en RAM) : combiné à un ``thread_id`` dans la
config d'exécution, il permet à l'agent de se souvenir des tours précédents.
Pour une persistance durable, on pourrait remplacer par ``SqliteSaver`` ou
``PostgresSaver`` sans changer le reste du code.
"""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer() -> MemorySaver:
    """Retourne un checkpointer mémoire pour LangGraph."""
    return MemorySaver()
