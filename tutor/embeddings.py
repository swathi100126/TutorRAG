import streamlit as st

from tutor.config import EMBED_MODEL


@st.cache_resource
def get_embedder():
    """Load the local embedding model once per app session."""
    from fastembed import TextEmbedding

    return TextEmbedding(EMBED_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turn note chunks into vectors."""
    return [vector.tolist() for vector in get_embedder().embed(texts)]


def embed_query(text: str) -> list[float]:
    """Turn a student question into a vector."""
    return next(get_embedder().query_embed(text)).tolist()
