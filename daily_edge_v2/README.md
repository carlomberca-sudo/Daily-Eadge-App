# Daily Edge V2

Daily Edge V2 is a private Streamlit microlearning app with:
- a richer evidence-based card format
- tabs for mechanism, sources, limitations, related topics, and application
- lightweight memory via SQLite
- a starter library CSV you can expand manually
- a page with guidance on how to develop the library

## Repo structure

```text
.
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── content_library_v2.csv
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Create a GitHub repo.
2. Upload all files, keeping the `data` folder in the repo root.
3. In Streamlit Community Cloud, create a new app from the repo.
4. Set `app.py` as the entry point.
5. Deploy.

## Notes

- This version stores interaction history in `data/daily_edge_v2.db`.
- On Streamlit Cloud, SQLite is fine for quick testing but is not robust long term.
- For durable memory later, move storage to Supabase or another hosted database.

## How to build the library well

Start with 15–20 high-quality cards instead of trying to build a giant database immediately.

Each card should have:
- one precise claim
- one short summary of why it matters
- one mechanism section
- one evidence-strength label
- one or two real sources
- one limitation section
- one skeptical view
- one practical takeaway
- one reflection prompt
- a few related topics

Good columns to keep in the CSV:

```text
id,title,category,subcategory,claim,summary,mechanism,evidence_strength,evidence_type,limitations,skeptical_view,practical_takeaway,reflection_prompt,related_topics,estimated_minutes,difficulty,source_1_title,source_1_url,source_1_type,source_2_title,source_2_url,source_2_type
```
