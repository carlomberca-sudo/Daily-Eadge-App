from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
LIBRARY_PATH = DATA_DIR / "content_library_v2.csv"
DB_PATH = DATA_DIR / "daily_edge_v2.db"

st.set_page_config(page_title="Daily Edge V2", page_icon="🧠", layout="wide")

EMBEDDED_LIBRARY_CSV = r'''id,title,category,subcategory,claim,summary,mechanism,evidence_strength,evidence_type,limitations,skeptical_view,practical_takeaway,reflection_prompt,related_topics,estimated_minutes,difficulty,source_1_title,source_1_url,source_1_type,source_2_title,source_2_url,source_2_type
DE201,Agreement before disagreement,Communication & influence,Persuasion,"Validating part of the other person's position before disagreeing often lowers defensiveness.","This usually makes the exchange feel collaborative instead of adversarial, which can increase openness to your reasoning.","Acknowledgment reduces social threat and signals fairness. When people feel heard, they are less likely to interpret disagreement as attack.",Moderate,Behavioral science and negotiation literature,"Effects depend on tone, sincerity, and context. Formulaic validation can sound manipulative.","This is not a magic trick. Some disagreements are driven by incentives, identity, or zero-sum conflict rather than misunderstanding.","Open with one sentence of genuine agreement before introducing your difference.","Where do you tend to jump into correction before making the other person feel understood?","status threat, identity-protective reasoning, labeling emotions",12,practical,Getting to Yes,https://www.penguinrandomhouse.com/books/305835/getting-to-yes-by-roger-fisher-william-ury-and-bruce-patton/,Book,Crucial Conversations,https://www.vitalsmarts.com/crucial-conversations/,Book
DE202,Identity-protective reasoning,Mind & behavior,Cognition,"People often resist facts that threaten an identity, tribe, or status position they care about.","A belief can be emotionally expensive to update when it is connected to belonging or self-image.","Reasoning is not only about truth-seeking. It can also serve identity protection, status defense, and social cohesion.",Strong,Behavioral science,"The concept explains some resistance but not all disagreement. People also differ because of values, incentives, and information quality.","Do not use this idea as a way to dismiss everyone who disagrees with you as irrational.","When presenting difficult facts, protect dignity first and avoid framing the update as humiliation.","Which of your own beliefs would be hardest to revisit because changing them would feel like losing part of yourself?","motivated reasoning, cognitive dissonance, status threat",15,conceptual,The Righteous Mind,https://jonathanhaidt.com/the-righteous-mind/,Book,The Enigma of Reason,https://www.hup.harvard.edu/books/9780674368309,Book
DE203,The spotlight effect,Mind & behavior,Social cognition,"Other people usually notice your mistakes less than you think.","Your own awkward moments feel huge because you experience them from the inside; everyone else is busy managing their own attention.","Self-focus makes personal errors vivid, while observers have fragmented attention and weaker memory for your minor slips.",Strong,Social psychology,"This does not mean audiences notice nothing. Very salient errors still matter.","The goal is not to become careless, but to calibrate anxiety.","Before speaking, remind yourself that the audience is mostly tracking the message, not your tiny imperfections.","What fear would shrink if you fully believed that most people are not scrutinizing you as much as you imagine?","public speaking anxiety, self-consciousness, reappraisal",10,practical,The spotlight effect in social judgment,https://psycnet.apa.org/record/2000-15524-001,Journal article,Quiet,https://quietrev.com/why-we-overestimate-how-much-people-notice-us/,Article
DE204,Cognitive reappraisal,Mind & behavior,Emotional regulation,"Changing the interpretation of an event can change the stress response to it.","Reframing does not erase difficulty, but it can reduce threat intensity and improve your sense of agency.","Appraisal shapes whether the nervous system treats a situation as danger, challenge, loss, or opportunity.",Strong,Emotion regulation literature,"Reappraisal is not always enough on its own, especially in chronic or structural stressors.","Poorly done reappraisal can become avoidance or self-deception.","When stressed, ask what else the situation could mean besides danger or personal failure.","Which recurring stressor could become lighter if you changed the story you tell yourself about it?","stress mindset, CBT, learned helplessness",12,practical,Emotion Regulation: Conceptual Foundations,https://www.guilford.com/books/Handbook-of-Emotion-Regulation/Gross/9781462538805,Book,How to Think Like a Roman Emperor,https://us.macmillan.com/books/9781250621436/howtothinklikearomanemperor,Book
DE205,One message per talk,Public speaking,Structure,"Audiences usually remember one clear thesis better than several medium-strength points.","Coverage feels satisfying to the speaker, but recall depends on compression and clarity.","Working memory is limited. A single organizing message gives the audience a stable structure to attach details to.",Strong,Communication and learning science,"Some technical settings genuinely require more detail. Simplicity must not distort substance.","This principle is often used lazily to justify oversimplification.","Write the one sentence you want remembered, then test every slide against it.","What presentation of yours is trying to say too many things at once?","chunking, contrast, storytelling",10,practical,Made to Stick,https://heathbrothers.com/books/made-to-stick/,Book,Presentation Zen,https://www.presentationzen.com/,Book
DE206,Stories beat abstractions,Communication & influence,Narrative,"Concrete stories are usually easier to remember than abstract explanations.","Stories provide sequence, causality, and imagery, which improves retention and engagement.","Narratives package information into units the mind can simulate and recall more easily than disembodied claims.",Strong,Communication research,"Stories can oversimplify and distort if they are treated as proof rather than illustration.","A vivid anecdote is memorable, but it is not automatically representative.","Start explanations with one concrete case, then generalize.","Where do you explain too abstractly when a specific example would make the idea land?","analogy, examples, concrete language",10,practical,Made to Stick,https://heathbrothers.com/books/made-to-stick/,Book,The Story Factor,https://annetteimmons.com/books/the-story-factor/,Book
DE207,Sleep pressure and adenosine,Body & performance,Sleep,"Caffeine reduces the feeling of sleep pressure, but it does not replace sleep.","It can improve alertness temporarily while leaving the underlying sleep debt unresolved.","Adenosine builds during wakefulness; caffeine blocks its signaling rather than restoring biological recovery.",Strong,Sleep physiology,"Individual responses vary with dose, timing, genetics, and sleep history.","People often generalize from short-term productivity gains and ignore longer-term disruption.","Use caffeine strategically and avoid treating it as a substitute for recovery.","Where are you using stimulation to compensate for a recovery problem that should be fixed directly?","circadian rhythm, light exposure, sleep debt",12,practical,Why We Sleep,https://www.penguinrandomhouse.com/books/557488/why-we-sleep-by-matthew-walker-phd/,Book,Sleep Foundation: Adenosine and Sleep,https://www.sleepfoundation.org/how-sleep-works/adenosine-and-sleep,Article
DE208,Morning light anchors the clock,Body & performance,Recovery,"Light soon after waking helps anchor circadian timing.","This can improve wakefulness cues and make the sleep-wake cycle more stable.","Morning light acts on the biological clock through retinal pathways that influence circadian alignment.",Strong,Circadian biology,"Latitude, weather, schedule, and individual chronotype matter. It is not a perfect fix for every energy issue.","Do not turn this into a ritual obsession; consistency matters more than perfection.","Get outdoor light soon after waking when practical.","What part of your daily energy might improve through timing rather than more discipline?","sleep hygiene, zeitgebers, caffeine timing",10,practical,Circadian Rhythms Fact Sheet,https://www.nigms.nih.gov/education/fact-sheets/Pages/circadian-rhythms.aspx,Government explainer,Huberman Lab Toolkit for Sleep,https://www.hubermanlab.com/newsletter/toolkit-for-sleep,Article
DE209,Expected value over single outcomes,Decision-making & thinking,Judgment,"A good decision can still have a bad outcome.","Under uncertainty, you should judge choices by process and expected value, not by one realized result.","Noise and probability separate decision quality from outcome quality. Overweighting outcomes encourages superstition and hindsight bias.",Strong,Decision science,"Expected value is not the only criterion. Risk tolerance, downside asymmetry, and ethics also matter.","People sometimes invoke expected value to excuse sloppy execution.","After an outcome, ask whether the decision was sensible given what you knew at the time.","Where are you being unfair to yourself because you are confusing a bad result with a bad decision?","base rates, hindsight bias, probabilistic thinking",12,conceptual,Thinking in Bets,https://www.penguinrandomhouse.com/books/550181/thinking-in-bets-by-annie-duke/,Book,Noise,https://www.littlebrown.com/titles/daniel-kahneman/noise/9780316451406/,Book
DE210,Base rates first,Decision-making & thinking,Forecasting,"Before focusing on the special details of a case, start with what usually happens in similar cases.","Reference-class thinking reduces the pull of seductive anecdotes and exceptional narratives.","Base rates anchor judgment in broader patterns before you layer on case-specific information.",Strong,Decision science,"Base rates can mislead when the reference class is poorly chosen or genuinely irrelevant.","Some people use base rates mechanically and underweight real unique information.","In forecasts, identify the closest comparison class before reasoning from the inside view.","Which predictions of yours rely too much on story and too little on typical outcomes?","inside vs outside view, planning fallacy, forecasting",12,practical,Thinking Fast and Slow,https://us.macmillan.com/books/9780374533557/thinkingfastandslow,Book,Superforecasting,https://www.penguinrandomhouse.com/books/239545/superforecasting-by-philip-e-tetlock-and-dan-gardner/,Book
DE211,Frontier claims need stronger filters,Experimental / frontier ideas,Research literacy,"The more novel and sensational a claim is, the higher your evidence threshold should be.","Interesting is not the same as actionable, and early findings often fail to generalize.","Novelty attracts attention and publication energy, but replication, external validity, and practical significance often lag behind the headline.",Strong,Research literacy,"A conservative filter can make you slow to adopt genuinely useful innovations.","Skepticism is valuable, but reflexive dismissal can become its own bias.","For every exciting claim, ask: what was measured, in whom, how large was the effect, and has it been replicated?","Which category of claims do you accept too quickly because they sound smart, technical, or edgy?","microplastics headlines, causality, replication crisis",12,conceptual,Calling Bullshit,https://press.princeton.edu/books/hardcover/9780691188294/calling-bullshit,Book,Understanding Research Methods,https://us.sagepub.com/en-us/nam/understanding-research-methods/book266975,Book
DE212,Retrieval beats rereading,Learning & growth,Learning,"Testing yourself usually builds memory better than passively rereading notes.","Active retrieval strengthens recall pathways and exposes what you do not actually know yet.","Memory improves when the brain has to reconstruct information rather than just re-expose itself to it.",Strong,Learning science,"Retrieval works best when the material was encoded reasonably well in the first place.","People sometimes over-quiz themselves without enough feedback or explanation.","After reading, close the page and write the key ideas from memory before checking.","What are you consuming repeatedly without ever testing whether it stuck?","spacing effect, desirable difficulty, active recall",10,practical,Make It Stick,https://www.hup.harvard.edu/books/9780674729018,Book,Retrieval Practice,https://www.retrievalpractice.org/,Resource
'''

