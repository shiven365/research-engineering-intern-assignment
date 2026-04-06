"""UI style helpers for NarrativeScope Streamlit pages."""

import streamlit as st


def apply_global_styles() -> None:
    """Inject a shared responsive style layer for all pages."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;500;600;700&display=swap');

:root {
  --ns-bg: #071023;
  --ns-panel: #0f1c33;
  --ns-panel-2: #132540;
  --ns-border: #29436b;
  --ns-text: #eaf2ff;
  --ns-muted: #9eb2cf;
  --ns-accent: #19c2b2;
}

html, body, [class*="css"] {
  font-family: 'Manrope', sans-serif;
  color: var(--ns-text);
}

h1, h2, h3, h4 {
  font-family: 'Space Grotesk', sans-serif;
  letter-spacing: 0.02em;
}

.main .block-container {
  max-width: 1200px;
  padding-top: clamp(1rem, 2.5vw, 2rem);
  padding-left: clamp(1rem, 3vw, 2.5rem);
  padding-right: clamp(1rem, 3vw, 2.5rem);
}

div[data-testid="stSidebarContent"] {
  background: linear-gradient(180deg, #08142a 0%, #0f1e3a 100%);
  border-right: 1px solid rgba(41, 67, 107, 0.5);
}

div[data-testid="stMetric"] {
  background: linear-gradient(145deg, var(--ns-panel), var(--ns-panel-2));
  border: 1px solid var(--ns-border);
  border-radius: 14px;
  padding: 0.8rem 1rem;
}

div[data-testid="stMetric"] label {
  color: var(--ns-muted);
}

div.stButton > button,
div.stDownloadButton > button {
  border-radius: 10px;
  border: 1px solid var(--ns-border);
}

.ns-hero {
  text-align: center;
  margin: 0.35rem 0 0.9rem 0;
}

.ns-badge {
  display: inline-block;
  border: 1px solid rgba(25, 194, 178, 0.35);
  color: #8de7de;
  background: rgba(25, 194, 178, 0.1);
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.7rem;
  margin-bottom: 0.55rem;
}

.ns-hero h1 {
  margin: 0;
  line-height: 1.08;
  font-size: clamp(2rem, 5.2vw, 3.2rem);
  background: linear-gradient(120deg, #7ee3ff 0%, #19c2b2 55%, #8de7de 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.ns-hero p {
  margin: 0.6rem auto 0;
  color: var(--ns-muted);
  max-width: 780px;
  font-size: clamp(0.98rem, 1.7vw, 1.1rem);
}

.ns-feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.8rem;
  margin-top: 0.25rem;
}

.ns-card {
  background: linear-gradient(145deg, #10203b, #122949);
  border: 1px solid var(--ns-border);
  border-radius: 14px;
  padding: 1rem 0.9rem;
  min-height: 130px;
  text-align: center;
  transition: border-color 160ms ease, transform 160ms ease;
}

.ns-card:hover {
  border-color: rgba(126, 227, 255, 0.75);
  transform: translateY(-2px);
}

.ns-card-icon {
  font-size: 1.35rem;
  margin-bottom: 0.35rem;
}

.ns-card h3 {
  margin: 0.05rem 0;
  font-size: 1rem;
}

.ns-card p {
  margin: 0.32rem 0 0;
  color: var(--ns-muted);
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .main .block-container {
    padding-left: 0.9rem;
    padding-right: 0.9rem;
  }

  .ns-card {
    min-height: 118px;
  }
}
</style>
        """,
        unsafe_allow_html=True,
    )
