# 100174 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100174.py   (or: marimo edit ...)

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "marimo>=0.8.0",
#   "polars>=1.5.0",
#   "pandas>=2.0.0",
#   "matplotlib>=3.8.0",
#   "requests>=2.31.0"
# ]
# ///

import os
import io
import requests
import polars as pl
import pandas as pd
import marimo as mo
import matplotlib.pyplot as plt

app = mo.App()

PROVIDER = """Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"""
IDENTIFIER = """100174"""
TITLE = """Smarte Strasse: Luftqualität des Vortages"""
DESCRIPTION = """<p>Der Datensatz zeigt die Maximalwerte (O3) und Mittelwerte (NO2, PM 2.5) des Vortages für die verschiedenen Messwerte als Vergleichswerte für die Echtzeitdaten.<br>Die Echtzeitdaten sind unter folgendem Datensatz zu finden: <a href='https://data.bs.ch/explore/dataset/100093/' target='_blank'>https://data.bs.ch/explore/dataset/100093/</a>  </p><p>Das <a href='https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/lufthygiene' target='_blank'>Lufthygieneamt beider Basel</a> (LHA) testet im Projekt «Smarte Strasse» kosteneffiziente Mikrosensoren auf ihre Genauigkeit und Zuverlässigkeit. Der installierte Sensor vom Typ «Nubo» der Firma Sensirion AG ist in der Lage, die Konzentration verschiedener Schadstoffe in der Luft in Echtzeit zu ermitteln. Gemessen werden die Gehalte der Gase Stickstoffdioxid (NO2) und Ozon (O3), sowie die feinere Fraktion des Feinstaubs «PM2.5». Die Belastungen mit Stickstoffdioxid und Feinstaub werden hauptsächlich durch den motorisierten Verkehr und durch Heizungen verursacht. Ozon wird in der Atmosphäre aus den Vorläuferschadstoffen Stickstoffdioxid und flüchtigen organischen Stoffen (VOC) unter Sonneneinwirkung gebildet. Parallel wurden drei «Nubo»- Sensoren an den permanenten Messstationen des LHA am St. Johanns-Platz, an der Feldbergastrasse und auf der Autobahn A2 in der Hard installiert und gegen die Referenzmessgeräte des LHA verglichen. Diese Werte stehen ebenfalls auf OGD zur Verfügung: <a href='https://data.bs.ch/explore/dataset/100178/' target='_blank'>https://data.bs.ch/explore/dataset/100178/</a><br>Weitere Informationen zur Luftqualität in der Region Basel sind auf <a href='https://www.luftqualitaet.ch/' target='_blank'>www.luftqualitaet.ch</a> verfügbar. Hintergrundinformationen zu Ozon und Feinstaub auf den Webseiten <a href='https://ozon-info.ch/' target='_blank'>www.ozon-info.ch</a> und <a href='https://feinstaub.ch/' target='_blank'>www.feinstaub.ch</a>. Angaben zu den gesundheitlichen Auswirkungen der Luftverschmutzung auf der Webseite <a href='https://www.swisstph.ch/de/projects/ludok/healtheffects/' target='_blank'>https://www.swisstph.ch/de/projects/ludok/healtheffects/</a>.</p><p class='' style='font-family: sans-serif;'><span style='font-weight: bolder;'>Weitere Informationen und Daten rund um das Projekt «Smarte Strasse» finden Sie unter den folgenden Links:</span></p><ul><li>Weitere Informationen zum Projekt «Smarte Strasse»: <a href='https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen' target='_blank'>https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen</a> </li><li>Genaue Standorte aller Sensoren: <a href='https://data.bs.ch/explore/dataset/100114/' target='_blank'>https://data.bs.ch/explore/dataset/100114/</a> </li><li>Weitere Datensätze rund um das Thema «Smarte Strasse»: <a href='https://data.bs.ch/explore/?refine.tags=smarte+strasse' target='_blank'>https://data.bs.ch/explore/?refine.tags=smarte+strasse</a> </li></ul><p><span style='font-weight: bolder;'>Hinweis:<br>Die Luft-Sensoren an der Gundeldingerstrasse wurden am 29.6.23 abmontiert. Seit Anfang/Mitte Juni wurden keine Daten mehr erhoben.</span><br></p>"""
CONTACT = """Fachstelle für OGD Basel-Stadt | opendata@bs.ch"""
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100174)"""

def _ensure_data_dir():
    data_path = os.path.join(os.getcwd(), "..", "data")
    os.makedirs(data_path, exist_ok=True)
    return data_path

def get_dataset(url: str) -> pl.DataFrame:
    _ensure_data_dir()
    csv_path = os.path.join("..", "data", f"{IDENTIFIER}.csv")

    try:
        r = requests.get(
            url,
            params={"format": "csv", "timezone": "Europe%2FZurich"},
            timeout=60,
        )
        r.raise_for_status()
        with open(csv_path, "wb") as f:
            f.write(r.content)
        content = io.BytesIO(r.content)
    except Exception:
        content = csv_path if os.path.exists(csv_path) else None

    if content is None:
        raise RuntimeError("Could not download or locate dataset locally.")

    for sep in (";", ",", "\t"):
        try:
            df = pl.read_csv(
                content,
                separator=sep,
                ignore_errors=True,
                infer_schema_length=2000,
            )
            if df.width > 1:
                return df
        except Exception:
            if hasattr(content, "seek"):
                content.seek(0)

    return pl.read_csv(content, ignore_errors=True, infer_schema_length=2000)

def drop_all_null_columns(df: pl.DataFrame) -> pl.DataFrame:
    if df.height == 0:
        return df
    null_counts_row = df.null_count().row(0)
    cols_keep = [c for c, n in zip(df.columns, null_counts_row) if n < df.height]
    return df.select(cols_keep)

@app.cell
def _():
    mo.md(
        f"""## Open Government Data, provided by **{PROVIDER}**