CATEGORY_WEIGHTS = {
    "Mind & behavior": 1.0,
    "Communication & influence": 1.0,
    "Public speaking": 0.95,
    "Body & performance": 0.95,
    "Decision-making & thinking": 1.0,
    "Learning & growth": 0.95,
    "Experimental / frontier ideas": 0.8,
}


def resolve_library_path() -> Path | None:
    candidates = [
        LIBRARY_PATH,
        APP_DIR / "content_library_v2.csv",
        APP_DIR / "data" / "content_library.csv",
        Path.cwd() / "data" / "content_library_v2.csv",
        Path.cwd() / "content_library_v2.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


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
    resolved = resolve_library_path()
    if resolved is not None:
        df = pd.read_csv(resolved)
    else:
        df = pd.read_csv(StringIO(EMBEDDED_LIBRARY_CSV))

    required_defaults = {
        "limitations": "",
        "skeptical_view": "",
        "related_topics": "",
        "source_1_title": "",
        "source_1_url": "",
        "source_1_type": "",
        "source_2_title": "",
        "source_2_url": "",
        "source_2_type": "",
    }
    for col, default in required_defaults.items():
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default)

    if "estimated_minutes" not in df.columns:
        df["estimated_minutes"] = 10
    if "difficulty" not in df.columns:
        df["difficulty"] = "practical"
    return df


