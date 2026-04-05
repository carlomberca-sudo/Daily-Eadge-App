from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
LIBRARY_PATH = DATA_DIR / "content_library.csv"
DB_PATH = DATA_DIR / "daily_edge.db"

st.set_page_config(page_title="Daily Edge", page_icon="🧠", layout="wide")

CATEGORY_WEIGHTS = {
    "Mind & behavior": 1.0,
    "Communication & influence": 1.0,
    "Public speaking": 0.95,
    "Body & performance": 0.9,
    "Decision-making & thinking": 1.0,
    "Learning & growth": 0.95,
    "Experimental / frontier ideas": 0.8,
}


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


CONN = get_connection()


def init_db() -> None:
    with CONN:
        CONN.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT NOT NULL,
                shown_at TEXT NOT NULL,
                rating INTEGER,
                response_tag TEXT,
                note TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                revisit_on TEXT,
                UNIQUE(card_id, shown_at)
            )
            """
        )


@st.cache_data

def load_library() -> pd.DataFrame:
    df = pd.read_csv(LIBRARY_PATH)
    df["estimated_minutes"] = df["estimated_minutes"].astype(int)
    df["novelty_score"] = df["novelty_score"].astype(int)
    return df


def get_history() -> pd.DataFrame:
    query = "SELECT * FROM interactions ORDER BY shown_at DESC"
    return pd.read_sql_query(query, CONN)


def upsert_interaction(card_id: str, shown_at: str, rating: Optional[int], response_tag: str, note: str, completed: bool, revisit_on: Optional[str]) -> None:
    with CONN:
        CONN.execute(
            """
            INSERT INTO interactions (card_id, shown_at, rating, response_tag, note, completed, revisit_on)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(card_id, shown_at)
            DO UPDATE SET
                rating = excluded.rating,
                response_tag = excluded.response_tag,
                note = excluded.note,
                completed = excluded.completed,
                revisit_on = excluded.revisit_on
            """,
            (card_id, shown_at, rating, response_tag, note, int(completed), revisit_on),
        )


def get_due_revisits(history: pd.DataFrame) -> set[str]:
    if history.empty or "revisit_on" not in history.columns:
        return set()
    today = date.today().isoformat()
    due = history[(history["revisit_on"].notna()) & (history["revisit_on"] <= today)]
    return set(due["card_id"].astype(str).tolist())


def compute_preferences(library: pd.DataFrame, history: pd.DataFrame) -> dict[str, float]:
    prefs = {category: 0.0 for category in library["category"].unique()}
    if history.empty:
        return prefs

    merged = history.merge(library[["id", "category"]], left_on="card_id", right_on="id", how="left")
    merged = merged.dropna(subset=["category"])
    if merged.empty:
        return prefs

    for category, group in merged.groupby("category"):
        score = 0.0
        if group["rating"].notna().any():
            score += (group["rating"].fillna(3).mean() - 3) * 0.35
        tags = group["response_tag"].fillna("")
        score += 0.5 * (tags == "More like this").sum()
        score -= 0.5 * (tags == "Less like this").sum()
        score -= 0.25 * (tags == "Too basic").sum()
        score -= 0.15 * (tags == "Too speculative").sum()
        prefs[category] = score / max(len(group), 1)
    return prefs


def days_since_last_seen(card_id: str, history: pd.DataFrame) -> int:
    rows = history[history["card_id"] == card_id]
    if rows.empty:
        return 999
    latest = pd.to_datetime(rows["shown_at"]).max().date()
    return (date.today() - latest).days


def select_today_card(library: pd.DataFrame, history: pd.DataFrame) -> pd.Series:
    today_key = date.today().isoformat()
    todays_rows = history[history["shown_at"] == today_key]
    if not todays_rows.empty:
        card_id = todays_rows.iloc[0]["card_id"]
        return library.loc[library["id"] == card_id].iloc[0]

    prefs = compute_preferences(library, history)
    due_revisits = get_due_revisits(history)

    recent_categories = []
    if not history.empty:
        merged_recent = history.merge(library[["id", "category"]], left_on="card_id", right_on="id", how="left")
        recent_categories = merged_recent.head(3)["category"].dropna().tolist()

    scored_rows = []
    for _, row in library.iterrows():
        card_id = row["id"]
        category = row["category"]
        seen_count = len(history[history["card_id"] == card_id])
        days_gap = days_since_last_seen(card_id, history)
        score = 0.0
        score += CATEGORY_WEIGHTS.get(category, 1.0)
        score += prefs.get(category, 0.0)
        score += 0.12 * row["novelty_score"]
        score += 0.03 * min(days_gap, 30)
        score -= 0.55 * seen_count
        if category in recent_categories[:2]:
            score -= 0.6
        elif category in recent_categories[2:3]:
            score -= 0.25
        if card_id in due_revisits:
            score += 1.2
        if row["difficulty"] == "practical":
            score += 0.12
        scored_rows.append((score, row))

    scored_rows.sort(key=lambda x: x[0], reverse=True)
    return scored_rows[0][1]


def style_badge(text: str, background: str = "#eef2ff", color: str = "#1e3a8a") -> str:
    return f"<span style='padding:0.25rem 0.6rem;border-radius:999px;background:{background};color:{color};font-size:0.85rem;font-weight:600;margin-right:0.35rem'>{text}</span>"


def render_card(card: pd.Series) -> None:
    badges = " ".join(
        [
            style_badge(card["category"]),
            style_badge(card["subcategory"], "#f1f5f9", "#334155"),
            style_badge(f"Evidence: {card['evidence_strength']}", "#ecfeff", "#155e75"),
            style_badge(f"{card['estimated_minutes']} min", "#f0fdf4", "#166534"),
        ]
    )
    st.markdown(badges, unsafe_allow_html=True)
    st.subheader(card["title"])
    st.markdown("### Core idea")
    st.write(card["core_idea"])
    st.markdown("### Why it matters")
    st.write(card["why_it_matters"])
    st.markdown("### Try this today")
    st.write(card["practical_application"])
    st.markdown("### Reflection prompt")
    st.info(card["reflection_prompt"])


def export_history_csv(history: pd.DataFrame) -> bytes:
    if history.empty:
        return b""
    return history.to_csv(index=False).encode("utf-8")


def sidebar_stats(library: pd.DataFrame, history: pd.DataFrame) -> None:
    st.sidebar.header("Daily Edge")
    st.sidebar.caption("Personal microlearning engine")
    total_cards = len(library)
    completed = int(history["completed"].sum()) if not history.empty else 0
    unique_seen = int(history["card_id"].nunique()) if not history.empty else 0
    st.sidebar.metric("Library size", total_cards)
    st.sidebar.metric("Cards completed", completed)
    st.sidebar.metric("Unique cards seen", unique_seen)

    if not history.empty and history["rating"].notna().any():
        avg_rating = round(float(history["rating"].dropna().mean()), 2)
        st.sidebar.metric("Average rating", avg_rating)

    st.sidebar.markdown("---")
    st.sidebar.write("This V1 stores progress in a local SQLite file. It works well for a private prototype. For durable cloud memory later, move storage to Supabase.")


def main() -> None:
    init_db()
    library = load_library()
    history = get_history()
    sidebar_stats(library, history)

    st.title("🧠 Daily Edge")
    st.caption("A private 15-minute microlearning app for psychology, communication, performance, and clearer thinking.")

    tabs = st.tabs(["Today", "Library", "History", "How it works"])

    with tabs[0]:
        card = select_today_card(library, history)
        today_key = date.today().isoformat()
        existing = history[(history["card_id"] == card["id"]) & (history["shown_at"] == today_key)]

        col1, col2 = st.columns([2.2, 1])
        with col1:
            render_card(card)

        default_rating = int(existing.iloc[0]["rating"]) if not existing.empty and pd.notna(existing.iloc[0]["rating"]) else 3
        default_tag = existing.iloc[0]["response_tag"] if not existing.empty and pd.notna(existing.iloc[0]["response_tag"]) else "Useful"
        default_note = existing.iloc[0]["note"] if not existing.empty and pd.notna(existing.iloc[0]["note"]) else ""
        default_completed = bool(existing.iloc[0]["completed"]) if not existing.empty else False

        with col2:
            st.markdown("### Score this session")
            with st.form("daily_feedback_form"):
                rating = st.slider("How valuable was this?", 1, 5, value=default_rating)
                response_tag = st.selectbox(
                    "How should this influence future suggestions?",
                    ["Useful", "More like this", "Less like this", "Too basic", "Too speculative"],
                    index=["Useful", "More like this", "Less like this", "Too basic", "Too speculative"].index(default_tag),
                )
                note = st.text_area("Your note", value=default_note, placeholder="One sentence on what you learned or where to apply it.")
                completed = st.checkbox("Completed today's 15-minute session", value=default_completed)
                revisit_days = st.selectbox("Revisit this in", ["No revisit", "3 days", "7 days", "14 days", "30 days"], index=0)
                submitted = st.form_submit_button("Save today's session")

            if submitted:
                revisit_on = None
                if revisit_days != "No revisit":
                    days = int(revisit_days.split()[0])
                    revisit_on = (date.today() + timedelta(days=days)).isoformat()
                upsert_interaction(card["id"], today_key, rating, response_tag, note.strip(), completed, revisit_on)
                st.success("Saved. Tomorrow's suggestion will adapt based on this feedback.")
                st.rerun()

            st.markdown("### Suggestion logic")
            st.write(
                "V1 favors category variety, lightly rewards topics you rate highly, and occasionally re-surfaces cards you marked for review."
            )

    with tabs[1]:
        st.subheader("Browse the library")
        category_options = ["All"] + sorted(library["category"].unique().tolist())
        difficulty_options = ["All"] + sorted(library["difficulty"].unique().tolist())
        col_a, col_b, col_c = st.columns([1.2, 1, 1.5])
        with col_a:
            selected_category = st.selectbox("Category", category_options)
        with col_b:
            selected_difficulty = st.selectbox("Difficulty style", difficulty_options)
        with col_c:
            search_term = st.text_input("Search", placeholder="Search title, subcategory, or idea")

        filtered = library.copy()
        if selected_category != "All":
            filtered = filtered[filtered["category"] == selected_category]
        if selected_difficulty != "All":
            filtered = filtered[filtered["difficulty"] == selected_difficulty]
        if search_term:
            mask = (
                filtered["title"].str.contains(search_term, case=False, na=False)
                | filtered["subcategory"].str.contains(search_term, case=False, na=False)
                | filtered["core_idea"].str.contains(search_term, case=False, na=False)
            )
            filtered = filtered[mask]

        seen_ids = set(history["card_id"].astype(str).tolist()) if not history.empty else set()
        filtered = filtered.copy()
        filtered["seen"] = filtered["id"].apply(lambda x: "Yes" if x in seen_ids else "No")
        st.dataframe(
            filtered[["id", "title", "category", "subcategory", "evidence_strength", "difficulty", "seen"]],
            use_container_width=True,
            hide_index=True,
        )

        selected_id = st.selectbox("Preview a card", filtered["id"].tolist() if not filtered.empty else [])
        if selected_id:
            preview_card = library[library["id"] == selected_id].iloc[0]
            st.markdown("---")
            render_card(preview_card)

    with tabs[2]:
        st.subheader("Your history")
        if history.empty:
            st.info("No sessions saved yet. Complete today's card to start building memory.")
        else:
            merged = history.merge(library[["id", "title", "category"]], left_on="card_id", right_on="id", how="left")
            history_view = merged[["shown_at", "card_id", "title", "category", "rating", "response_tag", "completed", "revisit_on", "note"]]
            st.dataframe(history_view, use_container_width=True, hide_index=True)
            st.download_button(
                "Download history as CSV",
                data=export_history_csv(history_view),
                file_name="daily_edge_history.csv",
                mime="text/csv",
            )

    with tabs[3]:
        st.subheader("How this version works")
        st.markdown(
            """
            **What is included**

            - A starter library of 49 Daily Edge cards
            - Categories across psychology, communication, public speaking, decision-making, performance, and frontier ideas
            - A daily recommendation engine with lightweight memory
            - Feedback logging and revisit scheduling
            - Local storage with SQLite for quick prototyping

            **What to add next**

            1. Custom card creation inside the app  
            2. Weekly review page  
            3. OpenAI-powered article-to-card generation  
            4. Persistent cloud storage with Supabase  
            5. Notification workflow
            """
        )
        st.code(
            json.dumps(
                {
                    "recommendation_rules": [
                        "Prefer categories you rated well",
                        "Avoid showing the same category too often in the short term",
                        "Give a small novelty boost to frontier and less-seen topics",
                        "Re-surface cards that are due for review",
                    ]
                },
                indent=2,
            ),
            language="json",
        )


if __name__ == "__main__":
    main()
