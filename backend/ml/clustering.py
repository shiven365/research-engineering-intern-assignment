from typing import Any

import numpy as np
import umap
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    import hdbscan  # type: ignore
except Exception:
    hdbscan = None


def cluster_posts(embeddings: np.ndarray, texts: list[str], n_clusters: int | None = None) -> dict[str, Any]:
    if embeddings is None or len(embeddings) == 0:
        return {
            "coords": [],
            "labels": [],
            "cluster_topics": {},
            "n_clusters_found": 0,
            "message": "Empty dataset.",
            "warnings": [],
        }

    if len(embeddings) == 1:
        return {
            "coords": [[0.0, 0.0]],
            "labels": [0],
            "cluster_topics": {"0": "Insufficient data"},
            "n_clusters_found": 1,
            "message": "Single post available.",
            "warnings": ["Insufficient data for clustering."],
        }

    warnings: list[str] = []

    reducer = umap.UMAP(
        n_components=2,
        metric="cosine",
        n_neighbors=min(15, max(2, len(embeddings) - 1)),
        min_dist=0.1,
        random_state=42,
    )
    coords_2d = reducer.fit_transform(embeddings)

    if n_clusters is None or n_clusters == 0:
        if hdbscan is not None:
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=5,
                min_samples=3,
                metric="euclidean",
                cluster_selection_method="eom",
            )
            labels = clusterer.fit_predict(coords_2d)
        else:
            warnings.append("hdbscan unavailable; used DBSCAN fallback.")
            labels = DBSCAN(eps=0.5, min_samples=3).fit_predict(coords_2d)
    else:
        requested = n_clusters
        if n_clusters <= 1:
            n_clusters = 2
            warnings.append("n_clusters=1 is invalid; forced to 2.")
        max_allowed = max(2, len(embeddings) // 2)
        if n_clusters > max_allowed:
            n_clusters = max_allowed
            warnings.append(f"n_clusters={requested} too large; clamped to {n_clusters}.")

        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(coords_2d)

    cluster_topics: dict[int, str] = {}
    unique_labels = set(labels)
    for label in unique_labels:
        if int(label) == -1:
            cluster_topics[int(label)] = "Noise / Unclustered"
            continue

        cluster_texts = [texts[i] for i, l in enumerate(labels) if int(l) == int(label)]
        if len(cluster_texts) < 2:
            cluster_topics[int(label)] = f"Cluster {label}"
            continue

        tfidf = TfidfVectorizer(max_features=5, stop_words="english")
        tfidf.fit(cluster_texts)
        # Preserve order by inverse index for deterministic labels.
        top_terms = [term for term, _ in sorted(tfidf.vocabulary_.items(), key=lambda item: item[1])][:5]
        cluster_topics[int(label)] = ", ".join(top_terms) if top_terms else f"Cluster {label}"

    return {
        "coords": coords_2d.tolist(),
        "labels": [int(x) for x in labels.tolist()],
        "cluster_topics": {str(k): v for k, v in cluster_topics.items()},
        "n_clusters_found": len({int(l) for l in labels if int(l) != -1}),
        "warnings": warnings,
    }