*Autogenerated Python (marimo) starter for dataset* **`{IDENTIFIER}`**"""
    )
    return

@app.cell
def _():
    mo.md(
        f"""## Dataset
# **{TITLE}**"""
    )
    return

@app.cell
def _():
    mo.md(
        """## Data set links

""" + DATASHOP_MD_LINK
    )
    return

@app.cell
def _():
    mo.md(
        """## Metadata
- **Dataset_identifier** `100174`
- **Title** `Smarte Strasse: Luftqualität des Vortages`
- **Description** `<p>Der Datensatz zeigt die Maximalwerte (O3) und Mittelwerte (NO2, PM 2.5) des Vortages für die verschiedenen Messwerte als Vergleichswerte für die Echtzeitdaten.<br>Die Echtzeitdaten sind unter folgendem Datensatz zu finden: <a href="https://data.bs.ch/explore/dataset/100093/" target="_blank">https://data.bs.ch/explore/dataset/100093/</a>  </p><p>Das <a href="https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/lufthygiene" target="_blank">Lufthygieneamt beider Basel</a> (LHA) testet im Projekt «Smarte Strasse» kosteneffiziente Mikrosensoren auf ihre Genauigkeit und Zuverlässigkeit. Der installierte Sensor vom Typ «Nubo» der Firma Sensirion AG ist in der Lage, die Konzentration verschiedener Schadstoffe in der Luft in Echtzeit zu ermitteln. Gemessen werden die Gehalte der Gase Stickstoffdioxid (NO2) und Ozon (O3), sowie die feinere Fraktion des Feinstaubs «PM2.5». Die Belastungen mit Stickstoffdioxid und Feinstaub werden hauptsächlich durch den motorisierten Verkehr und durch Heizungen verursacht. Ozon wird in der Atmosphäre aus den Vorläuferschadstoffen Stickstoffdioxid und flüchtigen organischen Stoffen (VOC) unter Sonneneinwirkung gebildet. Parallel wurden drei «Nubo»- Sensoren an den permanenten Messstationen des LHA am St. Johanns-Platz, an der Feldbergastrasse und auf der Autobahn A2 in der Hard installiert und gegen die Referenzmessgeräte des LHA verglichen. Diese Werte stehen ebenfalls auf OGD zur Verfügung: <a href="https://data.bs.ch/explore/dataset/100178/" target="_blank">https://data.bs.ch/explore/dataset/100178/</a><br>Weitere Informationen zur Luftqualität in der Region Basel sind auf <a href="https://www.luftqualitaet.ch/" target="_blank">www.luftqualitaet.ch</a> verfügbar. Hintergrundinformationen zu Ozon und Feinstaub auf den Webseiten <a href="https://ozon-info.ch/" target="_blank">www.ozon-info.ch</a> und <a href="https://feinstaub.ch/" target="_blank">www.feinstaub.ch</a>. Angaben zu den gesundheitlichen Auswirkungen der Luftverschmutzung auf der Webseite <a href="https://www.swisstph.ch/de/projects/ludok/healtheffects/" target="_blank">https://www.swisstph.ch/de/projects/ludok/healtheffects/</a>.</p><p class="" style="font-family: sans-serif;"><span style="font-weight: bolder;">Weitere Informationen und Daten rund um das Projekt «Smarte Strasse» finden Sie unter den folgenden Links:</span></p><ul><li>Weitere Informationen zum Projekt «Smarte Strasse»: <a href="https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen" target="_blank">https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen</a> </li><li>Genaue Standorte aller Sensoren: <a href="https://data.bs.ch/explore/dataset/100114/" target="_blank">https://data.bs.ch/explore/dataset/100114/</a> </li><li>Weitere Datensätze rund um das Thema «Smarte Strasse»: <a href="https://data.bs.ch/explore/?refine.tags=smarte+strasse" target="_blank">https://data.bs.ch/explore/?refine.tags=smarte+strasse</a> </li></ul><p><span style="font-weight: bolder;">Hinweis:<br>Die Luft-Sensoren an der Gundeldingerstrasse wurden am 29.6.23 abmontiert. Seit Anfang/Mitte Juni wurden keine Daten mehr erhoben.</span><br></p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2022-02-07`
- **Modified** `2023-06-29T07:45:17+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceRequired`
- **Temporal_coverage_start_date** `2022-01-22T23:00:00+00:00`
- **Temporal_coverage_end_date** `2023-06-26T22:00:00+00:00`
- **Themes** `['Raum und Umwelt']`
- **Keywords** `['Smarte Strasse', 'Luftqualität', 'Feinstaub', 'PM2.5', 'O3', 'NO2']`
- **Publisher** `Lufthygieneamt beider Basel`
- **Reference** `None`
"""
    )
    return

