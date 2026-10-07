# 80s Hot 100 Charts

Streamlit application for exploring Billboard Hot 100 chart history from the
1980s. The app loads `hot-100-80s.csv` into SQLite, ranks songs by chart
success, and provides interactive views by decade, year, and song.

## Features

- Main page titled **Welcome to the 80s Hot 100 Charts**.
- Top 10 all-time song chart using a success score based on chart position and
  time on chart.
- Year page with a dropdown that defaults to the highest available year.
- Top 50 songs report for the selected year.
- Clickable song rows that open the selected song on the Song Page.
- Song Page with a chronological Hot 100 position timeline.
- Shared sidebar navigation for Main Page, Year Page, and Song Page.
- Dark mode toggle.
- Shared 80s music montage background across all pages.

## Success Score

Songs are ranked with this score:

```text
sum(101 - current_week_position)
```

A week at number 1 contributes 100 points. A week at number 100 contributes 1
point. This rewards both high chart position and length of time on the chart.

## Project Files

- `app.py` - Streamlit application.
- `load_hot100.py` - Loads the CSV into SQLite.
- `hot-100-80s.csv` - Source chart data.
- `hot100-80s.db` - SQLite database used by the app.
- `assets/hot100_80s_montage.png` - Background image.
- `generate_80s_background.py` - Regenerates the background image.
- `build_runbook_pdf.py` - Generates the PDF run book.
- `docs/Hot_100_80s_Run_Book.pdf` - Application run book.
- `requirements.txt` - Python dependencies.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Rebuild the database:

```bash
python3 load_hot100.py
```

Run the application:

```bash
streamlit run app.py
```

If `streamlit` is not on your PATH, run:

```bash
python3 -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Regenerate Assets

Regenerate the background image:

```bash
python3 generate_80s_background.py
```

Regenerate the PDF run book:

```bash
python3 build_runbook_pdf.py
```

## Validation

Useful checks:

```bash
python3 load_hot100.py
PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile app.py load_hot100.py generate_80s_background.py build_runbook_pdf.py
```

The loaded database should contain 52,200 chart rows covering 1980 through
1989.
