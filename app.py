import base64
import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


DB_PATH = Path(__file__).resolve().parent / "hot100-80s.db"
BACKGROUND_PATH = (
    Path(__file__).resolve().parent / "assets" / "hot100_80s_montage.png"
)

LIGHT_THEME = {
    "background": "#f7f7f2",
    "background_overlay": "rgba(247, 247, 242, 0.88)",
    "panel": "#ffffff",
    "panel_alpha": "rgba(255, 255, 255, 0.86)",
    "text": "#171717",
    "muted": "#55584d",
    "border": "#d9d8cf",
    "accent": "#c7472e",
    "chart_range": ["#f1c453", "#287c79", "#c7472e"],
}

DARK_THEME = {
    "background": "#141415",
    "background_overlay": "rgba(20, 20, 21, 0.78)",
    "panel": "#202124",
    "panel_alpha": "rgba(32, 33, 36, 0.88)",
    "text": "#f4f1e8",
    "muted": "#b7b3a6",
    "border": "#3b3b3d",
    "accent": "#f0714f",
    "chart_range": ["#f7c95c", "#52aaa3", "#f0714f"],
}


st.set_page_config(
    page_title="Welcome to the 80s Hot 100 Charts",
    page_icon=":musical_note:",
    layout="wide",
)


@st.cache_data
def run_query(query, params=()):
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "hot100-80s.db was not found. Run `python load_hot100.py` first."
        )

    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


def active_theme():
    return DARK_THEME if st.session_state.get("dark_mode") else LIGHT_THEME


