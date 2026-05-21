import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

# ── Page config ──
st.set_page_config(
    page_title="Vouch Competitive Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Data loading ──
DATA_DIR = Path(__file__).parent / "data"


@st.cache_data(ttl=300)
def load_jsonl(filename: str) -> list[dict]:
    """Load a JSONL file from the data directory."""
    path = DATA_DIR / filename
    if not path.exists():
        st.error(f"Data file not found: {path}")
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def format_label(s: str) -> str:
    """Convert snake_case to Title Case with insurance abbreviations."""
    replacements = {
        "D And O": "D&O",
        "E And O": "E&O",
        "Gl": "GL",
        "Wc": "WC",
        "Bop": "BOP",
        "Epli": "EPLI",
        "Ip": "IP",
        "Mga": "MGA",
        "Hybrid Mga Broker": "Hybrid MGA/Broker",
    }
    label = s.replace("_", " ").title()
    for old, new in replacements.items():
        label = label.replace(old, new)
    return label


def confidence_color(level: str) -> str:
    colors = {
        "high": "#166534",
        "medium-high": "#854d0e",
        "medium": "#854d0e",
        "low": "#991b1b",
    }
    return colors.get(level, "#555")


def confidence_bg(level: str) -> str:
    bgs = {
        "high": "#dcfce7",
        "medium-high": "#fef9c3",
        "medium": "#fef9c3",
        "low": "#fee2e2",
    }
    return bgs.get(level, "#f0f0f0")


def activity_type_color(t: str) -> tuple[str, str]:
    """Return (bg, text) colors for activity types."""
    colors = {
        "partnership": ("#dbeafe", "#1e40af"),
        "leadership": ("#fae8ff", "#86198f"),
        "product_launch": ("#dcfce7", "#166534"),
        "acquisition": ("#fed7aa", "#9a3412"),
        "funding": ("#fef3c7", "#92400e"),
        "messaging_change": ("#e0e7ff", "#3730a3"),
        "pricing": ("#fce7f3", "#9d174d"),
        "content_play": ("#ccfbf1", "#115e59"),
        "other": ("#f0f0f0", "#555"),
    }
    return colors.get(t, ("#f0f0f0", "#555"))


# ── Load data ──
competitors = load_jsonl("competitors.jsonl")
activity_log = load_jsonl("competitor-activity-log.jsonl")
competitor_map = {c["id"]: c["name"] for c in competitors}

# ── Vouch's own verticals and coverage lines (for overlap color coding) ──
VOUCH_VERTICALS = {"tech", "professional_services", "health_life_sciences", "financial_services"}
VOUCH_SUB_VERTICALS = {
    "ai", "saas", "fintech", "ecommerce", "hardware", "crypto",
    "accounting", "architecture_engineering_construction", "it_consulting",
    "management_consulting", "marketing_creative_agencies",
    "healthtech", "biotools_testing",
    "hedge_funds", "asset_management", "venture_capital",
}
VOUCH_COVERAGE = {"d_and_o", "e_and_o", "cyber", "crime", "property", "gl", "media", "wc", "epli"}

# ── Custom CSS ──
st.markdown(
    """
<style>
    /* Clean up padding */
    .block-container { padding-top: 1rem; }

    /* Tag styling */
    .tag {
        display: inline-block;
        padding: 3px 10px;
        background: #f0f0f0;
        border-radius: 4px;
        font-size: 12px;
        color: #555;
        margin: 2px;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }

    /* Win/lose boxes */
    .win-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 16px;
        color: #15803d;
        font-size: 14px;
        line-height: 1.6;
    }
    .lose-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 16px;
        color: #b91c1c;
        font-size: 14px;
        line-height: 1.6;
    }
    .win-label, .lose-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Objection card */
    .objection-card {
        background: #f8f8f8;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 1.6;
        color: #333;
    }

    /* Overlap tags */
    .tag-overlap {
        display: inline-block;
        padding: 3px 10px;
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        border-radius: 4px;
        font-size: 12px;
        color: #166534;
        margin: 2px;
    }
    .tag-theirs-only {
        display: inline-block;
        padding: 3px 10px;
        background: #fee2e2;
        border: 1px solid #fecaca;
        border-radius: 4px;
        font-size: 12px;
        color: #991b1b;
        margin: 2px;
    }
    .tag-ours-only {
        display: inline-block;
        padding: 3px 10px;
        background: #f0f0f0;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        font-size: 12px;
        color: #888;
        margin: 2px;
    }

    /* Gap item */
    .gap-item {
        font-size: 13px;
        color: #666;
        padding: 4px 0;
    }
    .gap-marker {
        display: inline-block;
        width: 20px;
        height: 20px;
        line-height: 20px;
        text-align: center;
        background: #fef3c7;
        color: #92400e;
        border-radius: 50%;
        font-size: 10px;
        font-weight: 700;
        margin-right: 8px;
    }

    /* Timeline */
    .timeline-card {
        border-left: 3px solid #e5e5e5;
        padding: 12px 16px;
        margin-bottom: 12px;
        margin-left: 8px;
    }
    .timeline-date {
        font-size: 12px;
        color: #888;
    }
    .timeline-summary {
        font-size: 14px;
        color: #333;
        margin: 4px 0;
    }
    .timeline-impact {
        font-size: 13px;
        color: #666;
        font-style: italic;
    }

    /* Notes box */
    .notes-box {
        background: #f8f8f8;
        border-radius: 8px;
        padding: 14px;
        font-size: 14px;
        line-height: 1.6;
        color: #444;
    }

    /* Overview card */
    .overview-card {
        background: #f8f8f8;
        border-radius: 8px;
        padding: 12px;
    }
    .overview-label {
        font-size: 11px;
        font-weight: 500;
        color: #888;
        margin-bottom: 2px;
    }
    .overview-value {
        font-size: 13px;
        color: #333;
    }

    /* Section headers */
    .section-header {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #888;
        margin-bottom: 8px;
        margin-top: 16px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ──
st.title("Competitive Intelligence")
st.caption("Vouch competitor battlecards, activity tracking, and analysis")

# ── Sidebar filters ──
st.sidebar.header("Filters")

# Vertical filter
all_verticals = sorted(
    set(v for c in competitors for v in c.get("verticals", []))
)
selected_verticals = st.sidebar.multiselect(
    "Verticals",
    options=all_verticals,
    format_func=format_label,
)

# Category filter
all_categories = sorted(set(c.get("category", "") for c in competitors))
selected_categories = st.sidebar.multiselect(
    "Category",
    options=all_categories,
    format_func=format_label,
)

# Search
search_query = st.sidebar.text_input("Search", placeholder="Search competitors...")

# ── Tabs ──
tab_battlecards, tab_activity, tab_matrix, tab_ask = st.tabs(
    ["Battlecards", "Activity Log", "Coverage Matrix", "Ask Claude"]
)

# ── Filter competitors ──
filtered = competitors
if selected_verticals:
    filtered = [
        c
        for c in filtered
        if any(v in c.get("verticals", []) for v in selected_verticals)
    ]
if selected_categories:
    filtered = [c for c in filtered if c.get("category") in selected_categories]
if search_query:
    q = search_query.lower()
    filtered = [c for c in filtered if q in json.dumps(c).lower()]


# ══════════════════════════════════════════════
# TAB 1: BATTLECARDS
# ══════════════════════════════════════════════
with tab_battlecards:
    if not filtered:
        st.info("No competitors match the current filters.")
    for comp in filtered:
        conf = comp.get("confidence", "medium")
        conf_bg = confidence_bg(conf)
        conf_color = confidence_color(conf)

        with st.expander(
            f"**{comp['name']}** — {format_label(comp.get('business_model', ''))} · Confidence: {conf}",
            expanded=False,
        ):
            # Positioning
            st.markdown(f"*{comp.get('primary_positioning', '')}*")

            # Overview grid
            st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f'<div class="overview-card"><div class="overview-label">Founded</div><div class="overview-value">{comp.get("founded", "Unknown")}</div></div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="overview-card"><div class="overview-label">Employees</div><div class="overview-value">{comp.get("employee_count", "Unknown")}</div></div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f'<div class="overview-card"><div class="overview-label">Funding</div><div class="overview-value">{comp.get("funding_scale", "Unknown")}</div></div>',
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(
                    f'<div class="overview-card"><div class="overview-label">Distribution</div><div class="overview-value">{format_label(comp.get("distribution_model", ""))}</div></div>',
                    unsafe_allow_html=True,
                )

            # Verticals (color coded: green = overlap, red = theirs only, gray = ours only)
            st.markdown(
                '<div class="section-header">Verticals</div>',
                unsafe_allow_html=True,
            )
            comp_subs = set(comp.get("sub_verticals", []))
            vert_tags = ""
            for v in comp.get("sub_verticals", []):
                css = "tag-overlap" if v in VOUCH_SUB_VERTICALS else "tag-theirs-only"
                vert_tags += f'<span class="{css}">{format_label(v)}</span> '
            for v in sorted(VOUCH_SUB_VERTICALS - comp_subs):
                vert_tags += f'<span class="tag-ours-only">{format_label(v)}</span> '
            st.markdown(vert_tags, unsafe_allow_html=True)

            # Coverage lines (color coded: green = overlap, red = theirs only, gray = ours only)
            st.markdown(
                '<div class="section-header">Coverage Lines</div>',
                unsafe_allow_html=True,
            )
            comp_lines = set(comp.get("coverage_lines", []))
            line_tags = ""
            for l in comp.get("coverage_lines", []):
                css = "tag-overlap" if l in VOUCH_COVERAGE else "tag-theirs-only"
                line_tags += f'<span class="{css}">{format_label(l)}</span> '
            for l in sorted(VOUCH_COVERAGE - comp_lines):
                line_tags += f'<span class="tag-ours-only">{format_label(l)}</span> '
            st.markdown(line_tags, unsafe_allow_html=True)

            # Key differentiators
            st.markdown('<div class="section-header">Key Differentiators</div>', unsafe_allow_html=True)
            for d in comp.get("key_differentiators", []):
                st.markdown(f"- {d}")

            # Strengths vs Weaknesses
            st.markdown(
                '<div class="section-header">Strengths & Weaknesses vs. Vouch</div>',
                unsafe_allow_html=True,
            )
            col_s, col_w = st.columns(2)
            with col_s:
                st.markdown("**Their Strengths**")
                for s in comp.get("strengths_vs_vouch", []):
                    st.markdown(f"- {s}")
            with col_w:
                st.markdown("**Our Advantages**")
                for w in comp.get("weaknesses_vs_vouch", []):
                    st.markdown(f"- {w}")

            # Where we win / lose
            st.markdown(
                '<div class="section-header">Where We Win / Where We Lose</div>',
                unsafe_allow_html=True,
            )
            col_win, col_lose = st.columns(2)
            with col_win:
                st.markdown(
                    f'<div class="win-box"><div class="win-label">Where Vouch Wins</div>{comp.get("where_we_win", "")}</div>',
                    unsafe_allow_html=True,
                )
            with col_lose:
                st.markdown(
                    f'<div class="lose-box"><div class="lose-label">Where We Lose</div>{comp.get("where_we_lose", "")}</div>',
                    unsafe_allow_html=True,
                )

            # Objection handling
            st.markdown(
                '<div class="section-header">Objection Handling</div>',
                unsafe_allow_html=True,
            )
            for obj in comp.get("objection_handling", []):
                st.markdown(
                    f'<div class="objection-card">{obj}</div>',
                    unsafe_allow_html=True,
                )

            # Pricing
            if comp.get("pricing_model"):
                st.markdown(
                    '<div class="section-header">Pricing Intel</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="notes-box">{comp["pricing_model"]}</div>',
                    unsafe_allow_html=True,
                )

            # Intel gaps
            st.markdown(
                '<div class="section-header">Intel Gaps</div>',
                unsafe_allow_html=True,
            )
            for g in comp.get("gaps", []):
                st.markdown(
                    f'<div class="gap-item"><span class="gap-marker">?</span>{g}</div>',
                    unsafe_allow_html=True,
                )

            # Notes
            if comp.get("notes"):
                st.markdown(
                    '<div class="section-header">Notes</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="notes-box">{comp["notes"]}</div>',
                    unsafe_allow_html=True,
                )

            # Last updated
            st.caption(f"Last updated: {comp.get('last_updated', 'Unknown')}")


# ══════════════════════════════════════════════
# TAB 2: ACTIVITY LOG
# ══════════════════════════════════════════════
with tab_activity:
    # Activity type filter
    all_types = sorted(set(a.get("type", "") for a in activity_log))
    selected_types = st.multiselect(
        "Filter by type",
        options=all_types,
        format_func=format_label,
        key="activity_type_filter",
    )

    # Competitor filter for activity
    activity_competitor_filter = st.multiselect(
        "Filter by competitor",
        options=list(competitor_map.keys()),
        format_func=lambda x: competitor_map.get(x, x),
        key="activity_competitor_filter",
    )

    # Filter and sort
    filtered_activity = sorted(activity_log, key=lambda a: a.get("date", ""), reverse=True)
    if selected_types:
        filtered_activity = [a for a in filtered_activity if a.get("type") in selected_types]
    if activity_competitor_filter:
        filtered_activity = [
            a for a in filtered_activity if a.get("competitor_id") in activity_competitor_filter
        ]

    if not filtered_activity:
        st.info("No activity entries match the current filters.")
    for item in filtered_activity:
        bg, fg = activity_type_color(item.get("type", "other"))
        comp_name = competitor_map.get(item.get("competitor_id", ""), item.get("competitor_id", ""))
        date_str = item.get("date", "")
        try:
            date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %Y")
        except (ValueError, TypeError):
            date_formatted = date_str

        st.markdown(
            f"""<div class="timeline-card">
                <div class="timeline-date">{date_formatted}</div>
                <div>
                    <span class="badge" style="background:{bg};color:{fg};">{format_label(item.get("type", ""))}</span>
                    <strong>{comp_name}</strong>
                </div>
                <div class="timeline-summary">{item.get("summary", "")}</div>
                {"<div class='timeline-impact'>Impact: " + item.get("impact_on_vouch", "") + "</div>" if item.get("impact_on_vouch") else ""}
            </div>""",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════
# TAB 3: COVERAGE MATRIX
# ══════════════════════════════════════════════
with tab_matrix:
    st.markdown("### Coverage Line Comparison")
    st.caption("Which competitors cover which lines — at a glance.")

    all_lines = sorted(
        set(line for c in competitors for line in c.get("coverage_lines", []))
    )
    matrix_data = []
    for c in competitors:
        row = {"Competitor": c["name"]}
        for line in all_lines:
            row[format_label(line)] = "✓" if line in c.get("coverage_lines", []) else ""
        matrix_data.append(row)

    st.dataframe(
        matrix_data,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Vertical Overlap")
    st.caption("Which competitors serve which verticals.")

    all_verts = sorted(
        set(v for c in competitors for v in c.get("verticals", []))
    )
    vert_data = []
    for c in competitors:
        row = {"Competitor": c["name"]}
        for v in all_verts:
            row[format_label(v)] = "✓" if v in c.get("verticals", []) else ""
        vert_data.append(row)

    st.dataframe(
        vert_data,
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════
# TAB 4: ASK CLAUDE
# ══════════════════════════════════════════════
with tab_ask:
    st.markdown("### Ask Claude")
    st.caption(
        "Get deeper competitive analysis from the data. Requires an `ANTHROPIC_API_KEY` in Streamlit secrets."
    )

    # Suggestions
    suggestions = [
        "How do we beat Embroker in the AI vertical?",
        "Compare all competitors' positioning side by side",
        "What are our biggest intel gaps?",
        "Draft a competitive talk track for D&O",
        "How does Hiscox's acquisition of Vouch entities change the game?",
    ]

    cols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        if cols[i].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state["ask_input"] = sug

    question = st.text_input(
        "Your question",
        value=st.session_state.get("ask_input", ""),
        placeholder="e.g. How do we beat Embroker in the AI vertical?",
        key="ask_question_input",
    )

    if st.button("Ask", type="primary"):
        api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
        if not api_key:
            st.error(
                "No API key found. Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` "
                "or set it as an environment variable."
            )
        elif not question.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("Analyzing competitive data..."):
                try:
                    import anthropic

                    client = anthropic.Anthropic(api_key=api_key)
                    context = json.dumps(competitors, indent=2)
                    activity_context = json.dumps(activity_log, indent=2)

                    message = client.messages.create(
                        model="claude-sonnet-4-5-20250514",
                        max_tokens=2048,
                        messages=[
                            {
                                "role": "user",
                                "content": (
                                    "You are a competitive intelligence analyst for Vouch Insurance. "
                                    "Answer this question using ONLY the competitor data provided. "
                                    "Be specific, actionable, and concise. Format for easy scanning.\n\n"
                                    f"COMPETITOR PROFILES:\n{context}\n\n"
                                    f"ACTIVITY LOG:\n{activity_context}\n\n"
                                    f"Question: {question}"
                                ),
                            }
                        ],
                    )
                    st.markdown(message.content[0].text)
                except ImportError:
                    st.error(
                        "The `anthropic` package is not installed. "
                        "Add it to requirements.txt and redeploy."
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
