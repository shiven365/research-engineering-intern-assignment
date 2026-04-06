import os
import pickle
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
INDEX_PATH = os.getenv("INDEX_PATH", str(Path(__file__).resolve().parents[2] / "embeddings.index"))
ID_MAP_PATH = os.getenv("ID_MAP_PATH", str(Path(__file__).resolve().parents[2] / "id_map.pkl"))

_MODEL: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


def build_index(texts: list[str], post_ids: list[str]) -> tuple[faiss.IndexFlatIP, list[str], np.ndarray]:
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    vectors = np.array(embeddings, dtype=np.float32)
    index.add(vectors)

    faiss.write_index(index, INDEX_PATH)
    with open(ID_MAP_PATH, "wb") as f:
        pickle.dump(post_ids, f)

    return index, post_ids, vectors


def load_index() -> tuple[faiss.Index | None, list[str] | None]:
    if not Path(INDEX_PATH).exists() or not Path(ID_MAP_PATH).exists():
        return None, None

    index = faiss.read_index(INDEX_PATH)
    with open(ID_MAP_PATH, "rb") as f:
        id_map = pickle.load(f)

    return index, id_map


def semantic_search(query: str, index: faiss.Index, id_map: list[str], k: int = 10) -> list[dict[str, Any]]:
    model = get_model()

    if not query or len(query.strip()) < 2:
        return []

    query_vec = model.encode([query], normalize_embeddings=True)
    scores, indices = index.search(np.array(query_vec, dtype=np.float32), k)

    results: list[dict[str, Any]] = []
    for idx, score in zip(indices[0], scores[0]):
        if idx >= 0 and score > 0.1:
            results.append({"post_id": id_map[idx], "similarity_score": float(score)})

    return results
