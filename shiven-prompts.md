# AI Assistance Prompt Log

This file records the AI prompts used during development, in order, with what went wrong and how each issue was fixed.

1. Component: Project migration (React/FastAPI to Streamlit app)
   Prompt: "here i convert project into strimlit formate so project can work easily in deployment field so run based on them here make file analyse it"
   Note: Initial output left deployment gaps (missing startup metadata), so I added deployment files and Streamlit-first run docs.

2. Component: Deployment scaffolding
   Prompt: "Make this deploy-ready for Streamlit Cloud and Render."
   Note: First pass lacked explicit process startup, so I added Procfile and render.yaml with Streamlit start command.

3. Component: Repository cleanup
   Prompt: "here remove rect file and other unnesacery file and make project perfect"
   Note: First cleanup command failed on a locked DB file, so I retried deletion, identified lock behavior, and completed all other safe removals.



4. Component: UI/UX responsiveness
   Prompt: "make UI proper and responsive"
   Note: Styling was only applied on the home page, so I created shared global styles and applied them to every Streamlit page.

5. Component: Data loading reliability
   Prompt: "here it give error it not show any proper output"
   Note: Runtime crashed due to wrong DATA_PATH (./data.jsonl), so I added resilient path resolution with fallback to backend/data.jsonl.

6. Component: Backend performance (data/index path)
   Prompt: "here backend related thigs give slow responce"
   Note: Chat path was loading the full embedding matrix unnecessarily, so I split lightweight index loading from heavy vector loading.

7. Component: Timeline performance
   Prompt: "Improve slow page interactions when filters change."
   Note: Timeline called LLM summary on every rerun, so I switched to on-demand summary generation with session cache.

8. Component: Chat reliability
   Prompt: "chat not work poprly"
   Note: Anthropic API returned low-credit errors and broke responses, so I added friendly error mapping plus local fallback answers.

9. Component: Chat context size / latency
    Prompt: "Stabilize chat responses and reduce backend delay."
    Note: Full chat history increased request payload and failure risk, so I trimmed history to the latest turns before LLM calls.

10. Component: Documentation quality
    Prompt: "A detailed README file with screenshots of your solution and a URL to your publicly hosted web platform"
    Note: No screenshots/URL existed in repo, so I created a detailed README with structured placeholders and a screenshot folder spec.


