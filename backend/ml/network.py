from typing import Any

import community as community_louvain
import networkx as nx
import pandas as pd


def build_subreddit_network(posts_df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()

    if posts_df.empty:
        return G

    subreddit_info = (
        posts_df.groupby("subreddit")
        .agg(
            subscribers=("subreddit_subscribers", "first"),
            post_count=("id", "count"),
            avg_score=("score", "mean"),
        )
        .reset_index()
    )

    for _, row in subreddit_info.iterrows():
        G.add_node(
            row["subreddit"],
            subscribers=int(row["subscribers"] or 0),
            post_count=int(row["post_count"] or 0),
            avg_score=float(row["avg_score"] or 0.0),
        )

    author_subreddits = posts_df.groupby("author")["subreddit"].apply(list)

    for author, subs in author_subreddits.items():
        unique_subs = list(set(subs))
        if len(unique_subs) < 2:
            continue

        for i in range(len(unique_subs)):
            for j in range(i + 1, len(unique_subs)):
                s1, s2 = unique_subs[i], unique_subs[j]
                if G.has_edge(s1, s2):
                    G[s1][s2]["weight"] += 1
                    G[s1][s2]["shared_authors"].append(author)
                else:
                    G.add_edge(s1, s2, weight=1, shared_authors=[author])

    if len(G.nodes) > 0:
        pagerank = nx.pagerank(G, weight="weight") if len(G.edges) > 0 else {n: 0.0 for n in G.nodes}
        nx.set_node_attributes(G, pagerank, "pagerank")

        betweenness = (
            nx.betweenness_centrality(G, weight="weight") if len(G.edges) > 0 else {n: 0.0 for n in G.nodes}
        )
        nx.set_node_attributes(G, betweenness, "betweenness")

        if len(G.edges) > 0:
            communities = community_louvain.best_partition(G, weight="weight")
            nx.set_node_attributes(G, communities, "community")

    return G


def graph_to_json(G: nx.Graph, remove_node: str | None = None) -> dict[str, Any]:
    G_copy = G.copy()
    message = None

    if remove_node:
        if remove_node in G_copy:
            G_copy.remove_node(remove_node)
            message = f"Removed node: {remove_node}"
        else:
            message = f"Node not found: {remove_node}. Graph unchanged."

    components = list(nx.connected_components(G_copy))

    nodes = []
    for node, data in G_copy.nodes(data=True):
        component_id = next((i for i, comp in enumerate(components) if node in comp), 0)
        nodes.append(
            {
                "id": node,
                "label": node,
                "subscribers": data.get("subscribers", 0),
                "post_count": data.get("post_count", 0),
                "avg_score": round(data.get("avg_score", 0), 2),
                "pagerank": round(data.get("pagerank", 0), 6),
                "betweenness": round(data.get("betweenness", 0), 6),
                "community": data.get("community", 0),
                "component": component_id,
            }
        )

    edges = []
    for s, t, data in G_copy.edges(data=True):
        edges.append(
            {
                "source": s,
                "target": t,
                "weight": data.get("weight", 1),
                "shared_author_count": len(data.get("shared_authors", [])),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "components": len(components),
        "removed_node": remove_node,
        "message": message,
    }