def get_history() -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM interactions ORDER BY shown_at DESC", CONN)


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
    if history.empty:
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
        score += 0.45 * (tags == "More like this").sum()
        score -= 0.45 * (tags == "Less like this").sum()
        score -= 0.2 * (tags == "Too basic").sum()
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
    recent_categories: list[str] = []
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
        score += 0.03 * min(days_gap, 30)
        score -= 0.55 * seen_count
        if category in recent_categories[:2]:
            score -= 0.6
        elif category in recent_categories[2:3]:
            score -= 0.2
        if card_id in due_revisits:
            score += 1.2
        if str(row.get("difficulty", "practical")).lower() == "practical":
            score += 0.12
        scored_rows.append((score, row))

    scored_rows.sort(key=lambda x: x[0], reverse=True)
    return scored_rows[0][1]


def source_rows(card: pd.Series) -> list[tuple[str, str, str]]:
    rows = []
    for idx in (1, 2, 3):
        title = str(card.get(f"source_{idx}_title", "") or "").strip()
        url = str(card.get(f"source_{idx}_url", "") or "").strip()
        src_type = str(card.get(f"source_{idx}_type", "") or "").strip()
        if title:
            rows.append((title, url, src_type))
    return rows


def render_today_card(card: pd.Series) -> None:
    st.markdown(
        f"""
        <div style='padding:1rem 1.1rem;border:1px solid #e5e7eb;border-radius:16px;background:#fafafa;'>
            <div style='font-size:0.9rem;color:#475569;margin-bottom:0.4rem;'>{card['category']} · {card['subcategory']} · {card['estimated_minutes']} min</div>
            <div style='font-size:1.6rem;font-weight:700;margin-bottom:0.7rem;'>{card['title']}</div>
            <div style='font-size:1.05rem;line-height:1.6;margin-bottom:0.9rem;'><strong>Claim:</strong> {card['claim']}</div>
            <div style='line-height:1.65;margin-bottom:0.9rem;'><strong>Why it matters:</strong> {card['summary']}</div>
            <div><span style='padding:0.25rem 0.55rem;border-radius:999px;background:#ecfeff;color:#155e75;font-size:0.82rem;font-weight:600;'>Evidence: {card['evidence_strength']}</span>
            <span style='padding:0.25rem 0.55rem;border-radius:999px;background:#f8fafc;color:#334155;font-size:0.82rem;font-weight:600;margin-left:0.35rem;'>{card['evidence_type']}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Mechanism", "Sources", "Limitations", "Related topics", "Apply it"])

    with tab1:
        st.write(card["mechanism"])
    with tab2:
        rows = source_rows(card)
        if rows:
            for title, url, src_type in rows:
                if url:
                    st.markdown(f"- [{title}]({url}) — {src_type}".strip())
                else:
                    st.markdown(f"- {title} — {src_type}".strip(" —"))
        else:
            st.info("No source links added yet for this card.")
    with tab3:
        st.markdown("**Main limitations**")
        st.write(card["limitations"] or "Not filled yet.")
        st.markdown("**Skeptical view**")
        st.write(card["skeptical_view"] or "Not filled yet.")
    with tab4:
        topics = [t.strip() for t in str(card["related_topics"]).split(",") if t.strip()]
        if topics:
            for topic in topics:
                st.markdown(f"- {topic}")
        else:
            st.info("No related topics added yet.")
    with tab5:
        st.markdown("**Practical takeaway**")
        st.write(card["practical_takeaway"])
        st.markdown("**Reflection prompt**")
        st.info(card["reflection_prompt"])


def sidebar_stats(library: pd.DataFrame, history: pd.DataFrame) -> None:
    st.sidebar.header("Daily Edge V2")
    st.sidebar.caption("Evidence-based microlearning")
    st.sidebar.metric("Library size", len(library))
    st.sidebar.metric("Unique cards seen", int(history["card_id"].nunique()) if not history.empty else 0)
    st.sidebar.metric("Completed sessions", int(history["completed"].sum()) if not history.empty else 0)
    if not history.empty and history["rating"].notna().any():
        st.sidebar.metric("Average rating", round(float(history["rating"].dropna().mean()), 2))
    st.sidebar.markdown("---")
    st.sidebar.write("This version uses SQLite for quick private prototyping. For durable cloud memory later, move to Supabase or another hosted database.")


def main() -> None:
    init_db()
    library = load_library()
    history = get_history()
    sidebar_stats(library, history)

    st.title("🧠 Daily Edge")
    st.caption("A private microlearning app with layered cards, sources, limitations, and lightweight recommendation memory.")

    tabs = st.tabs(["Today", "Library", "History", "Build the library"])

    with tabs[0]:
        card = select_today_card(library, history)
        today_key = date.today().isoformat()
        existing = history[(history["card_id"] == card["id"]) & (history["shown_at"] == today_key)]

        col1, col2 = st.columns([2.1, 1])
        with col1:
            render_today_card(card)

        default_rating = int(existing.iloc[0]["rating"]) if not existing.empty and pd.notna(existing.iloc[0]["rating"]) else 3
        default_tag = existing.iloc[0]["response_tag"] if not existing.empty and pd.notna(existing.iloc[0]["response_tag"]) else "Useful"
        default_note = existing.iloc[0]["note"] if not existing.empty and pd.notna(existing.iloc[0]["note"]) else ""
        default_completed = bool(existing.iloc[0]["completed"]) if not existing.empty else False

        with col2:
            st.markdown("### Log today's session")
            with st.form("daily_feedback_form"):
                rating = st.slider("How valuable was this?", 1, 5, value=default_rating)
                response_tag = st.selectbox(
                    "How should this influence future suggestions?",
                    ["Useful", "More like this", "Less like this", "Too basic", "Too speculative"],
                    index=["Useful", "More like this", "Less like this", "Too basic", "Too speculative"].index(default_tag),
                )
                note = st.text_area("Your note", value=default_note, placeholder="One sentence on what you learned or where to apply it.")
                completed = st.checkbox("Completed today's session", value=default_completed)
                revisit_days = st.selectbox("Revisit this in", ["No revisit", "3 days", "7 days", "14 days", "30 days"], index=0)
                submitted = st.form_submit_button("Save")

            if submitted:
                revisit_on = None
                if revisit_days != "No revisit":
                    days = int(revisit_days.split()[0])
                    revisit_on = (date.today() + timedelta(days=days)).isoformat()
                upsert_interaction(card["id"], today_key, rating, response_tag, note.strip(), completed, revisit_on)
                st.success("Saved.")
                st.rerun()

            st.markdown("### How V2 chooses")
            st.write("It prefers category variety, lightly rewards topics you rate highly, avoids immediate repetition, and brings back cards you scheduled for review.")

    with tabs[1]:
        st.subheader("Browse the library")
        category_options = ["All"] + sorted(library["category"].unique().tolist())
        col_a, col_b = st.columns([1, 1.6])
        with col_a:
            selected_category = st.selectbox("Category", category_options)
        with col_b:
            search_term = st.text_input("Search", placeholder="Search title, claim, related topics")

        filtered = library.copy()
        if selected_category != "All":
            filtered = filtered[filtered["category"] == selected_category]
        if search_term:
            mask = (
                filtered["title"].str.contains(search_term, case=False, na=False)
                | filtered["claim"].str.contains(search_term, case=False, na=False)
                | filtered["related_topics"].str.contains(search_term, case=False, na=False)
            )
            filtered = filtered[mask]

        st.dataframe(
            filtered[["id", "title", "category", "subcategory", "evidence_strength", "evidence_type"]],
            use_container_width=True,
            hide_index=True,
        )

        if not filtered.empty:
            selected_id = st.selectbox("Preview a card", filtered["id"].tolist())
            preview_card = library[library["id"] == selected_id].iloc[0]
            st.markdown("---")
            render_today_card(preview_card)

    with tabs[2]:
        st.subheader("Your history")
        if history.empty:
            st.info("No sessions saved yet.")
        else:
            merged = history.merge(library[["id", "title", "category"]], left_on="card_id", right_on="id", how="left")
            view = merged[["shown_at", "card_id", "title", "category", "rating", "response_tag", "completed", "revisit_on", "note"]]
            st.dataframe(view, use_container_width=True, hide_index=True)
            st.download_button("Download history CSV", view.to_csv(index=False).encode("utf-8"), "daily_edge_history.csv", "text/csv")

    with tabs[3]:
        st.subheader("How to develop the library")
        st.markdown(
            """
            Build **15–20 excellent cards first**, not 200 average ones.

            Each good card should include:
            - one precise claim
            - a short explanation of why it matters
            - a mechanism or causal logic section
            - an evidence-strength label
            - one or two real sources
            - at least one limitation
            - a skeptical view
            - one practical takeaway
            - one reflection prompt
            - a few related topics

            A useful rule is to keep a card in the main rotation only if it scores well on:
            - clarity
            - usefulness
            - source quality
            - honesty about limitations
            - practical relevance
            """
        )
        st.code(
            """Recommended CSV columns:
id,title,category,subcategory,claim,summary,mechanism,evidence_strength,evidence_type,limitations,skeptical_view,practical_takeaway,reflection_prompt,related_topics,estimated_minutes,difficulty,source_1_title,source_1_url,source_1_type,source_2_title,source_2_url,source_2_type""",
            language="text",
        )


if __name__ == "__main__":
    main()
