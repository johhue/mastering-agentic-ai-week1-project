from pathlib import Path
from textwrap import wrap


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "docs" / "Hot_100_80s_Run_Book.pdf"

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 54
TOP = 730
BOTTOM = 56


RUNBOOK = [
    (
        "Hot 100 80s Charts Application Run Book",
        [
            "This run book explains the requirements, behavior, operating steps, "
            "and support notes for the Streamlit application built around the "
            "1980s Billboard Hot 100 dataset.",
            "Application entry point: app.py",
            "Database: hot100-80s.db",
            "Source data: hot-100-80s.csv",
        ],
    ),
    (
        "Application Requirements",
        [
            "Load hot-100-80s.csv into a SQLite database named hot100-80s.db.",
            "Provide a Streamlit app with a main page, year page, song page, "
            "and common navigation menu.",
            "Set the Streamlit page title to 'Welcome to the 80s Hot 100 Charts'.",
            "On the main page, show the top 10 most successful songs of all "
            "time using a score based on Hot 100 position and time on chart.",
            "On the year page, allow the user to select a chart year. The "
            "default is the highest year available in the database.",
            "On the year page, show the top 50 songs for the selected year and "
            "allow each song to be opened on the song page.",
            "On the song page, show a chronological Hot 100 position timeline "
            "for the selected song.",
            "Provide a dark mode option and a shared 80s music montage "
            "background across all pages.",
        ],
    ),
    (
        "What The Application Does",
        [
            "The app presents an interactive view of Hot 100 chart activity "
            "from 1980 through 1989. It ranks songs by a success score that "
            "rewards both high chart placement and longevity.",
            "The success score is calculated as the sum of 101 minus the Hot "
            "100 position for every weekly chart appearance. A number 1 week "
            "therefore contributes 100 points, while a number 100 week "
            "contributes 1 point.",
            "The main page visualizes the top 10 songs across the full decade.",
            "The year page filters rankings to a selected year and supports "
            "click-through song navigation.",
            "The song page shows the selected song's week-by-week chart "
            "history with the y-axis reversed so stronger chart positions "
            "appear higher on the chart.",
        ],
    ),
    (
        "Data And Database",
        [
            "The CSV file contains one row per song per chart week with these "
            "fields: chart_week, current_week, title, performer, last_week, "
            "peak_pos, and wks_on_chart.",
            "load_hot100.py rebuilds the hot100 table from the CSV and derives "
            "the year column from chart_week.",
            "The generated database contains indexes for year, song lookup, "
            "and chart week lookup to keep the Streamlit reports responsive.",
            "The current loaded database has 52,200 chart rows covering years "
            "1980 through 1989.",
        ],
    ),
    (
        "How To Run",
        [
            "Install dependencies with: pip install -r requirements.txt",
            "Rebuild the database when the CSV changes with: "
            "python3 load_hot100.py",
            "Start the app with: streamlit run app.py",
            "If streamlit is not on PATH, use: python3 -m streamlit run app.py",
            "Open the local URL printed by Streamlit, commonly "
            "http://localhost:8501 or http://127.0.0.1:8501.",
        ],
    ),
    (
        "Navigation And User Workflow",
        [
            "Use the sidebar navigation menu to move between Main Page, Year "
            "Page, and Song Page.",
            "Use the sidebar Dark mode toggle to switch between light and dark "
            "visual themes. The background image remains visible on all pages "
            "with an overlay that preserves readability.",
            "On Year Page, select a year from the dropdown. The highest "
            "available year is selected by default.",
            "Click a song button in the top 50 report to open that song on the "
            "Song Page.",
            "On Song Page, the dropdown can also be used to select any song "
            "directly.",
        ],
    ),
    (
        "File Inventory",
        [
            "app.py: Streamlit application, navigation, queries, charts, theme, "
            "and background styling.",
            "load_hot100.py: CSV-to-SQLite loading script.",
            "hot-100-80s.csv: Source chart data.",
            "hot100-80s.db: SQLite database used by the app.",
            "assets/hot100_80s_montage.png: Shared page background image.",
            "generate_80s_background.py: Regenerates the background asset.",
            "requirements.txt: Python package dependencies.",
            "docs/Hot_100_80s_Run_Book.pdf: This run book.",
        ],
    ),
    (
        "Validation Checklist",
        [
            "Run python3 load_hot100.py and confirm it reports 52,200 rows.",
            "Run python3 -m py_compile app.py load_hot100.py "
            "generate_80s_background.py to check syntax.",
            "Start Streamlit and confirm the app loads without errors.",
            "Confirm the main page shows a top 10 chart.",
            "Confirm the year dropdown defaults to 1989.",
            "Confirm clicking a year-page song opens that song on the song page.",
            "Confirm the dark mode toggle changes page colors while preserving "
            "legibility.",
        ],
    ),
    (
        "Troubleshooting",
        [
            "If the app reports that hot100-80s.db is missing, run "
            "python3 load_hot100.py from the project directory.",
            "If Streamlit is not found, install requirements or run it as a "
            "Python module with python3 -m streamlit run app.py.",
            "If the background image is missing, run "
            "python3 generate_80s_background.py.",
            "If charts are blank, verify that hot100-80s.db contains the "
            "hot100 table and that the CSV load completed successfully.",
        ],
    ),
]


