from __future__ import annotations

import json
import sqlite3
from io import StringIO

EMBEDDED_LIBRARY_CSV = r"""id,title,category,subcategory,core_idea,why_it_matters,evidence_strength,practical_application,reflection_prompt,difficulty,novelty_score,estimated_minutes,source_type
DE001,The agreement-before-disagreement effect,Communication & influence,Persuasion,Start by validating part of the other person's view before presenting your disagreement.,It reduces defensiveness and signals you are cooperating rather than attacking which lowers resistance to your argument.,Moderate,"In your next disagreement, open with: 'I think you're right about X; where I see it differently is Y.'",Where in your life do you push your point before making the other person feel understood?,practical,2,15,behavioral science
DE002,Identity-protective reasoning,Mind & behavior,Cognition,People often reject facts that threaten a group or identity they care about.,When a belief is tied to identity changing the belief feels like losing belonging or status.,Strong,Frame difficult ideas in a way that protects dignity and identity before presenting evidence.,Which of your views are hard to question because they are tied to who you think you are?,conceptual,3,15,psychology
DE003,The spotlight effect,Mind & behavior,Social cognition,People usually notice your mistakes far less than you think.,Your mind has privileged access to your own awkward moments so you overestimate how visible they are.,Strong,Before a presentation remind yourself that the audience is focused on the message more than on your tiny imperfections.,What social fear of yours would shrink if you really believed this?,practical,1,10,psychology
DE004,Cognitive reappraisal,Mind & behavior,Emotional regulation,Stress often changes when you change the interpretation not the event.,Reframing a situation can reduce threat perception and improve control.,Strong,"When anxious, ask: 'What else could this mean besides danger?'",What recurring stressor could you reinterpret more productively?,practical,2,12,psychology
DE005,The pause boosts authority,Public speaking,Delivery,A short pause before or after an important sentence increases perceived control and emphasis.,Pauses create cognitive space mark importance and prevent rushed delivery.,Moderate,In your next talk deliberately pause one beat before your main message and one beat after.,Which part of your speaking becomes weaker because you rush it?,practical,1,8,rhetoric
DE006,One message per talk,Public speaking,Structure,Audiences remember a single clear thesis better than several medium-strength points.,Working memory is limited; clarity beats coverage.,Strong,Write the one sentence you want the audience to remember and test every slide against it.,What presentation of yours is trying to say too many things at once?,practical,2,12,communication research
DE007,Stories beat abstractions,Communication & influence,Narrative,People retain concrete stories more easily than abstract explanations.,Stories provide causality characters and emotional hooks that support recall.,Strong,When explaining a concept begin with one specific case before moving to general principles.,Where do you explain too abstractly when an anecdote would work better?,practical,1,10,communication research
DE008,The curse of knowledge,Communication & influence,Explanation,Once you know something it is hard to imagine what it feels like not to know it.,Experts unconsciously skip steps and overload novices.,Strong,Before teaching list three assumptions a beginner does not share with you.,Where do you assume background knowledge that other people do not have?,practical,2,12,cognition
DE009,Implementation intentions,Mind & behavior,Habits,Habits improve when you define exactly when and where the behavior will happen.,If-then plans reduce decision friction and increase follow-through.,Strong,"Turn a vague goal into a script: 'After coffee, I will do 10 minutes of Daily Edge.'",Which of your goals fails because it is still too vague?,practical,1,10,behavior change
DE010,Variable reward loops,Mind & behavior,Habits,Unpredictable rewards can reinforce compulsive checking more than predictable ones.,Variable reinforcement keeps the brain anticipating the next payoff.,Strong,Notice which apps or habits keep you engaged through uncertainty rather than value.,Which parts of your information diet are built to hook you rather than help you?,conceptual,2,12,behavioral science
DE011,Social proof,Communication & influence,Persuasion,People use others' behavior as evidence of what is credible or acceptable.,In uncertainty group behavior reduces the perceived risk of acting.,Strong,When persuading mention who else has already adopted the idea or why a respected group values it.,How often do you ignore the power of examples and references when trying to convince someone?,practical,1,10,behavioral science
DE012,Status threat in debates,Communication & influence,Conflict,People resist more when they feel your point lowers their competence or status.,Threat narrows openness and pushes people into defense mode.,Moderate,Critique the idea not the person and leave them a dignified path to update.,How can you disagree without making the other person feel small?,practical,2,12,social psychology
DE013,Chunking into threes,Public speaking,Structure,Ideas grouped in threes are easier to follow and remember.,Three-part structures create rhythm and reduce cognitive load.,Strong,Convert your next explanation into three points instead of six loosely connected ones.,Where could stronger grouping improve how you speak or write?,practical,1,8,rhetoric
DE014,Contrast creates attention,Public speaking,Narrative,An audience pays more attention when you create tension between two possibilities.,Contrast sharpens meaning: before/after old/new problem/solution.,Strong,Instead of describing a result alone compare it to the failure case or old assumption.,What idea of yours becomes sharper when paired with its opposite?,practical,2,10,rhetoric
DE015,Sleep pressure and adenosine,Body & performance,Sleep,Caffeine masks sleep pressure but it does not replace sleep.,Adenosine builds during wakefulness; caffeine blocks its signal temporarily.,Strong,Avoid using caffeine to ignore chronic sleep debt and consider delaying it after waking.,Do you use stimulants to compensate for poor recovery instead of fixing the cause?,practical,2,15,physiology
DE016,Morning light and circadian rhythm,Body & performance,Recovery,Light exposure soon after waking helps anchor circadian timing.,Morning light influences the biological clock and improves wakefulness signals.,Strong,Try going outside for natural light within the first hour after waking.,Which part of your daily energy could improve through better timing rather than more effort?,practical,1,10,sleep research
DE017,Heat exposure: promise vs proof,Experimental / frontier ideas,Biohacking,Sauna has plausible cardiovascular and recovery benefits but many strong claims outrun the evidence.,Heat stress may influence circulation relaxation and stress pathways but effect size and causality vary by claim.,Moderate,Separate broad evidence-supported benefits from viral claims about extreme detox or miracle outcomes.,Which biohacking claim have you accepted because it sounds mechanistic and impressive?,conceptual,3,15,health research
DE018,Microplastics headlines,Experimental / frontier ideas,Research literacy,A striking headline is not the same as a meaningful intervention.,Presence mechanism and practical reversibility are separate questions.,Moderate,"When you see a claim like 'X removes Y from the body,' ask what was measured, in whom, and whether the result changes decisions.",How often do you confuse a surprising finding with a practical recommendation?,conceptual,3,15,research literacy
DE019,Expected value thinking,Decision-making & thinking,Strategy,A good decision can have a bad outcome; focus on expected value not single results.,Uncertainty means quality should be judged by process and probabilities not only outcomes.,Strong,When evaluating a choice ask whether it was sensible given what you knew at the time.,Where are you unfairly judging yourself by outcome alone?,conceptual,2,12,decision science
DE020,Base rates first,Decision-making & thinking,Judgment,Before focusing on the special details of a case ask what usually happens in similar cases.,Base rates protect you from overvaluing anecdotes and exceptional stories.,Strong,In any forecast start with the reference class before moving to the unique narrative.,Where do you jump to specifics without checking the broader pattern?,practical,2,12,decision science
DE021,Second-order effects,Decision-making & thinking,Systems thinking,The first consequence of an action is rarely the only one that matters.,Systems react over time; short-term wins can create delayed costs.,Strong,"When making a change, ask: 'And then what?' at least twice.",Which current choice of yours looks good in the first order but questionable in the second?,conceptual,2,12,strategy
DE022,Reversible vs irreversible decisions,Decision-making & thinking,Strategy,Move fast on reversible decisions and slow down on hard-to-reverse ones.,This preserves speed without treating all choices as equally risky.,Strong,Classify upcoming decisions into one-way and two-way doors before allocating time to them.,What are you overthinking even though it is easy to reverse?,practical,1,10,management
DE023,Opportunity cost,Decision-making & thinking,Economics,Every yes silently commits you against alternatives.,The real cost of a choice includes what you could have done instead.,Strong,When adding a project name the specific thing it will displace.,Which of your commitments looks different once you state its opportunity cost clearly?,conceptual,2,10,economics
DE024,Loss aversion,Mind & behavior,Biases,Losses often feel larger than equivalent gains.,People become conservative or irrationally protective when something feels like it is being taken away.,Strong,When evaluating a change check whether resistance comes from actual downside or from framing it as a loss.,What are you holding onto mainly because giving it up feels like losing?,conceptual,2,12,behavioral economics
DE025,Anchoring,Mind & behavior,Biases,The first number or frame introduced can disproportionately influence later judgment.,Initial anchors shape reference points even when arbitrary.,Strong,In negotiations or estimates notice how the opening value distorts your sense of reasonable.,Where are you being pulled by the first frame you encountered?,practical,2,10,behavioral economics
DE026,Mirroring and labeling,Communication & influence,Negotiation,Repeating a key phrase and naming the other person's emotion can lower tension and open dialogue.,It signals listening and helps the other person feel understood.,Moderate,"Try: 'It sounds like the timeline is your main concern.' Then let them expand.",Do you rush into solutions before proving you understood the concern?,practical,2,12,negotiation
DE027,The audience remembers less than you think,Public speaking,Delivery,Most audiences retain only a small fraction of a talk so structure matters more than density.,People forget detail quickly unless it is repeated visualized or emotionally tagged.,Strong,Cut low-value detail and reinforce the same central message multiple times in different ways.,What should you remove from your next talk because it helps you more than the audience?,practical,1,10,communication research
DE028,Novelty vs mastery,Body & performance,Learning,New tools feel productive but progress often comes from repeating fundamentals.,Novelty stimulates interest while mastery compounds through repetition.,Strong,Before adding a new protocol ask whether improving the basics would do more.,Where are you substituting newness for depth?,conceptual,1,10,learning science
DE029,Stress inoculation,Body & performance,Performance,Exposure to manageable stress can improve resilience but overload can backfire.,Adaptation depends on dose recovery and context.,Moderate,Use deliberate challenges with recovery rather than constant self-imposed strain.,Are you training resilience or just accumulating fatigue?,conceptual,3,12,performance psychology
DE030,Attention residue,Mind & behavior,Focus,Switching tasks leaves part of your attention stuck on the previous one.,Frequent context switching reduces depth and increases friction.,Moderate,Protect 15–30 minute blocks for one topic instead of jumping between messages and work.,Which recurring interruption leaves your mind split afterward?,practical,2,10,productivity research
DE031,Dopamine detox skepticism,Experimental / frontier ideas,Biohacking,Many dopamine-detox claims oversimplify how motivation and reward systems work.,Reward systems are not reset like a device; behavior change is more about cues habits and attention management.,Moderate,Be suspicious of dramatic reset narratives and focus on reducing triggers and improving routines.,Which self-improvement idea appeals to you because it promises a clean reset?,conceptual,2,12,neuroscience communication
DE032,Voice tempo and credibility,Public speaking,Delivery,Speaking slightly slower than your anxious default often increases clarity and confidence.,A calmer tempo improves intelligibility and projects control.,Moderate,Record yourself delivering the same point at three speeds and compare clarity.,When you get excited or nervous how much does pace undermine your message?,practical,1,8,rhetoric
DE033,The map is not the territory,Decision-making & thinking,Epistemology,Models and explanations are simplifications not reality itself.,Useful abstractions can still hide key variables or distort what matters.,Strong,Use models to orient decisions then test them against direct observation.,Where are you mistaking a neat theory for the full situation?,conceptual,3,12,epistemology
DE034,Mechanistic plausibility is not proof,Experimental / frontier ideas,Research literacy,A compelling biological or psychological mechanism does not guarantee real-world impact.,Many ideas sound plausible but fail in effect size translation or replication.,Strong,When a claim sounds smart ask whether it has robust outcome evidence.,Which claim do you currently believe mainly because the mechanism sounds elegant?,conceptual,3,12,research literacy
DE035,The mere-exposure effect,Communication & influence,Persuasion,Repeated exposure can increase liking and familiarity.,What feels familiar often feels safer and more trustworthy.,Strong,Repeat key messages across time instead of trying to win everything in one conversation.,Where do you expect instant buy-in when repeated exposure would work better?,practical,1,8,social psychology
DE036,Emotional granularity,Mind & behavior,Emotional regulation,Naming emotions with precision can improve regulation.,Specific labels create more workable interpretations than broad labels like bad or stressed.,Moderate,Replace 'I feel bad' with a more precise description such as frustrated ashamed restless or overloaded.,How often do vague emotional labels block useful action?,practical,2,10,psychology
DE037,The illusion of explanatory depth,Mind & behavior,Cognition,People often think they understand something better than they actually do until asked to explain it.,Fluent familiarity can be mistaken for deep understanding.,Strong,Test your understanding by writing a simple explanation from scratch.,What topic do you think you understand but have not yet tried to explain cleanly?,conceptual,2,10,cognitive science
DE038,Progressive overload beyond the gym,Body & performance,Training,Improvement usually requires gradually increasing challenge not repeating the same comfortable level.,Adaptation happens when demand rises enough to require change.,Strong,Apply progressive overload to speaking focus or learning by increasing one difficulty variable at a time.,Where in your life are you practicing without actually increasing the challenge?,practical,1,10,performance science
DE039,Nasal breathing claims,Experimental / frontier ideas,Biohacking,Nasal breathing has real uses but online claims often exceed the evidence.,Some contexts benefit from it but not every performance or health claim is equally supported.,Moderate,Separate low-risk useful practices from exaggerated universal claims.,Which health trend do you treat as all-or-nothing when the truth is more conditional?,conceptual,2,12,respiratory science
DE040,Framing effects,Communication & influence,Persuasion,The same information can produce different reactions depending on how it is framed.,People respond differently to gains losses risks and defaults even when facts are equivalent.,Strong,Before presenting an idea test two framings: what people gain and what they avoid losing.,How could reframing one message change a current conversation?,practical,2,10,behavioral economics
DE041,Self-distancing,Mind & behavior,Reflection,Thinking about your problem as if advising someone else can improve judgment.,Distance reduces emotional flooding and broadens perspective.,Moderate,"Ask: 'If a friend had this problem, what would I tell them?'",Which issue of yours needs less immersion and more perspective?,practical,2,10,psychology
DE042,Desirable difficulty,Learning & growth,Learning,Learning often improves when practice is slightly effortful rather than perfectly smooth.,Some friction enhances encoding and retrieval.,Strong,Use active recall short quizzes or explanation from memory instead of only re-reading.,Where are you choosing comfort over retention?,practical,2,12,learning science
DE043,Retrieval beats rereading,Learning & growth,Learning,Testing yourself usually strengthens memory more than passively reviewing notes.,Retrieval practice reinforces pathways and reveals gaps.,Strong,After reading close the page and write the key ideas from memory before checking.,What are you repeatedly consuming without ever testing yourself on it?,practical,1,10,learning science
DE044,Spacing effect,Learning & growth,Learning,Distributed review over time usually beats cramming.,Spaced encounters strengthen long-term retention more reliably than massed exposure.,Strong,Revisit important ideas after a delay instead of trying to master them in one sitting.,How could your microlearning habit include deliberate review rather than constant novelty?,practical,1,10,learning science
DE045,Incentives shape behavior,Decision-making & thinking,Economics,What people do is heavily influenced by what the system rewards.,Misaligned incentives produce predictable distortions.,Strong,When behavior seems irrational ask what incentives make it reasonable from that person's perspective.,Which frustrating behavior around you makes more sense once incentives are visible?,conceptual,2,12,economics
DE046,Default effects,Decision-making & thinking,Behavior design,What happens automatically often drives choices more than deliberate preference.,Defaults reduce friction and exploit inertia.,Strong,Improve your environment by making the desired action the default.,What could you make automatic so discipline matters less?,practical,1,10,behavior design
DE047,Peak-end rule,Mind & behavior,Memory,People often judge experiences disproportionately by the peak moment and the ending.,Memory compresses long experiences into a few salient points.,Moderate,Design presentations meetings and even social events with a strong ending in mind.,How would your work change if you optimized endings more deliberately?,practical,2,10,behavioral science
DE048,The power of naming the tradeoff,Communication & influence,Leadership,People trust decisions more when the tradeoff is made explicit.,Acknowledging constraints makes reasoning feel honest and adult.,Moderate,Instead of pretending you can optimize everything say what you are choosing and what you are giving up.,Where could clearer tradeoff language make you sound more credible?,practical,2,10,leadership
DE049,Frontier claims need stronger filters,Experimental / frontier ideas,Research literacy,The newer and more sensational the claim the higher your evidence threshold should be.,Novelty attracts attention but early claims are often unstable or overstated.,Strong,Adopt a rule: the more exciting the claim the more conservative your belief until replication appears.,Which area of your curiosity most needs a stricter filter?,conceptual,2,10,research literacy
"""


def resolve_library_path() -> Path | None:
    candidates = [
        LIBRARY_PATH,
        APP_DIR / "content_library.csv",
        Path.cwd() / "data" / "content_library.csv",
        Path.cwd() / "content_library.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    try:
        matches = list(APP_DIR.rglob("content_library.csv"))
        if matches:
            return matches[0]
    except Exception:
        pass

    return None

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
    resolved = resolve_library_path()
    if resolved is not None:
        df = pd.read_csv(resolved)
    else:
        df = pd.read_csv(StringIO(EMBEDDED_LIBRARY_CSV))
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