@app.cell
def _():
    mo.md(
        """## Imports and helper functions
Using Polars for speed and memory efficiency."""
    )
    return

@app.cell
def _():
    pass

@app.cell
def _():
    mo.md(
        """## Load data
The dataset is read into a Polars DataFrame."""
    )
    return

@app.cell
def _():
    df = get_dataset('https://data.bs.ch/explore/dataset/100174/download?format=csv&timezone=Europe%2FZurich')
    df = drop_all_null_columns(df)
    mo.md(
        f"Loaded **{df.height:,}** rows × **{df.width:,}** columns after dropping all-null columns."
    )
    df
    return df

@app.cell
def _(df):
    mo.md("## Quick profile")
    duplicates = int(df.is_duplicated().sum()) if df.height else 0
    schema = "\n".join([f"- `{k}`: {v}" for k, v in df.schema.items()])
    try:
        size_mb = f"{(df.estimated_size() or 0)/1_048_576:,.2f} MB"
    except Exception:
        size_mb = "n/a"
    mo.md(
        f"""- Approx. memory size: **{size_mb}**  
- Exact duplicates (row-wise): **{duplicates:,}**  
- Schema:
{schema}"""
    )
    return

@app.cell
def _(df):
    mo.md("### Head (first 5 rows)")
    df.head(5)
    return

@app.cell
def _(df):
    mo.md("### Describe (numeric columns)")
    try:
        desc = df.describe()
        desc
    except Exception:
        mo.md("_No numeric columns to describe._")
    return

@app.cell
def _(df):
    mo.md("### Missingness overview (first 1,000 rows, up to 40 columns)")
    n = min(1000, df.height)
    c = min(40, df.width)
    if n == 0 or c == 0:
        mo.md("_Dataset empty._")
    else:
        sub = df.select(df.columns[:c]).head(n)
        miss = sub.to_pandas().isna().to_numpy()
        plt.figure()
        plt.imshow(miss, aspect="auto", interpolation="nearest")
        plt.title("Missingness matrix (True=missing)")
        plt.xlabel("columns")
        plt.ylabel("rows")
        plt.tight_layout()
        plt.show()
    return

@app.cell
def _(df):
    mo.md("### Histograms (numeric)")
    num_cols = [c for c, t in df.schema.items() if pl.datatypes.is_numeric(t)]
    if not num_cols:
        mo.md("_No numeric data to plot._")
    else:
        for c in num_cols[:24]:
            s = df.select(c).drop_nulls()
            if s.height == 0:
                continue
            plt.figure()
            plt.hist(s.to_series().to_list(), bins=25)
            plt.title(f"Histogram: {c}")
            plt.tight_layout()
            plt.show()
    return

@app.cell
def _():
    mo.md(f"""**Questions about the data?** {CONTACT}""")
    return

if __name__ == "__main__":
    app.run()