@st.cache_data
def background_data_uri():
    if not BACKGROUND_PATH.exists():
        return ""

    encoded = base64.b64encode(BACKGROUND_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def apply_theme():
    theme = active_theme()
    background_image = background_data_uri()
    st.markdown(
        f"""
        <style>
            :root {{
                --hot100-bg: {theme["background"]};
                --hot100-bg-overlay: {theme["background_overlay"]};
                --hot100-panel: {theme["panel"]};
                --hot100-panel-alpha: {theme["panel_alpha"]};
                --hot100-text: {theme["text"]};
                --hot100-muted: {theme["muted"]};
                --hot100-border: {theme["border"]};
                --hot100-accent: {theme["accent"]};
            }}

            .stApp {{
                background-color: var(--hot100-bg);
                background-image:
                    linear-gradient(
                        var(--hot100-bg-overlay),
                        var(--hot100-bg-overlay)
                    ),
                    url("{background_image}");
                background-attachment: fixed;
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
                color: var(--hot100-text);
            }}

            [data-testid="stSidebar"],
            [data-testid="stHeader"] {{
                background-color: var(--hot100-panel-alpha);
                backdrop-filter: blur(8px);
            }}

            h1, h2, h3, h4, h5, h6,
            p, label, span, div {{
                color: var(--hot100-text);
            }}

            [data-testid="stCaptionContainer"],
            [data-testid="stMarkdownContainer"] small {{
                color: var(--hot100-muted);
            }}

            .stButton > button {{
                border-color: var(--hot100-border);
                color: var(--hot100-accent);
                background: var(--hot100-panel-alpha);
            }}

            .stButton > button:hover {{
                border-color: var(--hot100-accent);
                color: var(--hot100-accent);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def song_score_sql(where_clause="1 = 1"):
    return f"""
        SELECT
            title,
            performer,
            COUNT(*) AS weeks_on_chart,
            MIN(current_week) AS peak_position,
            SUM(101 - current_week) AS success_score
        FROM hot100
        WHERE {where_clause}
        GROUP BY title, performer
    """


def get_years():
    return run_query("SELECT DISTINCT year FROM hot100 ORDER BY year DESC")[
        "year"
    ].tolist()


def get_all_songs():
    return run_query(
        """
        SELECT
            title,
            performer,
            MIN(current_week) AS peak_position,
            COUNT(*) AS weeks_on_chart
        FROM hot100
        GROUP BY title, performer
        ORDER BY title, performer
        """
    )


def set_song(title, performer):
    st.session_state.selected_song = {"title": title, "performer": performer}
    st.session_state.page = "Song Page"


def main_page():
    theme = active_theme()
    st.title("Welcome to the 80s Hot 100 Charts")
    st.caption(
        "Success score combines chart position with chart longevity: "
        "each week contributes 101 minus the song's Hot 100 position."
    )

    top_songs = run_query(
        f"""
        SELECT
            title || ' by ' || performer AS song,
            title,
            performer,
            weeks_on_chart,
            peak_position,
            success_score
        FROM ({song_score_sql()})
        ORDER BY success_score DESC, peak_position ASC, weeks_on_chart DESC
        LIMIT 10
        """
    )

    chart = (
        alt.Chart(top_songs)
        .mark_bar()
        .encode(
            x=alt.X("success_score:Q", title="Success Score"),
            y=alt.Y("song:N", title="", sort="-x"),
            color=alt.Color("peak_position:Q", title="Peak Position"),
            tooltip=[
                alt.Tooltip("title:N", title="Song"),
                alt.Tooltip("performer:N", title="Artist"),
                alt.Tooltip("success_score:Q", title="Success Score"),
                alt.Tooltip("peak_position:Q", title="Peak"),
                alt.Tooltip("weeks_on_chart:Q", title="Weeks"),
            ],
        )
        .properties(height=440, width="container")
        .configure_view(stroke=theme["border"])
        .configure_axis(
            labelColor=theme["text"],
            titleColor=theme["muted"],
            gridColor=theme["border"],
        )
        .configure_legend(labelColor=theme["text"], titleColor=theme["muted"])
        .configure_range(ramp=theme["chart_range"])
    )
    st.altair_chart(chart)

    st.dataframe(
        top_songs[
            [
                "title",
                "performer",
                "success_score",
                "peak_position",
                "weeks_on_chart",
            ]
        ],
        column_config={
            "title": "Song",
            "performer": "Artist",
            "success_score": st.column_config.NumberColumn(
                "Success Score", format="%d"
            ),
            "peak_position": "Peak",
            "weeks_on_chart": "Weeks",
        },
        hide_index=True,
        width="stretch",
    )


def year_page():
    st.title("Year Chart")
    years = get_years()
    selected_year = st.selectbox("Select a year", years, index=0)

    top_50 = run_query(
        f"""
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY success_score DESC, peak_position ASC, weeks_on_chart DESC
            ) AS rank,
            title,
            performer,
            success_score,
            peak_position,
            weeks_on_chart
        FROM ({song_score_sql("year = ?")})
        ORDER BY rank
        LIMIT 50
        """,
        (selected_year,),
    )

    st.subheader(f"Top 50 Songs of {selected_year}")

    header = st.columns([0.6, 3, 2.4, 1.2, 1, 1])
    header[0].markdown("**#**")
    header[1].markdown("**Song**")
    header[2].markdown("**Artist**")
    header[3].markdown("**Score**")
    header[4].markdown("**Peak**")
    header[5].markdown("**Weeks**")

    for row in top_50.itertuples(index=False):
        cols = st.columns([0.6, 3, 2.4, 1.2, 1, 1])
        cols[0].write(int(row.rank))
        if cols[1].button(
            row.title,
            key=f"song-{selected_year}-{row.rank}",
            width="stretch",
        ):
            set_song(row.title, row.performer)
            st.rerun()
        cols[2].write(row.performer)
        cols[3].write(int(row.success_score))
        cols[4].write(int(row.peak_position))
        cols[5].write(int(row.weeks_on_chart))


def song_page():
    theme = active_theme()
    st.title("Song History")

    songs = get_all_songs()
    labels = [
        f"{row.title} - {row.performer}" for row in songs.itertuples(index=False)
    ]

    selected_song = st.session_state.get("selected_song")
    default_index = 0
    if selected_song:
        selected_label = (
            f"{selected_song['title']} - {selected_song['performer']}"
        )
        if selected_label in labels:
            default_index = labels.index(selected_label)

    selected_label = st.selectbox("Select a song", labels, index=default_index)
    selected_row = songs.iloc[labels.index(selected_label)]

    history = run_query(
        """
        SELECT
            chart_week,
            current_week,
            peak_pos,
            wks_on_chart
        FROM hot100
        WHERE title = ? AND performer = ?
        ORDER BY chart_week
        """,
        (selected_row["title"], selected_row["performer"]),
    )

    st.subheader(f"{selected_row['title']} - {selected_row['performer']}")

    timeline = history.assign(chart_week=pd.to_datetime(history["chart_week"]))
    chart = (
        alt.Chart(timeline)
        .mark_line(point=True)
        .encode(
            x=alt.X("chart_week:T", title="Chart Week"),
            y=alt.Y(
                "current_week:Q",
                title="Hot 100 Position",
                scale=alt.Scale(reverse=True, domain=[100, 1]),
            ),
            tooltip=[
                alt.Tooltip("chart_week:T", title="Chart Week"),
                alt.Tooltip("current_week:Q", title="Position"),
                alt.Tooltip("peak_pos:Q", title="Peak"),
                alt.Tooltip("wks_on_chart:Q", title="Weeks"),
            ],
        )
        .properties(height=440, width="container")
        .configure_view(stroke=theme["border"])
        .configure_axis(
            labelColor=theme["text"],
            titleColor=theme["muted"],
            gridColor=theme["border"],
        )
    )
    st.altair_chart(chart)

    st.dataframe(
        history,
        column_config={
            "chart_week": "Chart Week",
            "current_week": "Hot 100 Position",
            "peak_pos": "Peak",
            "wks_on_chart": "Weeks on Chart",
        },
        hide_index=True,
        width="stretch",
    )


def navigation():
    if "page" not in st.session_state:
        st.session_state.page = "Main Page"
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    st.sidebar.toggle("Dark mode", key="dark_mode")
    apply_theme()

    page = st.sidebar.radio(
        "Navigation",
        ["Main Page", "Year Page", "Song Page"],
        index=["Main Page", "Year Page", "Song Page"].index(
            st.session_state.page
        ),
    )
    st.session_state.page = page
    return page


page = navigation()

if page == "Main Page":
    main_page()
elif page == "Year Page":
    year_page()
else:
    song_page()
