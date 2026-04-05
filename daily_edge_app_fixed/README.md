# Daily Edge

Daily Edge is a private Streamlit app for 15-minute daily microlearning.

It includes:
- a starter library of 49 cards
- lightweight recommendation logic
- a scoring and notes flow
- local memory through SQLite
- a library browser and history export

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Recommended GitHub structure

Keep these files in the repo root:
- `app.py`
- `requirements.txt`
- `README.md`
- `.streamlit/config.toml`
- `data/content_library.csv`

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload all project files.
3. Push to GitHub.
4. Go to Streamlit Community Cloud.
5. Create a new app and connect the repository.
6. Set the main file path to `app.py`.
7. Deploy.

## Important note about memory

This V1 stores interaction history in a local SQLite file under `data/daily_edge.db`.
That is fine for local use and early testing, but cloud persistence on Streamlit Community Cloud is not guaranteed.

When you want durable memory, move user history to a hosted database such as Supabase.

## Suggested next features

- add a weekly review page
- add custom card creation from inside the app
- add OpenAI-based article-to-card generation
- add a notification workflow
- replace SQLite with Supabase for persistent memory
