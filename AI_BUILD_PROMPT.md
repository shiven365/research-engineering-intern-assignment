# FULL PROJECT BUILD PROMPT FOR AI CODING ASSISTANT
# Paste this entire file into your AI assistant (Cursor / Claude / Copilot) to build the project.
# Read every section before starting. Do not skip sections.

---

## PROJECT OVERVIEW

Build a full-stack **Social Media Narrative Intelligence Dashboard** called **"NarrativeScope"**.

**Case Study:** "How political narratives spread across ideologically diverse Reddit communities — tracking cross-subreddit coordination and influence patterns."

This is a research dashboard for studying how content from subreddits (Anarchism, Conservative, Liberal, news, worldnews, politics, conspiracy, etc.) spreads, clusters, and forms coordinated narratives over time.

**Tech Stack:**
- Backend: Python + FastAPI
- Database: DuckDB (embedded, no server needed)
- Embeddings: sentence-transformers (`all-MiniLM-L6-v2`)
- Vector Search: FAISS
- Clustering: UMAP + HDBSCAN
- Network: NetworkX + python-louvain
- LLM summaries + chatbot: Anthropic Claude API (`claude-sonnet-4-20250514`)
- Frontend: React (Vite) with TypeScript
- Charts: Recharts
- Network Graph: react-force-graph or Sigma.js via react-sigma
- Styling: Tailwind CSS with custom design system (dark theme)
- Hosting: Render.com (backend) + Vercel (frontend)

---

## DESIGN DIRECTION (READ THIS BEFORE WRITING ANY CODE)

**Aesthetic:** Industrial intelligence terminal — like a journalist's war room crossed with a Bloomberg terminal. Dark, dense, precise. NOT a generic purple-gradient Streamlit dashboard.

**Color Palette (CSS variables):**
```css
--bg-primary: #0a0a0f;
--bg-secondary: #0f0f1a;
--bg-card: #13131f;
--bg-card-hover: #1a1a2e;
--border: #1e1e35;
--border-bright: #2a2a4a;
--accent-primary: #00d4ff;     /* electric cyan */
--accent-secondary: #ff6b35;   /* warning orange */
--accent-tertiary: #7c3aed;    /* deep violet */
--text-primary: #e8e8f0;
--text-secondary: #8888aa;
--text-muted: #44445a;
--success: #00ff88;
--danger: #ff3366;
```

**Typography:**
- Display/Headers: `IBM Plex Mono` (monospace, technical feel)
- Body: `DM Sans` (clean, readable)
- Data/Numbers: `JetBrains Mono`
- Import from Google Fonts

**Layout:**
- Fixed left sidebar (240px) with navigation icons + labels
- Top bar with search input always visible
- Main content area with card-based grid
- Cards have subtle `1px` borders, slight glow on hover
- Use `backdrop-filter: blur()` for overlays
- Scanline texture overlay on header (CSS only, subtle)

**Animations:**
- Page load: staggered card reveals with `opacity 0 → 1` + `translateY(10px → 0)` with 80ms delays
- Data loading: skeleton shimmer effect (CSS animation)
- Chart lines draw in on mount
- Hover on network nodes: glow pulse
- Chatbot messages: typewriter effect for AI responses

---

## BACKEND STRUCTURE

```
backend/
├── main.py                  # FastAPI app, all routes
├── data/
│   ├── loader.py            # Parse data.jsonl → DuckDB
│   ├── database.py          # DuckDB connection + queries
├── ml/
│   ├── embeddings.py        # sentence-transformers + FAISS index
│   ├── clustering.py        # UMAP + HDBSCAN pipeline
│   ├── network.py           # NetworkX graph construction
├── llm/
│   ├── summarizer.py        # Claude API for time-series summaries
│   ├── chatbot.py           # RAG chatbot using Claude
├── requirements.txt
├── .env.example
```

---

## STEP 1 — DATA LOADING (backend/data/loader.py)

