# 100112 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100112.py   (or: marimo edit ...)

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
IDENTIFIER = """100112"""
TITLE = """Geschwindigkeitsmonitoring: Kennzahlen pro Mess-Standort"""
DESCRIPTION = """<p>In diesem Datensatz werden zu jeder Messung (ein Messgerät an einem Standort) die Kennzahlen V50, V85, Anzahl Fahrzeuge und Übertretungsquote pro Richtung angegeben. Die einzelnen Fahrten finden Sie im Datensatz Einzelmessungen (<a href='https://data.bs.ch/explore/dataset/100097//' target='_blank'>https://data.bs.ch/explore/dataset/100097/</a>)</p><p class='MsoNormal' style='margin-bottom: 12pt; line-height: normal; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;'><span style='font-size: 10.5pt; font-family: Arial, sans-serif;'>Bei den dargestellten
Daten handelt es sich ausschliesslich um statistische Erhebungen. Diese stehen
nicht in einem Zusammenhang mit Ordnungsbussen oder einer strafrechtlichen
Verfolgung. Die statistischen Geschwindigkeitsmessungen dienen der
Kantonspolizei Basel-Stadt zur Überprüfung der Geschwindigkeit sowie der
Verkehrssicherheit (z.B. Sicherheit an Fussgängerstreifen) an der betreffenden
Örtlichkeit. Die Ergebnisse dienen zur Entscheidung, an welchen Örtlichkeiten
Handlungsbedarf in Form von Geschwindigkeitskontrollen besteht. Jedes
Statistikgerät besitzt eine einzige Punktgeometrie und ist meist mit zwei
Richtungen versehen (Richtung 1 und 2).<o:p></o:p></span></p><p class='MsoNormal' style='margin-bottom: 12pt; line-height: normal; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;'><span style='font-size: 10.5pt; font-family: Arial, sans-serif;'>Hinweis: Die
Messungen sind nicht zwingend repräsentativ für das ganze Jahr und müssen im
Kontext des Erhebungsdatums betrachtet werden. Darüber hinaus wurden gewisse
Messungen während einer ausserordentlichen Verkehrsführung (z.B.
Umleitungsverkehr infolge von Baustellentätigkeiten etc.) erhoben.
Manipulationen an Geräten können zu fehlerhaften Messungen führen.</span></p><p class='MsoNormal' style='margin-bottom: 12pt; line-height: normal; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;'><font face='Arial, sans-serif'>Eine Übersicht aller Datensätze auf dem kantonalen Datenportal zum Geschwindigkeitsmonitoring sind unter </font><a href='https://data.bs.ch/explore/?refine.tags=Geschwindigkeitsmonitoring' style='background-color: rgb(255, 255, 255); font-family: sans-serif; font-size: 14px; font-weight: 400;' target='_blank'>https://data.bs.ch/explore/?refine.tags=Geschwindigkeitsmonitoring</a><font face='Arial, sans-serif'> aufrufbar.</font></p><p>Die Mess-Standorte werden auch auf dem Geoportal Basel-Stadt publiziert: <a href='https://www.geo.bs.ch/geschwindigkeitsmonitoring' target='_blank'>https://www.geo.bs.ch/geschwindigkeitsmonitoring</a></p>"""
CONTACT = """Fachstelle für OGD Basel-Stadt | opendata@bs.ch"""
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100112)"""

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
- **Dataset_identifier** `100112`
- **Title** `Geschwindigkeitsmonitoring: Kennzahlen pro Mess-Standort`
- **Description** `<p>In diesem Datensatz werden zu jeder Messung (ein Messgerät an einem Standort) die Kennzahlen V50, V85, Anzahl Fahrzeuge und Übertretungsquote pro Richtung angegeben. Die einzelnen Fahrten finden Sie im Datensatz Einzelmessungen (<a href="https://data.bs.ch/explore/dataset/100097//" target="_blank">https://data.bs.ch/explore/dataset/100097/</a>)</p><p class="MsoNormal" style="margin-bottom: 12pt; line-height: normal; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;"><span style="font-size: 10.5pt; font-family: Arial, sans-serif;">Bei den dargestellten
Daten handelt es sich ausschliesslich um statistische Erhebungen. Diese stehen
nicht in einem Zusammenhang mit Ordnungsbussen oder einer strafrechtlichen
Verfolgung. Die statistischen Geschwindigkeitsmessungen dienen der
Kantonspolizei Basel-Stadt zur Überprüfung der Geschwindigkeit sowie der
Verkehrssicherheit (z.B. Sicherheit an Fussgängerstreifen) an der betreffenden
Örtlichkeit. Die Ergebnisse dienen zur Entscheidung, an welchen Örtlichkeiten
Handlungsbedarf in Form von Geschwindigkeitskontrollen besteht. Jedes
Statistikgerät besitzt eine einzige Punktgeometrie und ist meist mit zwei
Richtungen versehen (Richtung 1 und 2).<o:p></o:p></span></p><p class="MsoNormal" style="margin-bottom: 12pt; line-height: normal; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;"><span style="font-size: 10.5pt; font-family: Arial, sans-serif;">Hinweis: Die
Messungen sind nicht zwingend repräsentativ für das ganze Jahr und müssen im
Kontext des Erhebungsdatums betrachtet werden. Darüber hinaus wurden gewisse
Messungen während einer ausserordentlichen Verkehrsführung (z.B.
Umleitungsverkehr infolge von Baustellentätigkeiten etc.) erhoben.
Manipulationen an Geräten können zu fehlerhaften Messungen führen.</span></p><p class="MsoNormal" style="margin-bottom: 12pt; line-height: normal; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;"><font face="Arial, sans-serif">Eine Übersicht aller Datensätze auf dem kantonalen Datenportal zum Geschwindigkeitsmonitoring sind unter </font><a href="https://data.bs.ch/explore/?refine.tags=Geschwindigkeitsmonitoring" style="background-color: rgb(255, 255, 255); font-family: sans-serif; font-size: 14px; font-weight: 400;" target="_blank">https://data.bs.ch/explore/?refine.tags=Geschwindigkeitsmonitoring</a><font face="Arial, sans-serif"> aufrufbar.</font></p><p>Die Mess-Standorte werden auch auf dem Geoportal Basel-Stadt publiziert: <a href="https://www.geo.bs.ch/geschwindigkeitsmonitoring" target="_blank">https://www.geo.bs.ch/geschwindigkeitsmonitoring</a></p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2021-02-02`
- **Modified** `2025-09-16T02:01:24+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceRequired`
- **Temporal_coverage_start_date** `2018-01-01T23:00:00+00:00`
- **Temporal_coverage_end_date** `None`
- **Themes** `['Mobilität und Verkehr']`
- **Keywords** `['Messung', 'Messwert', 'Standort', 'Mess-Stelle', 'Messstelle', 'Geschwindigkeit', 'Verkehr', 'Auto', 'PKW', 'PW', 'LKW', 'LW', 'Radar']`
- **Publisher** `Kantonspolizei`
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
    df = get_dataset('https://data.bs.ch/explore/dataset/100112/download?format=csv&timezone=Europe%2FZurich')
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
