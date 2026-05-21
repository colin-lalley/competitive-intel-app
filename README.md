# Vouch Competitive Intelligence Dashboard

Streamlit app for Vouch competitor battlecards, activity tracking, and analysis.

## Setup

### Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud
1. Push this directory to a GitHub repo
2. Connect the repo at [share.streamlit.io](https://share.streamlit.io)
3. Set the main file path to `app.py`

### Ask Claude (optional)
To enable the AI analysis feature, add your Anthropic API key:

**Local:** Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

**Streamlit Cloud:** Add `ANTHROPIC_API_KEY` in the app's Secrets settings.

## Data

The app reads from two JSONL files in the `data/` directory:

- `competitors.jsonl` — Structured competitor profiles
- `competitor-activity-log.jsonl` — Timestamped competitive moves

To update data, replace the JSONL files and push to GitHub. The app caches data for 5 minutes.