Parse `data.jsonl`. Each line is a JSON object with structure:
```json
{
  "kind": "t3",
  "data": {
    "id": "1is5wgo",
    "title": "What Are You Reading/Book Club Tuesday",
    "selftext": "What you are reading...",
    "author": "AutoModerator",
    "author_fullname": "t2_6l4z3",
    "subreddit": "Anarchism",
    "subreddit_id": "t5_2qh5j",
    "subreddit_subscribers": 275979,
    "score": 2,
    "ups": 2,
    "upvote_ratio": 1.0,
    "num_comments": 1,
    "num_crossposts": 0,
    "created_utc": 1739858460.0,
    "url": "https://www.reddit.com/r/Anarchism/...",
    "permalink": "/r/Anarchism/comments/...",
    "domain": "self.Anarchism",
    "is_self": true,
    "over_18": false,
    "stickied": false,
    "locked": false,
    "gilded": 0,
    "total_awards_received": 0
  }
}
```

**Loader must:**
1. Read every line of data.jsonl
2. Extract the `data` dict from each line
3. Compute engineered features:
   - `engagement_score = score + (num_comments * 2) + (num_crossposts * 3)`
   - `text_combined = title + " " + selftext` (strip HTML entities: `&lt;` → `<`, `&amp;` → `&`, `&gt;` → `>`)
   - `created_dt = datetime.utcfromtimestamp(created_utc)`
   - `hour_of_day = created_dt.hour`
   - `day_of_week = created_dt.strftime('%A')`
   - `date_only = created_dt.date()`
   - `is_crosspost = num_crossposts > 0`
4. Load into DuckDB table `posts` with all original + engineered columns
5. Create indexes on `subreddit`, `author`, `created_utc`, `date_only`
6. Print summary: total posts, unique authors, unique subreddits, date range

**DuckDB setup (backend/data/database.py):**
```python
import duckdb
conn = duckdb.connect('narrativescope.db')
# All queries go through this connection
```

---

## STEP 2 — EMBEDDINGS + FAISS SEMANTIC SEARCH (backend/ml/embeddings.py)

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

def build_index(texts: list[str], post_ids: list[str]):
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    
    index = faiss.IndexFlatIP(EMBEDDING_DIM)  # Inner product = cosine similarity on normalized vectors
    index.add(np.array(embeddings, dtype=np.float32))
    
    # Save index + id mapping
    faiss.write_index(index, "embeddings.index")
    with open("id_map.pkl", "wb") as f:
        pickle.dump(post_ids, f)
    
    return index, post_ids

def semantic_search(query: str, index, id_map: list[str], k: int = 10) -> list[str]:
    model = SentenceTransformer(MODEL_NAME)
    
    # Handle edge cases
    if not query or len(query.strip()) < 2:
        # Return top posts by engagement instead
        return []  # caller handles this
    
    query_vec = model.encode([query], normalize_embeddings=True)
    scores, indices = index.search(np.array(query_vec, dtype=np.float32), k)
    
    results = []
    for idx, score in zip(indices[0], scores[0]):
        if idx >= 0 and score > 0.1:  # filter very low similarity
            results.append({"post_id": id_map[idx], "similarity_score": float(score)})
    
    return results
```

**IMPORTANT:** Build the index once at startup, cache it in memory. Rebuild only if DB changes.

**On startup (main.py):**
```python
@app.on_event("startup")
async def startup():
    # Load all posts from DuckDB
    # Build FAISS index if not exists
    # Load clustering model if not exists
    pass
