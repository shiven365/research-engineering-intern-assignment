const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type ApiResult<T> = { data: T | null; error: string | null }

async function request<T>(url: string, init?: RequestInit): Promise<ApiResult<T>> {
  try {
    const res = await fetch(url, init)
    const json = await res.json()
    if (!res.ok) return { data: null, error: json?.error || 'Request failed' }

    if (json && 'data' in json) {
      return { data: json.data as T, error: json.error || null }
    }

    return { data: json as T, error: null }
  } catch (e) {
    return { data: null, error: e instanceof Error ? e.message : 'Unknown error' }
  }
}

export function fetchOverview() {
  return request<any>(`${BASE_URL}/api/stats/overview`)
}

export function fetchTimeSeries(params: {
  metric: string
  subreddit?: string
  granularity: string
  start_date?: string
  end_date?: string
}) {
  const url = new URL(`${BASE_URL}/api/timeseries`)
  Object.entries(params).forEach(([k, v]) => {
    if (v) url.searchParams.set(k, String(v))
  })
  return request<any>(url.toString())
}

export function fetchSearch(params: {
  q: string
  k?: number
  subreddit?: string
  start_date?: string
  end_date?: string
}) {
  const url = new URL(`${BASE_URL}/api/search`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined) url.searchParams.set(k, String(v))
  })
  return request<any>(url.toString())
}

export function fetchNetwork(params: {
  min_edge_weight?: number
  remove_node?: string
  centrality_metric?: 'pagerank' | 'betweenness'
}) {
  const url = new URL(`${BASE_URL}/api/network`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '') url.searchParams.set(k, String(v))
  })
  return request<any>(url.toString())
}

export function fetchClusters(params: { n_clusters?: number; subreddit?: string }) {
  const url = new URL(`${BASE_URL}/api/clusters`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined) url.searchParams.set(k, String(v))
  })
  return request<any>(url.toString())
}

export function fetchSubreddits() {
  return request<any>(`${BASE_URL}/api/subreddits`)
}

export function postChat(body: { query: string; history: Array<{ role: string; content: string }> }) {
  return request<any>(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