def pdf_escape(value):
    return (
        value.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def text_width(value, size):
    # Helvetica average width approximation, good enough for wrapping docs.
    return len(value) * size * 0.52


def wrap_text(value, size, max_width):
    words = value.split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if text_width(candidate, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def add_line(pages, state, text, size=10, bold=False, leading=14, gap=0):
    if state["y"] - leading < BOTTOM:
        pages.append([])
        state["y"] = TOP

    font = "F2" if bold else "F1"
    pages[-1].append((LEFT, state["y"], size, font, text))
    state["y"] -= leading + gap


def add_paragraph(pages, state, text, size=10, gap=8, indent=0):
    max_width = PAGE_WIDTH - LEFT * 2 - indent
    for line in wrap_text(text, size, max_width):
        if state["y"] - 14 < BOTTOM:
            pages.append([])
            state["y"] = TOP
        pages[-1].append((LEFT + indent, state["y"], size, "F1", line))
        state["y"] -= 14
    state["y"] -= gap


def build_pages():
    pages = [[]]
    state = {"y": TOP}

    for section_index, (heading, paragraphs) in enumerate(RUNBOOK):
        if section_index == 0:
            add_line(pages, state, heading, size=20, bold=True, leading=26, gap=10)
        else:
            if state["y"] < 170:
                pages.append([])
                state["y"] = TOP
            add_line(pages, state, heading, size=15, bold=True, leading=20, gap=4)

        for paragraph in paragraphs:
            if section_index > 0:
                add_paragraph(pages, state, f"- {paragraph}", size=10, gap=5, indent=8)
            else:
                add_paragraph(pages, state, paragraph, size=10.5, gap=7)

    return pages


def content_stream(page_lines, page_number, total_pages):
    commands = [
        "0.96 0.96 0.93 rg",
        f"0 0 {PAGE_WIDTH} {PAGE_HEIGHT} re f",
        "0.18 0.17 0.18 RG",
        "0.5 w",
        f"{LEFT} 42 {PAGE_WIDTH - LEFT * 2} 0 l S",
    ]

    for x, y, size, font, text in page_lines:
        commands.append(
            f"BT /{font} {size} Tf {x} {y} Td ({pdf_escape(text)}) Tj ET"
        )

    footer = f"Hot 100 80s Run Book | Page {page_number} of {total_pages}"
    commands.append(f"BT /F1 8 Tf {LEFT} 30 Td ({pdf_escape(footer)}) Tj ET")
    return "\n".join(commands).encode("latin-1")


def write_pdf(pages):
    objects = []

    def add_object(body):
        objects.append(body)
        return len(objects)

    catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_object(None)
    font_regular_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    page_ids = []
    for index, page_lines in enumerate(pages, start=1):
        stream = content_stream(page_lines, index, len(pages))
        stream_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R >> >> "
            f"/Contents {stream_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("wb") as pdf:
        pdf.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]

        for obj_id, body in enumerate(objects, start=1):
            offsets.append(pdf.tell())
            pdf.write(f"{obj_id} 0 obj\n".encode("ascii"))
            if isinstance(body, bytes):
                pdf.write(body)
            else:
                pdf.write(body.encode("latin-1"))
            pdf.write(b"\nendobj\n")

        xref_start = pdf.tell()
        pdf.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        pdf.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.write(f"{offset:010d} 00000 n \n".encode("ascii"))

        pdf.write(
            (
                "trailer\n"
                f"<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
                "startxref\n"
                f"{xref_start}\n"
                "%%EOF\n"
            ).encode("ascii")
        )


def main():
    write_pdf(build_pages())
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