```

---

## STEP 3 — TOPIC CLUSTERING (backend/ml/clustering.py)

```python
import umap
import hdbscan
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def cluster_posts(embeddings: np.ndarray, texts: list[str], n_clusters: int = None):
    """
    Parameters:
    - embeddings: shape (N, 384) normalized float32
    - texts: original text for TF-IDF labeling
    - n_clusters: if None use HDBSCAN auto, else use KMeans with n_clusters
    
    Returns: dict with 2D coords, labels, cluster_topics
    """
    
    # Step 1: UMAP dimensionality reduction
    reducer = umap.UMAP(
        n_components=2,
        metric='cosine',
        n_neighbors=15,
        min_dist=0.1,
        random_state=42
    )
    coords_2d = reducer.fit_transform(embeddings)
    
    # Step 2: Clustering
    if n_clusters is None or n_clusters == 0:
        # Auto clustering with HDBSCAN
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=5,
            min_samples=3,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        labels = clusterer.fit_predict(coords_2d)
    else:
        # User-specified with KMeans
        from sklearn.cluster import KMeans
        n_clusters = max(2, min(n_clusters, len(embeddings) // 2))  # clamp
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(coords_2d)
    
    # Step 3: Label each cluster with top TF-IDF terms
    cluster_topics = {}
    unique_labels = set(labels)
    for label in unique_labels:
        if label == -1:
            cluster_topics[label] = "Noise / Unclustered"
            continue
        cluster_texts = [texts[i] for i, l in enumerate(labels) if l == label]
        if len(cluster_texts) < 2:
            cluster_topics[label] = f"Cluster {label}"
            continue
        tfidf = TfidfVectorizer(max_features=5, stop_words='english')
        tfidf.fit(cluster_texts)
        top_terms = list(tfidf.vocabulary_.keys())[:5]
        cluster_topics[label] = ", ".join(top_terms)
    
    return {
        "coords": coords_2d.tolist(),
        "labels": labels.tolist(),
        "cluster_topics": {str(k): v for k, v in cluster_topics.items()},
        "n_clusters_found": len(set(l for l in labels if l != -1))
    }
```

**EDGE CASES — HANDLE ALL OF THESE:**
- n_clusters = 1 → force 2, show warning in response
- n_clusters > total posts / 2 → clamp with warning
- n_clusters = 100 → clamp to reasonable max, do not crash
- Empty dataset → return empty coords with message
- Single post → return single point, label "Insufficient data"

---

## STEP 4 — NETWORK GRAPH (backend/ml/network.py)

**Graph definition:**
- **Nodes** = subreddits
- **Edges** = same author posted in both subreddits (within dataset)
- **Edge weight** = number of shared authors
- **Node size** = subreddit_subscribers (log scale)
- **Node color** = Louvain community label

```python
import networkx as nx
import community as community_louvain  # python-louvain
import json

def build_subreddit_network(posts_df):
    """
    posts_df columns: id, author, subreddit, score, subreddit_subscribers
    """
    G = nx.Graph()
    
    # Add nodes
    subreddit_info = posts_df.groupby('subreddit').agg(
        subscribers=('subreddit_subscribers', 'first'),
        post_count=('id', 'count'),
        avg_score=('score', 'mean')
    ).reset_index()
    
    for _, row in subreddit_info.iterrows():
        G.add_node(row['subreddit'], 
                   subscribers=int(row['subscribers']),
                   post_count=int(row['post_count']),
                   avg_score=float(row['avg_score']))
    
    # Add edges: subreddits connected if same author posted in both
    author_subreddits = posts_df.groupby('author')['subreddit'].apply(list)
    
    for author, subs in author_subreddits.items():
        unique_subs = list(set(subs))
        if len(unique_subs) < 2:
            continue
        for i in range(len(unique_subs)):
            for j in range(i+1, len(unique_subs)):
                s1, s2 = unique_subs[i], unique_subs[j]
                if G.has_edge(s1, s2):
                    G[s1][s2]['weight'] += 1
                    G[s1][s2]['shared_authors'].append(author)
                else:
                    G.add_edge(s1, s2, weight=1, shared_authors=[author])
    
    # PageRank
    pagerank = nx.pagerank(G, weight='weight')
    nx.set_node_attributes(G, pagerank, 'pagerank')
    
    # Betweenness centrality
    betweenness = nx.betweenness_centrality(G, weight='weight')
    nx.set_node_attributes(G, betweenness, 'betweenness')
    
    # Louvain community detection
    if len(G.nodes) > 0 and len(G.edges) > 0:
        communities = community_louvain.best_partition(G, weight='weight')
        nx.set_node_attributes(G, communities, 'community')
    
    return G

def graph_to_json(G: nx.Graph, remove_node: str = None) -> dict:
    """Convert graph to JSON for frontend. Optionally remove a node (for edge case testing)."""
    G_copy = G.copy()
    
    if remove_node and remove_node in G_copy:
        G_copy.remove_node(remove_node)
    
    # Handle disconnected components gracefully
    components = list(nx.connected_components(G_copy))
    
    nodes = []
    for node, data in G_copy.nodes(data=True):
        nodes.append({
            "id": node,
            "label": node,
            "subscribers": data.get('subscribers', 0),
            "post_count": data.get('post_count', 0),
            "avg_score": round(data.get('avg_score', 0), 2),
            "pagerank": round(data.get('pagerank', 0), 6),
            "betweenness": round(data.get('betweenness', 0), 6),
            "community": data.get('community', 0),
            "component": next(i for i, comp in enumerate(components) if node in comp)
        })
    
    edges = []
    for s, t, data in G_copy.edges(data=True):
        edges.append({
            "source": s,
            "target": t,
            "weight": data.get('weight', 1),
            "shared_author_count": len(data.get('shared_authors', []))
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "components": len(components),
        "removed_node": remove_node
    }
```

---

## STEP 5 — LLM SUMMARIES (backend/llm/summarizer.py)

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def generate_timeseries_summary(series_data: dict) -> str:
    """
    series_data = {
        "metric": "post_count",
        "date_range": {"start": "2024-01-01", "end": "2024-03-01"},
        "total": 1240,
        "peak_date": "2024-02-14",
        "peak_value": 89,
        "trend": "increasing",  # increasing / decreasing / stable / volatile
        "top_subreddits": ["politics", "worldnews", "Anarchism"],
        "avg_value": 14.2,
        "data_points": 60  # number of days
    }
    """
    prompt = f"""You are a data analyst for a social media research platform studying narrative spread on Reddit.

Here is a time-series summary of Reddit post activity:
- Metric: {series_data['metric']}
- Date range: {series_data['date_range']['start']} to {series_data['date_range']['end']}
- Total posts in period: {series_data['total']}
- Peak activity: {series_data['peak_value']} posts on {series_data['peak_date']}
- Overall trend: {series_data['trend']}
- Most active communities: {', '.join(series_data['top_subreddits'])}
- Daily average: {series_data['avg_value']:.1f} posts

Write exactly 2-3 sentences for a non-technical audience explaining:
1. What the trend shows
2. When/why there may have been a spike
3. What this might mean for narrative spread

Be specific with numbers. Do not use jargon. Do not mention "time series" or "data points"."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

---

## STEP 6 — RAG CHATBOT (backend/llm/chatbot.py)

```python
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are NarrativeScope AI, an intelligence analyst assistant for a social media research platform.
You analyze Reddit posts to help researchers understand how narratives spread across communities.

When given search results (retrieved Reddit posts), you:
1. Answer the user's question based ONLY on the retrieved posts
2. Cite specific posts (by subreddit and title) when making claims
3. Identify narrative patterns and cross-community connections
4. At the end, suggest exactly 2-3 follow-up queries the researcher might explore next

Format your follow-up suggestions as:
FOLLOW-UP QUERIES:
- [query 1]
- [query 2]
- [query 3]

If no relevant posts were found, say so clearly and suggest the user try different search terms."""

def chat(query: str, retrieved_posts: list[dict], conversation_history: list[dict]) -> str:
    """
    retrieved_posts: list of {title, subreddit, text, score, author, created_dt, similarity_score}
    conversation_history: list of {role, content} for multi-turn
    """
    
    # Format retrieved posts as context
    if retrieved_posts:
        context = "RETRIEVED POSTS (ranked by semantic relevance):\n\n"
        for i, post in enumerate(retrieved_posts[:8], 1):
            context += f"{i}. [{post['subreddit']}] \"{post['title']}\"\n"
            context += f"   Score: {post['score']} | Author: {post['author']} | Similarity: {post['similarity_score']:.2f}\n"
            if post.get('text') and len(post['text']) > 20:
                context += f"   Content preview: {post['text'][:200]}...\n"
            context += "\n"
    else:
        context = "NO RELEVANT POSTS FOUND for this query.\n"
    
    user_message = f"{context}\nResearcher question: {query}"
    
    messages = conversation_history + [{"role": "user", "content": user_message}]
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    
    return response.content[0].text
```

---

## STEP 7 — FASTAPI ROUTES (backend/main.py)

```python
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="NarrativeScope API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/stats/overview")
async def overview():
    """Total posts, authors, subreddits, date range, top subreddits"""
    pass

@app.get("/api/timeseries")
async def timeseries(
    metric: str = Query("post_count", enum=["post_count", "avg_score", "engagement"]),
    subreddit: Optional[str] = None,
    granularity: str = Query("day", enum=["hour", "day", "week"]),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Returns time series + GenAI summary"""
    pass

@app.get("/api/search")
async def search(
    q: str = Query(..., min_length=0),
    k: int = Query(10, ge=1, le=50),
    subreddit: Optional[str] = None
):
    """Semantic search. Handles empty/short/non-English queries gracefully."""
    if not q or len(q.strip()) < 2:
        # Return top posts by engagement instead
        return {"results": [], "mode": "fallback_top_engagement", "message": "Query too short. Showing top posts by engagement."}
    pass

@app.get("/api/network")
async def network(
    min_edge_weight: int = Query(1, ge=1),
    remove_node: Optional[str] = None,
    centrality_metric: str = Query("pagerank", enum=["pagerank", "betweenness"])
):
    """Returns graph JSON. remove_node tests edge case."""
    pass

@app.get("/api/clusters")
async def clusters(
    n_clusters: Optional[int] = Query(None, ge=2, le=100),
    subreddit: Optional[str] = None
):
    """Topic clustering with tunable n_clusters. Handles extremes."""
    pass

class ChatMessage(BaseModel):
    query: str
    history: list[dict] = []

@app.post("/api/chat")
async def chat(body: ChatMessage):
    """RAG chatbot. Semantic search + Claude response + follow-up queries."""
    pass

@app.get("/api/subreddits")
async def subreddits():
    """List all unique subreddits with post counts for filter dropdowns."""
    pass
```

---

## STEP 8 — FRONTEND STRUCTURE

```
frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css            # CSS variables + global styles
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   └── Layout.tsx
│   │   ├── charts/
│   │   │   ├── TimeSeriesChart.tsx    # Recharts LineChart
│   │   │   ├── AISummaryCard.tsx      # Below each chart
│   │   │   └── EngagementChart.tsx
│   │   ├── network/
│   │   │   └── NetworkGraph.tsx       # react-force-graph-2d
│   │   ├── clusters/
│   │   │   └── ClusterMap.tsx         # UMAP scatter plot via Recharts ScatterChart
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── FollowUpSuggestions.tsx
│   │   └── ui/
│   │       ├── Card.tsx
│   │       ├── StatBadge.tsx
│   │       ├── Skeleton.tsx           # Loading state
│   │       └── ErrorState.tsx
│   ├── pages/
│   │   ├── Overview.tsx               # Stats + quick charts
│   │   ├── Timeline.tsx               # Full time-series page
│   │   ├── Network.tsx                # Network graph page
│   │   ├── Clusters.tsx               # Topic clustering page
│   │   └── Chat.tsx                   # Full chatbot page
│   ├── hooks/
│   │   ├── useSearch.ts
│   │   ├── useTimeSeries.ts
│   │   └── useNetwork.ts
│   └── api/
│       └── client.ts                  # All API calls
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## STEP 9 — FRONTEND DESIGN SYSTEM (src/index.css)

```css
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #0f0f1a;
  --bg-card: #13131f;
  --bg-card-hover: #1a1a2e;
  --border: #1e1e35;
  --border-bright: #2a2a4a;
  --accent-primary: #00d4ff;
  --accent-secondary: #ff6b35;
  --accent-tertiary: #7c3aed;
  --text-primary: #e8e8f0;
  --text-secondary: #8888aa;
  --text-muted: #44445a;
  --success: #00ff88;
  --danger: #ff3366;
  --font-display: 'IBM Plex Mono', monospace;
  --font-body: 'DM Sans', sans-serif;
  --font-data: 'JetBrains Mono', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-body);
  line-height: 1.6;
  /* Subtle noise texture */
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
}

h1, h2, h3 { font-family: var(--font-display); }

/* Card style */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.card:hover {
  border-color: var(--border-bright);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.05);
}

/* Accent glow */
.glow-cyan { box-shadow: 0 0 15px rgba(0, 212, 255, 0.2); }
.glow-orange { box-shadow: 0 0 15px rgba(255, 107, 53, 0.2); }

/* Skeleton shimmer */
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
.skeleton {
  background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
  background-size: 1000px 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

/* Page load animation */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeUp 0.4s ease forwards; }

/* Scanline effect for header */
.scanline::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px
  );
  pointer-events: none;
}
```

---

## STEP 10 — SIDEBAR NAVIGATION COMPONENT

```tsx
// src/components/layout/Sidebar.tsx
// Navigation items:
const navItems = [
  { icon: LayoutDashboard, label: "Overview", path: "/" },
  { icon: TrendingUp, label: "Timeline", path: "/timeline" },
  { icon: Network, label: "Network", path: "/network" },
  { icon: Layers, label: "Topics", path: "/clusters" },
  { icon: MessageSquare, label: "Intelligence", path: "/chat" },  // chatbot
]

// Style: fixed left, 240px wide, dark bg, icons + labels
// Active state: accent-primary left border + text glow
// Logo: "NarrativeScope" in IBM Plex Mono, with a small "◈" symbol
// Bottom: version badge "v1.0 · SimPPL"
```

---

## STEP 11 — TOPBAR WITH SEARCH

```tsx
// src/components/layout/TopBar.tsx
// Always visible at top
// Left: Page title (changes per page)
// Center: Search input (full semantic search)
//   - Placeholder: "Search narratives semantically..."
//   - Debounced 300ms
//   - Shows result count + mode (semantic / fallback)
//   - Handles empty, short, non-English gracefully
// Right: Subreddit filter dropdown + date range picker
```

---

## STEP 12 — NETWORK GRAPH (react-force-graph-2d)

```tsx
// src/components/network/NetworkGraph.tsx
import ForceGraph2D from 'react-force-graph-2d';

// Node color: by community (use D3 categorical color scale)
// Node size: Math.log(subscribers + 1) * 3
// Edge width: Math.sqrt(shared_author_count)
// On node click: show sidebar with node details (subreddit stats, top posts)
// Controls:
//   - Slider: min_edge_weight (filter weak connections)
//   - Select: centrality metric (pagerank / betweenness)
//   - Button: "Remove top node" → calls API with remove_node param → re-renders
//   - Toggle: show/hide node labels

// MUST handle:
// - Empty graph (no edges): show message "No connections found with current filters"
// - Single node: render it alone, no crash
// - Disconnected components: render all, color by component
```

---

## STEP 13 — CLUSTER MAP

```tsx
// src/components/clusters/ClusterMap.tsx
// Use Recharts ScatterChart for the UMAP 2D scatter plot
// X/Y: UMAP coordinates
// Color: by cluster label
// Hover tooltip: post title, subreddit, cluster topic
// Below the chart: table of clusters with top terms + post count

// Controls:
//   - Slider: n_clusters (2 to 50)
//   - Dropdown: filter by subreddit
//   - Slider value 2 and 50: must not crash, show reasonable results

// Cluster color legend on the right
// "Noise" cluster (-1 from HDBSCAN): shown in grey, labeled "Unclustered"
```

---

## STEP 14 — CHAT PAGE

```tsx
// src/pages/Chat.tsx
// Full page chat interface

// Left panel (60%): Chat messages
//   - User messages: right-aligned, accent-primary bubble
//   - AI messages: left-aligned, bg-card bubble
//   - AI messages have typewriter animation on render
//   - Each AI message ends with FollowUpSuggestions component

// Right panel (40%): Retrieved posts panel
//   - Shows the posts retrieved by semantic search for the last query
//   - Title, subreddit badge, similarity score bar, engagement score
//   - Updates with each new query

// FollowUpSuggestions:
//   - Parse "FOLLOW-UP QUERIES:" section from AI response
//   - Render as clickable chips below AI message
//   - Clicking a chip fills the input and submits

// Input bar at bottom:
//   - Send on Enter, Shift+Enter for newline
//   - Loading state: "NarrativeScope is analyzing..." with pulsing dot
```

---

## STEP 15 — API CLIENT (src/api/client.ts)

```typescript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchOverview() {
  const res = await fetch(`${BASE_URL}/api/stats/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview');
  return res.json();
}

export async function fetchTimeSeries(params: {
  metric: string;
  subreddit?: string;
  granularity: string;
  start_date?: string;
  end_date?: string;
}) {
  const url = new URL(`${BASE_URL}/api/timeseries`);
  Object.entries(params).forEach(([k, v]) => v && url.searchParams.set(k, v));
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch time series');
  return res.json();
}

// ... similar for search, network, clusters, chat
// Always wrap in try/catch and return {data, error} pattern
```

---

## STEP 16 — ENVIRONMENT VARIABLES

**.env (backend):**
```
ANTHROPIC_API_KEY=your_key_here
DATA_PATH=./data/data.jsonl
DB_PATH=./narrativescope.db
INDEX_PATH=./embeddings.index
ID_MAP_PATH=./id_map.pkl
```

**.env (frontend):**
```
VITE_API_URL=http://localhost:8000
```

---

## STEP 17 — requirements.txt

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
duckdb==0.10.3
sentence-transformers==3.0.1
faiss-cpu==1.8.0
umap-learn==0.5.6
hdbscan==0.8.38
networkx==3.3
python-louvain==0.16
anthropic==0.34.0
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.1
python-dotenv==1.0.1
pydantic==2.8.2
```

---

## STEP 18 — package.json (frontend)

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "recharts": "^2.12.7",
    "react-force-graph-2d": "^1.25.5",
    "lucide-react": "^0.436.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "typescript": "^5.5.3",
    "vite": "^5.4.2",
    "@vitejs/plugin-react": "^4.3.1",
    "tailwindcss": "^3.4.10",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.41"
  }
}
```

---

## STEP 19 — GRACEFUL ERROR HANDLING (IMPLEMENT EVERYWHERE)

**Backend:**
- Every route: wrap in try/except, return `{"error": str(e), "data": null}` never 500 crash
- Clustering extremes: clamp n_clusters, add warning to response
- Network with removed node: if node not found, return graph unchanged with message
- Semantic search with non-English: run through model anyway (MiniLM is multilingual)
- Empty query: return top-10 by engagement_score with mode="fallback"

**Frontend:**
- Every API call: show ErrorState component on failure, not blank screen
- Loading states: Skeleton components, not spinners alone
- Empty results: `<EmptyState message="No posts found. Try broader terms." />`
- Network empty: message in canvas center
- Cluster map with 0 results: message, no crash

---

## STEP 20 — README.md FOR THE GITHUB REPO

Write a `README.md` with these sections:
1. **NarrativeScope** — one-paragraph case study description
2. **Live Demo** — URL + screenshot
3. **Architecture Diagram** — ASCII or mermaid diagram
4. **ML/AI Components** — exactly one line per component:
   - Embeddings: `all-MiniLM-L6-v2`, 384-dim, cosine similarity, `sentence-transformers` library
   - Vector Search: FAISS `IndexFlatIP`, inner product on L2-normalized vectors
   - Dimensionality Reduction: UMAP, 2 components, cosine metric, `umap-learn` library
   - Clustering: HDBSCAN, `min_cluster_size=5`, `min_samples=3`, `hdbscan` library
   - Network Centrality: PageRank + Betweenness, `networkx` library
   - Community Detection: Louvain algorithm, `python-louvain` library
   - LLM Summaries: Claude `claude-sonnet-4-20250514`, dynamic prompting based on actual data
   - Chatbot: RAG pattern, semantic retrieval + Claude generation
5. **Semantic Search Examples** (3 zero-overlap examples):

   | Query | Top Result | Why Correct |
   |---|---|---|
   | "people organizing against authority" | r/Anarchism book club post | Semantic match on anarchist themes without keyword overlap |
   | "community reading recommendations" | "What Are You Reading/Book Club Tuesday" | Matches intent without using "book" or "club" in query |
   | "weekly collective discussion thread" | AutoModerator stickied posts | Matches recurring community discussion pattern |

6. **Design Decisions** — 3-4 bullet points on WHY you made key choices
7. **Video Walkthrough** — YouTube/Drive link
8. **Local Setup** — `git clone`, `pip install`, `npm install`, `.env` setup, `uvicorn main:app`, `npm run dev`

---

## BUILD ORDER (do in this exact sequence)

1. `loader.py` — parse data.jsonl → DuckDB, verify with print(stats)
2. `embeddings.py` — build FAISS index, test 3 semantic searches
3. FastAPI `/api/search` route — test with curl
4. `clustering.py` — test with n=5, n=2, n=50
5. FastAPI `/api/clusters` route — test edge cases
6. `network.py` — build graph, test remove_node
7. FastAPI `/api/network` and `/api/timeseries` routes
8. `summarizer.py` — test Claude API call
9. `chatbot.py` — test full RAG pipeline
10. FastAPI `/api/chat` route
11. Frontend: Layout + Sidebar + TopBar
12. Frontend: Overview page
13. Frontend: Timeline page with AI summaries
14. Frontend: Network page
15. Frontend: Clusters page with slider
16. Frontend: Chat page
17. Error handling pass — test every edge case listed above
18. Deploy backend to Render, frontend to Vercel
19. Write README.md
20. Record video walkthrough

---

## CRITICAL REMINDERS

- Never hardcode AI summaries — always generate dynamically from actual data
- FAISS index must be built once and cached, not rebuilt per request
- All 3 semantic search zero-overlap examples must actually work before submission
- Network graph must not crash when highest-degree node is removed
- Cluster slider at n=2 and n=50 must not crash
- Non-English chatbot input must return a response, not an error
- Commit after each step above — do not squash commits
- Record the video LAST after everything works
