"""Fabrique du modèle de langage.

On s'appuie sur OpenRouter (https://openrouter.ai), dont l'API est compatible
OpenAI. On peut donc réutiliser ``ChatOpenAI`` de ``langchain-openai`` en
pointant simplement ``base_url`` vers OpenRouter.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b:free")


def get_llm(model: str | None = None, temperature: float = 0.3) -> ChatOpenAI:
    """Instancie le client LLM configuré pour OpenRouter.

    Args:
        model: Identifiant OpenRouter du modèle. Si ``None``, on utilise
            la variable d'environnement ``OPENROUTER_MODEL`` ou le défaut.
        temperature: Créativité du modèle (0 = déterministe).

    Returns:
        Un ``ChatOpenAI`` prêt à être utilisé (et à recevoir ``bind_tools``).

    Raises:
        ValueError: si la clé API OpenRouter est absente.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY est manquante. "
            "Copiez .env.example vers .env et renseignez votre clé."
        )

    chosen_model = model or DEFAULT_MODEL
    logger.info("Initialisation du LLM OpenRouter : %s", chosen_model)

    return ChatOpenAI(
        model=chosen_model,
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
        timeout=60,
        max_retries=2,
        default_headers={
            "HTTP-Referer": os.getenv("APP_REFERER", ""),
            "X-Title": os.getenv("APP_TITLE", "LLM MultiTools Travel Agent"),
        },
    )
