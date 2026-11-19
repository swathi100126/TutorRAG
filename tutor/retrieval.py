import streamlit as st

from tutor.chunking import load_chunks
from tutor.config import COLLECTION_NAME, STORE_DIR, TOP_K
from tutor.documents import notes_fingerprint
from tutor.embeddings import embed_query, embed_texts


class PrecomputedEmbeddings:
    """Stop Chroma from downloading a second embedding model."""

    def __call__(self, input):
        raise RuntimeError("Embeddings are created before they are stored.")

    def name(self):
        return "precomputed"

    def embed_query(self, input):
        return self(input)


def open_store(fingerprint: str):
    """Open the saved vectors, or build them when the notes have changed."""
    import chromadb

    STORE_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(STORE_DIR))
    existing = {collection.name for collection in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(
            COLLECTION_NAME,
            embedding_function=PrecomputedEmbeddings(),
        )
        stored = (collection.metadata or {}).get("fingerprint")
        if stored == fingerprint and collection.count() > 0:
            return collection
        client.delete_collection(COLLECTION_NAME)

    chunks = load_chunks()
    vectors = embed_texts([chunk["text"] for chunk in chunks])
    collection = client.create_collection(
        COLLECTION_NAME,
        embedding_function=PrecomputedEmbeddings(),
        metadata={"hnsw:space": "cosine", "fingerprint": fingerprint},
    )
    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=vectors,
        metadatas=[
            {
                "title": chunk["title"],
                "topic": chunk["topic"],
                "section": chunk["section"],
                "section_number": chunk["section_number"],
                "source": chunk["source"],
            }
            for chunk in chunks
        ],
    )
    return collection


@st.cache_resource
def get_store(fingerprint: str):
    return open_store(fingerprint)


def retrieve(question: str, current_topic: str) -> tuple[list[str], list[str]]:
    """Return the closest note texts and their title-and-section labels."""
    collection = get_store(notes_fingerprint())
    vector = embed_query(f"{current_topic}\n{question}")
    found = collection.query(
        query_embeddings=[vector],
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )
    documents = found["documents"][0] if found["documents"] else []
    metadatas = found["metadatas"][0] if found["metadatas"] else []
    sources = []
    for meta in metadatas:
        meta = meta or {}
        title = meta.get("title") or meta.get("source")
        number = meta.get("section_number")
        if not title:
            continue
        label = f"{title}, section {number}" if number else title
        if label not in sources:
            sources.append(label)
    return documents, sources
